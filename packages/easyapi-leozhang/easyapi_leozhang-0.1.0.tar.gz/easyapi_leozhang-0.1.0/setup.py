from setuptools import setup, find_packages

setup(
    name="easyapi-leozhang",
    version="0.1.0",
    description="A simple unified interface for major AI APIs.",
    author="Your Name",
    author_email="youremail@example.com",
    packages=find_packages(),
    install_requires=[
        "requests",
        "google-generativeai",
        "cohere"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires=">=3.7",
)
