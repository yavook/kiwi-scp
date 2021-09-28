from setuptools import setup, find_packages

setup(
    name="kiwi_scp",
    version="0.1.6",
    description="kiwi is the simple tool for managing container servers.",
    long_description=open("README.md").read(),
    packages=find_packages(),
    license="LICENSE",

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
        ('./kiwi_scp/', [
            "*.txt",
            "*.yml",
            "*.Dockerfile",
            "data/etc/version_tag",
        ])
    ],
    include_package_data=True,
)
