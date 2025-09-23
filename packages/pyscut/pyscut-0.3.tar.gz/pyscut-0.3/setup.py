from setuptools import setup, find_packages

setup(
    name="pyscut",
    version="0.3",
    packages=find_packages(),
    install_requires=[
        "pywin32"
    ],
    entry_points={
        "console_scripts": [
            "pyscut = pyscut:createDesktopShortcut "
        ]
    }
)