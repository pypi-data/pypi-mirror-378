from setuptools import setup,find_packages
#change version in __init__.py and here

setup(
    name="phobius-utils",              # Tên trên PyPI
    version="0.1.1",                       # Phiên bản
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "psutil==7.0.0",
        "pympler"
    ],                 # Dependencies nếu có
    author="MetaPhobius",
    author_email="metaphobius@gmail.com",
    description="Using for me",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://tuanca2503.github.io/",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    license="MIT",
)