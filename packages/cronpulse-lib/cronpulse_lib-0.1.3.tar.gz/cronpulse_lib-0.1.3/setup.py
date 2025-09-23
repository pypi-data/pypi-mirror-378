from setuptools import setup, find_packages
from pathlib import Path

readme_path = Path(__file__).resolve().parent.parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else "CronPulse client library for Python"

setup(
    name="cronpulse-lib",  # renamed from cronpulse (taken on PyPI)
    version="0.1.3",  # bump after restructuring and bug fixes for trusted OIDC publish
    packages=find_packages(include=["cronpulse_lib", "cronpulse_lib.*"]),
    install_requires=["requests>=2.28.0"],
    extras_require={
        "dev": ["pytest>=8.0.0", "pre-commit>=3.0.0"]
    },
    description="CronPulse client library for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/cronpulse-lib",
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
    ],
)
