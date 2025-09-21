from setuptools import setup, find_packages

setup(
    name="icezip",
    version="1.0.2",
    description="Advanced lightweight ICEZIP archive tool",
    author="Iceland",
    author_email="icelandmc.help@gmail.com",
    url="https://github.com/Icelandmc/Ice-zip",
    py_modules=["icezip"],
    entry_points={
        "console_scripts": ["icezip=icezip:main"]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires=">=3.7"
)
