from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name='passphera-core',
    version='0.30.2',
    author='Fathi Abdelmalek',
    author_email='abdelmalek.fathi.2001@gmail.com',
    url='https://github.com/passphera/core',
    description='The core system of passphera project',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires='>=3',
    install_requires=['cipherspy'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Security",
        "Topic :: Security :: Cryptography",
    ]
)
