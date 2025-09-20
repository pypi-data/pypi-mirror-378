from setuptools import setup, find_packages

setup(
    name="accessnode",
    packages=find_packages(include=["accessnode", "accessnode.*"]),
    package_data={"accessnode": ["py.typed"]},
)