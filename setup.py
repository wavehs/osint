from setuptools import setup, find_packages

setup(
    name="robust",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="An automated OSINT investigation framework",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="<repository_url>",
    packages=find_packages(),
    install_requires=open('requirements.txt').read().splitlines(),
    entry_points={
        'console_scripts': [
            'robust = main:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
