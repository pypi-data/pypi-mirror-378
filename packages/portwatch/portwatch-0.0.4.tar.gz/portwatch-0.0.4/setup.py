from setuptools import find_packages, setup

setup(
    name="portwatch",
    version="0.0.4",
    description="A simple tool to monitor network ports and connections",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    install_requires=["psutil", "rich"],
    entry_points={
        "console_scripts": [
            "portwatch=portwatch.cli:main",
        ],
    },
    author="Madushanaka Rajapaksha",
    author_email="madushanakarajapakshe999@gmail.com",
    url="https://github.com/madushanakarajapakshe999/portwatch",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)

 