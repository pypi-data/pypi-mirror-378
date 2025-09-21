from setuptools import setup, find_packages


def readme():
    with open("README.md", "r") as f:
        return f.read()


setup(
    name="tg-bot-discussion",
    version="0.1.0",
    author="BorisPlus",
    description="Telegram Bot framework based on native Python-library for the Telegram Bot API.",
    long_description=readme(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[""],
    classifiers=[
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="python Telegram-bot framework",
    python_requires=">=3.9",
)
