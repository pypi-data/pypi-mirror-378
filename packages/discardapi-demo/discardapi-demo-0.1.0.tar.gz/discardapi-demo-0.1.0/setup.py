from setuptools import setup, find_packages

setup(
    name="discardapi-demo",
    version="0.1.0",
    description="Python demo client for Discard API",
    author="Qasim Ali",
    author_email="discardapi@gmail.com",
    url="https://github.com/GlobalTechInfo/discardapi",
    packages=find_packages(),
    install_requires=["requests"],
    python_requires=">=3.7",
)
