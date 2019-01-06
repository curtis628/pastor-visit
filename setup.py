import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="homevisit",
    version="0.0.1",
    author="Tyler Curtis",
    author_email="tjcurt@gmail.com",
    description="Helps organize and plan pastor home visits",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/curtis628/homevisit",
    packages=setuptools.find_packages(),
    install_requires=[
        "django",
        "django-phonenumber-field",
        "phonenumbers",
        "django-crispy-forms",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
