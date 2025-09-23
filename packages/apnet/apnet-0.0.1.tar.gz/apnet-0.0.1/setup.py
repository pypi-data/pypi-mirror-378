from setuptools import setup, find_packages

setup(
    name="apnet",
    version="0.0.1",
    author="Leonardo Nery",
    author_email="leonardonery616@gmail.com",
    description="Biblioteca Python para comunicação TCP entre Access Points (APs) com envio de arquivos e criptografia.",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "cryptography>=41.0.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
