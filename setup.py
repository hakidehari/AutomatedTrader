from setuptools import find_packages, setup

import os
import versioneer

HERE = os.path.dirname(os.path.abspath(__file__))


def extract_requires():
    with open(os.path.join(HERE, "requirements/requirements.txt"), "r") as reqs:
        return [line.split(" ")[0] for line in reqs if not line[0] in ("-", "#")]


setup(
    name="AutomatedTrader",
    version=versioneer.get_version(),
    description="Automated Turtle Trader",
    author="Haki Dehari and Andrew Yang",
    author_email="hakidehari@outlook.com",
    url="https://github.com/hakidehari/RepliClade",
    cmdclass=versioneer.get_cmdclass(),
    packages=find_packages(),
    include_package_data=True,
    install_requires=extract_requires(),
    data_files=[("requirements", ["requirements/requirements.txt"])],
    entry_points={"console_scripts": ["automated_trader = automated_trader.app:main"]},
)
