from setuptools import setup, find_packages

setup(
    name="globchat",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["requests"],
    description="Global console chat package",
    author="Omer",
    python_requires=">=3.7",
)
