from setuptools import setup, find_packages
import os

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
def read_requirements(file):
    if not os.path.exists(file):
        return []
    with open(file, "r", encoding="utf-8") as f:
        requirements = []
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                requirements.append(line)
        return requirements

requirements = read_requirements("requirements.txt")
print(f"Found requirements: {requirements}")  # Debug line

setup(
    name="collaborative-gym",
    version="0.1.1",
    author="SALT NLP Lab",
    author_email="your-email@domain.com",  # Update this
    description="Framework and toolkits for building and evaluating collaborative agents that can work together with humans",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SALT-NLP/collaborative-gym",
    project_urls={
        "Bug Tracker": "https://github.com/SALT-NLP/collaborative-gym/issues",
        "Documentation": "https://cogym.saltlab.stanford.edu/",
        "Source Code": "https://github.com/SALT-NLP/collaborative-gym",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.950",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "collaborative-gym=collaborative_gym.command:main",  # If you have a CLI
        ],
    },
    include_package_data=True,
    zip_safe=False,
)