from setuptools import setup, find_packages

setup(
    name="laia-ontology-sync",
    version="0.1.1",
    description="Librería para sincronizar MongoDB con Apache Jena Fuseki usando RDF.",
    author="Itziar Mensa Minguito",
    author_email="itziar.mensa08@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "requests>=2.0",
        "rdflib>=7.0",
        "pymongo>=4.0",
        "python-dotenv>=1.0",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-runner",
            "setuptools>=61.0",
            "wheel",
            "twine"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)
