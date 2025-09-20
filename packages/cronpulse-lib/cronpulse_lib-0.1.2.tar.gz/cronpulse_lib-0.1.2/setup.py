from setuptools import setup, find_packages

setup(
    name="cronpulse-lib",  # renamed from cronpulse (taken on PyPI)
    version="0.1.2",  # bump for new publish attempt
    packages=find_packages(),
    install_requires=["requests>=2.28.0"],
    extras_require={
        "dev": ["pytest>=8.0.0", "pre-commit>=3.0.0"]
    },
    description="CronPulse client library for Python",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/cronpulse-lib",
    python_requires=">=3.8",
)
