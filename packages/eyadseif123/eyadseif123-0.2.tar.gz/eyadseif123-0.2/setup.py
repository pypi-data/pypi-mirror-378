from setuptools import setup, find_packages

setup(
    name="eyadseif123",
    version="0.2",
    packages=find_packages(),
    install_requires=["flask"],
    entry_points={
        "console_scripts": [
            "hello-world = eyadseif123.__main__:main"
        ]
    },
)
