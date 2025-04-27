from setuptools import setup, find_packages

setup(
    name="domainsearch",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    entry_points={
        'console_scripts': [
            'domainsearch=domainsearch.cli:run',
        ],
    },
    author="Jon Arnar Jonsson",
    description="Simple CLI tool to find existing domains and check HTTPS availability.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/domainsearch",  # if you want
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
