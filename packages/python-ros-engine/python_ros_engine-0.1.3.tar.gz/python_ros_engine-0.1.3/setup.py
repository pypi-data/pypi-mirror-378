from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="python-ros-engine",
    version="0.1.2",
    author="Python ROS Engine Team",
    author_email="pyros@example.com",
    description="A pure Python implementation of ROS2 functionality with "
    "bridging capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yhbcode000/python-ros-engine",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Distributed Computing",
    ],
    python_requires=">=3.8",
    install_requires=[
        "hydra-core>=1.0.0",
    ],
    extras_require={
        "test": [
            "pytest>=6.0.0",
            "pytest-asyncio>=0.14.0",
        ],
        "dev": [
            "pytest>=6.0.0",
            "pytest-asyncio>=0.14.0",
            "mkdocs>=1.4.0",
            "mkdocs-material>=9.0.0",
            "black>=22.0.0",
            "isort>=5.10.0",
            "flake8>=4.0.0",
            "pre-commit>=2.20.0",
        ],
    },
)
