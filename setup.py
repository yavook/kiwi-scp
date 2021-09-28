from setuptools import setup, find_packages

setup(
    name="kiwi_scp",
    version="0.1.6",
    packages=find_packages(),
    author="LDericher",
    author_email="ldericher@gmx.de",
    setup_requires="setuptools-pipfile",
    use_pipfile=True,
    entry_points={
        "console_scripts": [
            "kiwi = kiwi_scp.scripts.kiwi:main"
        ],
    },
    data_files=[
        ("", ["data/etc/kiwi_help.txt"])
    ],
    include_package_data=True,
    license="LICENSE",
    description="kiwi is the simple tool for managing container servers.",
    long_description=open("README.md").read(),
)
