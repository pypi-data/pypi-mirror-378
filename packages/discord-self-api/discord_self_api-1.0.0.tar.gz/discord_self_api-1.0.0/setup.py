from setuptools import setup, find_packages

setup(
    name="discord-self-api",
    version="0.2.0",
    author="Zombie",
    author_email="darshdubey08@gmail.com",
    description="A cross-platform Discord selfbot API wrapper that works on Termux and other platforms",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Operating System :: Android",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Communications :: Chat",
    ],
    python_requires=">=3.7",
    install_requires=[
        "aiohttp>=3.8.0",
        "websockets>=10.0",
    ],
    entry_points={
        'console_scripts': [
            'discord-selfbot=examples.basic_selfbot:main',
        ],
    },
)