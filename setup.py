from setuptools import setup, find_packages

setup(
    name="searchtruth-telegram-bot",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A Telegram bot for Islamic knowledge using SearchTruth.com",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/searchtruth-bot",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Communications :: Chat",
        "Topic :: Religion",
    ],
    python_requires=">=3.8",
    install_requires=[
        "python-telegram-bot>=20.0",
        "requests>=2.28.0",
        "beautifulsoup4>=4.11.0",
        "lxml>=4.9.0",
    ],
    entry_points={
        "console_scripts": [
            "searchtruth-bot=main:main",
        ],
    },
)