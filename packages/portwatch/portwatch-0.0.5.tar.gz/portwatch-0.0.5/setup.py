from setuptools import find_packages, setup

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements if you have a requirements.txt (optional)
# with open("requirements.txt", "r", encoding="utf-8") as fh:
#     requirements = [line.strip() for line in fh.readlines() if line.strip() and not line.startswith("#")]
# But for now, we'll list them inline:

setup(
    name="portwatch",
    version="0.0.5",
    author="Madushanaka Rajapaksha",
    author_email="madushanakarajapakshe999@gmail.com",
    description="A real-time TUI app to monitor, filter, and kill processes using dev ports — with conflict alerts and built-in config UI.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/madushanakarajapakshe999/portwatch",   
    packages=find_packages(),
    include_package_data=True,   
    install_requires=[
        "textual>=0.49.0",   # Core TUI framework
        "psutil>=5.9.0",     # Process/port scanning
        "plyer>=2.1.0",      # Cross-platform desktop notifications
        "pyyaml>=6.0",       # Config file handling
        "rich>=13.0.0",      # Optional: for CLI formatting (if used)
    ],
    entry_points={
        "console_scripts": [
            "portwatch=portwatch.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Environment :: Console :: Curses",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Networking",
        "Topic :: Utilities",
    ],
    python_requires=">=3.9",
    license="MIT",
    keywords="port monitor, dev tools, tui, terminal, process killer, port conflict",
    project_urls={
        "Bug Tracker": "https://github.com/madushanakarajapakshe999/portwatch/issues",
        "Source Code": "https://github.com/madushanakarajapakshe999/portwatch",
        "Documentation": "https://github.com/madushanakarajapakshe999/portwatch#readme",
    },
)