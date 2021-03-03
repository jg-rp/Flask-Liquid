import setuptools


with open("README.rst", "r") as fd:
    long_description = fd.read()

setuptools.setup(
    name="Flask-Liquid",
    version="0.1.3",
    description="A Flask extension for rendering Liquid templates.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/jg-rp/flask-liquid",
    packages=setuptools.find_packages(exclude=["tests*"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=["flask>=0.7", "python-liquid>=0.6.1"],
    test_suite="tests",
    python_requires=">=3.7",
)
