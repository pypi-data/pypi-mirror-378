from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    page_description = f.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="climg-tools",
    version="0.0.1",
    author="Luiz Carlos Dev",
    author_email="luizcarlosdev@gmail.com",
    description="A personal python package for image processing",
    long_description=page_description,
    long_description_content_type="text/markdown",
    url="https://github.com/milhodroid/climg-tools",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)