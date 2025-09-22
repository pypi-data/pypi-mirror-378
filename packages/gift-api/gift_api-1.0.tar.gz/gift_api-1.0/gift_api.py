# gift_api.py
from __future__ import annotations

import os
import sys
import json
import time
import random
import argparse
import re
from dataclasses import dataclass
from typing import Optional, Iterable, List, Literal, Any, Dict

# -------------------------
# Модели и исключения
# -------------------------

@dataclass(frozen=True, slots=True)
class Gift:
    id: str
    name: str
    link: str
    price_ton: Optional[float] = None
    currency: str = "TON"
    expires_at: Optional[str] = None
    source: Optional[str] = None
    metadata: Optional[dict] = None

@dataclass(frozen=True, slots=True)
class GiftList:
    items: List[Gift]
    total: int
    next_cursor: Optional[str] = None

@dataclass(frozen=True, slots=True)
class GiftClaimResult:
    gift_id: str
    status: str  # "claimed" | "already_claimed" | "expired" | "failed"
    detail: Optional[str] = None

class GiftAPIError(Exception):
    def __init__(self, message: str, *, status: int | None = None, payload: dict | None = None):
        super().__init__(message)
        self.status = status
        self.payload = payload or {}

class GiftAuthError(GiftAPIError):
    pass

class GiftRateLimitError(GiftAPIError):
    pass


# -------------------------
# Вспомогательные функции
# -------------------------

def _env(key: str, default: Optional[str] = None) -> Optional[str]:
    return os.environ.get(key, default)

def _backoff_delays(max_retries: int, factor: float) -> Iterable[float]:
    for i in range(max_retries):
        base = factor * (2 ** i)
        yield base * (0.5 + random.random())

def _safe_float(v) -> Optional[float]:
    try:
        return float(v)
    except Exception:
        return None


# -------------------------
# Бэкенды
# -------------------------

BackendName = Literal["mock", "http", "mtproto", "bot"]

class BaseBackend:
    def list_gifts(self, limit: int = 20, cursor: Optional[str] = None, source: Optional[str] = None) -> GiftList:
        raise NotImplementedError
    def get_gift(self, gift_id: str) -> Gift:
        raise NotImplementedError
    def claim_gift(self, gift_id: str) -> GiftClaimResult:
        raise NotImplementedError
    def close(self) -> None:
        pass

class MockBackend(BaseBackend):
    def __init__(self):
        self._data: Dict[str, Gift] = {
            "abc123": Gift(id="abc123", name="Premium 1m", link="https://t.me/gifts/abc123", price_ton=0.0, source="mock"),
            "pepe01": Gift(id="pepe01", name="Sticker Pack Pepe", link="https://t.me/gifts/pepe01", price_ton=1.2, source="mock"),
        }
        self._claimed: set[str] = set()

    def list_gifts(self, limit=20, cursor=None, source=None) -> GiftList:
        items = list(self._data.values())
        if source:
            items = [g for g in items if g.source == source]
        return GiftList(items=items[:limit], total=len(items), next_cursor=None)

    def get_gift(self, gift_id: str) -> Gift:
        g = self._data.get(gift_id)
        if not g:
            raise GiftAPIError(f"Gift {gift_id} not found", status=404)
        return g

    def claim_gift(self, gift_id: str) -> GiftClaimResult:
        if gift_id not in self._data:
            return GiftClaimResult(gift_id=gift_id, status="failed", detail="not_found")
        if gift_id in self._claimed:
            return GiftClaimResult(gift_id=gift_id, status="already_claimed")
        self._claimed.add(gift_id)
        return GiftClaimResult(gift_id=gift_id, status="claimed")

class HTTPBackend(BaseBackend):
    RETRY_STATUSES = {408, 425, 429, 500, 502, 503, 504}
    def __init__(self, base_url: str, token: Optional[str] = None, user_agent: Optional[str] = None,
                 timeout_s=15.0, max_retries=3, backoff_factor=0.75, headers: Optional[dict] = None):
        try:
            import httpx
        except ImportError:
            raise RuntimeError("Install httpx to use HTTP backend")
        self.client = httpx.Client(
            base_url=base_url,
            headers=self._build_headers(token, user_agent, headers),
            timeout=timeout_s
        )
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

    def _build_headers(self, token, ua, extra) -> dict:
        h = {"User-Agent": ua or "gift-api/onefile"}
        if token: h["Authorization"] = f"Bearer {token}"
        if extra: h.update(extra)
        return h

    def _request(self, method, url, **kwargs):
        last_exc = None
        from httpx import HTTPStatusError
        for delay in list(_backoff_delays(self.max_retries, self.backoff_factor)) + [0]:
            try:
                resp = self.client.request(method, url, **kwargs)
                if resp.status_code == 401:
                    raise GiftAuthError("Unauthorized", status=401, payload=resp.json())
                if resp.status_code == 429:
                    raise GiftRateLimitError("Rate limited", status=429, payload=resp.json())
                resp.raise_for_status()
                return resp
            except (GiftAPIError, HTTPStatusError) as e:
                last_exc = e
                if delay: time.sleep(delay)
            except Exception as e:
                last_exc = e
                if delay: time.sleep(delay)
        raise GiftAPIError(str(last_exc))

    def list_gifts(self, limit=20, cursor=None, source=None) -> GiftList:
        params = {"limit": limit}
        if cursor: params["cursor"] = cursor
        if source: params["source"] = source
        resp = self._request("GET", "/api/gifts", params=params)
        data = resp.json()
        items = [self._parse_gift(x) for x in data.get("items", [])]
        return GiftList(items=items, total=int(data.get("total", len(items))), next_cursor=data.get("next_cursor"))

    def get_gift(self, gift_id: str) -> Gift:
        resp = self._request("GET", f"/api/gifts/{gift_id}")
        return self._parse_gift(resp.json())

    def claim_gift(self, gift_id: str) -> GiftClaimResult:
        resp = self._request("POST", f"/api/gifts/{gift_id}/claim", json={})
        data = resp.json()
        return GiftClaimResult(gift_id=gift_id, status=str(data.get("status", "failed")), detail=data.get("detail"))

    def _parse_gift(self, x: dict) -> Gift:
        return Gift(
            id=str(x.get("id") or x.get("gift_id")),
            name=x.get("name") or x.get("title") or "Gift",
            link=x.get("link") or x.get("url") or "",
            price_ton=_safe_float(x.get("price_ton") or x.get("priceTon")),
            currency=x.get("currency") or "TON",
            expires_at=x.get("expires_at") or x.get("expiresAt"),
            source=x.get("source"),
            metadata=x.get("metadata") or {},
        )

    def close(self):
        self.client.close()

class MTProtoBackend(BaseBackend):
    def __init__(self, api_id: int, api_hash: str, session: str):
        try:
            from telethon import TelegramClient
            from telethon.sessions import StringSession
        except ImportError:
            raise RuntimeError("Install telethon to use MTProto backend")
        self.client = TelegramClient(StringSession(session), api_id, api_hash)
        self._started = False

    def _ensure(self):
        if not self._started:
            self.client.connect()
            self._started = True

    def list_gifts(self, limit=20, cursor=None, source=None) -> GiftList:
        self._ensure()
        # TODO: parse real messages
        items = [Gift(id="mt1", name="MTProto Gift", link="https://t.me/gifts/mt1", source="telegram")]
        return GiftList(items=items[:limit], total=len(items), next_cursor=None)

    def get_gift(self, gift_id: str) -> Gift:
        self._ensure()
        return Gift(id=gift_id, name="MTProto Gift", link=f"https://t.me/gifts/{gift_id}")

    def claim_gift(self, gift_id: str) -> GiftClaimResult:
        self._ensure()
        return GiftClaimResult(gift_id=gift_id, status="claimed")

    def close(self):
        if self._started:
            self.client.disconnect()
            self._started = False

class BotBackend(BaseBackend):
    """Новый backend: получает подарки из Telegram Bot API."""
    def __init__(self, bot_token: str, chat_id: Optional[int] = None):
        try:
            import requests
        except ImportError:
            raise RuntimeError("Install requests to use Bot backend")
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"

    def _get_updates(self, limit: int) -> List[dict]:
        import requests
        params = {"limit": limit}
        resp = requests.get(f"{self.base_url}/getUpdates", params=params).json()
        if not resp.get("ok"):
            raise GiftAPIError("Bot API error", payload=resp)
        return resp.get("result", [])

    def list_gifts(self, limit=20, cursor=None, source=None) -> GiftList:
        updates = self._get_updates(limit)
        gifts: List[Gift] = []
        for upd in updates:
            msg = upd.get("message") or upd.get("channel_post")
            if not msg: continue
            if self.chat_id and msg["chat"]["id"] != self.chat_id:
                continue
            text = msg.get("text", "") or msg.get("caption", "")
            for m in re.finditer(r"t\\.me/gifts/([A-Za-z0-9_-]+)", text):
                gid = m.group(1)
                gifts.append(Gift(
                    id=gid,
                    name=text.strip().split("\n")[0][:50],
                    link=f"https://t.me/gifts/{gid}",
                    source="bot"
                ))
        return GiftList(items=gifts[:limit], total=len(gifts), next_cursor=None)

    def get_gift(self, gift_id: str) -> Gift:
        # Не поддерживается напрямую
        raise GiftAPIError("BotBackend does not support get_gift")

    def claim_gift(self, gift_id: str) -> GiftClaimResult:
        # Требуется другой backend для claim
        return GiftClaimResult(gift_id=gift_id, status="failed", detail="not_supported")

# -------------------------
# Публичный API
# -------------------------

class GiftAPI:
    def __init__(self,
                 backend: BackendName | None = None,
                 *,
                 # http
                 base_url: Optional[str] = None,
                 token: Optional[str] = None,
                 # mtproto
                 api_id: Optional[int] = None,
                 api_hash: Optional[str] = None,
                 session: Optional[str] = None,
                 # bot
                 bot_token: Optional[str] = None,
                 chat_id: Optional[int] = None):
        name = (backend or _env("GIFT_API_BACKEND", "mock")).lower()
        if name == "http":
            base_url = base_url or _env("GIFT_API_BASE_URL")
            if not base_url:
                raise ValueError("HTTP backend requires base_url")
            token = token or _env("GIFT_API_TOKEN")
            self.impl = HTTPBackend(base_url=base_url, token=token)
        elif name == "mtproto":
            api_id = api_id or int(_env("TG_API_ID", "0"))
            api_hash = api_hash or _env("TG_API_HASH")
            session = session or _env("TG_STRING_SESSION")
            self.impl = MTProtoBackend(api_id=api_id, api_hash=api_hash, session=session)
        elif name == "bot":
            bot_token = bot_token or _env("TG_BOT_TOKEN")
            chat_id = chat_id or (_env("TG_CHAT_ID") and int(_env("TG_CHAT_ID")))
            if not bot_token:
                raise ValueError("Bot backend requires bot_token")
            self.impl = BotBackend(bot_token=bot_token, chat_id=chat_id)
        else:
            self.impl = MockBackend()

    def list_gifts(self, limit=20, cursor=None, source=None) -> GiftList:
        return self.impl.list_gifts(limit=limit, cursor=cursor, source=source)

    def get_gift(self, gift_id: str) -> Gift:
        return self.impl.get_gift(gift_id)

    def claim_gift(self, gift_id: str) -> GiftClaimResult:
        return self.impl.claim_gift(gift_id)

    def close(self) -> None:
        try:
            self.impl.close()
        except Exception:
            pass

__all__ = [
    "GiftAPI", "Gift", "GiftList", "GiftClaimResult",
    "GiftAPIError", "GiftAuthError", "GiftRateLimitError"
]

__version__ = "0.4.0"


# -------------------------
# CLI
# -------------------------

def _cli() -> int:
    parser = argparse.ArgumentParser(prog="gift-api", description="Gift API one-file CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # list, get, claim
    p_list = sub.add_parser("list", help="List gifts")
    p_list.add_argument("--limit", type=int, default=10)
    p_list.add_argument("--source", type=str, default=None)

    p_get = sub.add_parser("get", help="Get gift by id")
    p_get.add_argument("gift_id", type=str)

    p_claim = sub.add_parser("claim", help="Claim gift by id")
    p_claim.add_argument("gift_id", type=str)

    # backend options
    parser.add_argument("--backend", choices=["mock","http","mtproto","bot"], default=_env("GIFT_API_BACKEND","mock"))
    parser.add_argument("--base-url", type=str, default=_env("GIFT_API_BASE_URL"))
    parser.add_argument("--token", type=str, default=_env("GIFT_API_TOKEN"))
    parser.add_argument("--api-id", type=int, default=int(_env("TG_API_ID","0")))
    parser.add_argument("--api-hash", type=str, default=_env("TG_API_HASH"))
    parser.add_argument("--session", type=str, default=_env("TG_STRING_SESSION"))
    parser.add_argument("--bot-token", type=str, default=_env("TG_BOT_TOKEN"))
    parser.add_argument("--chat-id", type=int, default=(_env("TG_CHAT_ID") and int(_env("TG_CHAT_ID"))))

    args = parser.parse_args()

    api = GiftAPI(
        backend=args.backend,
        base_url=args.base_url,
        token=args.token,
        api_id=args.api_id or None,
        api_hash=args.api_hash,
        session=args.session,
        bot_token=args.bot_token,
        chat_id=args.chat_id or None,
    )

    try:
        if args.cmd == "list":
            res = api.list_gifts(limit=args.limit, source=args.source)
            for g in res.items:
                print(f"{g.id}\t{g.name}\t{g.price_ton or '-'} {g.currency}\t{g.link}")
            print(f"-- total: {res.total}")
        elif args.cmd == "get":
            g = api.get_gift(args.gift_id)
            print(json.dumps(g.__dict__, ensure_ascii=False, indent=2))
        elif args.cmd == "claim":
            r = api.claim_gift(args.gift_id)
            print(json.dumps(r.__dict__, ensure_ascii=False, indent=2))
        return 0
    except GiftAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        if e.payload:
            print(json.dumps(e.payload, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1
    finally:
        api.close()

if __name__ == "__main__":
    sys.exit(_cli())