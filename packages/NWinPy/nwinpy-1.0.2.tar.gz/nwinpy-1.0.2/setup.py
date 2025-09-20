from setuptools import setup, find_packages

with open("README.md", "r", encoding="UTF-8") as f:
    long_description = f.read()

setup(
    name="NWinPy",
    version="1.0.2",
    author="bzNAK",
    url="https://space.bilibili.com/3546681377295185?spm_id_from=333.337.0.0",
    description="Omnipotent processing pylib!(Not only.Will continue to update many features.).",
    long_description=long_description,
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    packages=find_packages(),
)
