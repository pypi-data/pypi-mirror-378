from setuptools import setup, find_packages

setup(
    name                          = "baseui",
    version                       = "1.0.3",
    packages                      = find_packages(),
    install_requires              = ["requests"],  # Dependencies
    author                        = "Abdelmathin Habachi",
    author_email                  = "contact@abdelmathin.com" ,
    description                   = "baseui",
    long_description              = "# baseui",
    long_description_content_type = "text/markdown",
    url                           = "https://github.com/Abdelmathin/baseui",
    classifiers                   = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
