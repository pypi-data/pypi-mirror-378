from setuptools import setup, find_packages

setup(
    name="gift-api",
    version="0.1.0",
    author="Твоё имя",
    author_email="you@example.com",
    description="Gift API Wrapper Pro — работа с Telegram-подарками",
    packages=find_packages(),
    install_requires=["requests", "rich"],
    python_requires=">=3.8",
)
