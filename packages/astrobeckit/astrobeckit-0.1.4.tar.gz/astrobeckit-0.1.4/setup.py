from setuptools import setup, find_packages

setup(
    name="astrobeckit",
    version="0.1.4",
    packages=find_packages(),
    install_requires=[],  # Add dependencies here
    author="Rebecca Nealon",
    description="Package of particularly useful scripts",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/becnealon/becastro",  # Optional
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    entry_points={
        'console_scripts': [
            'synchro=astrobeckit.synchronise_for_movie:main',
            'papergirl=astrobeckit.papergirl:main',
            'auto_resubmit=astrobeckit.automatic_resubmit:main',
        ],
    },    
    python_requires=">=3.8",
)