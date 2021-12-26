import setuptools


with open("README.rst", "r", encoding="utf-8") as fd:
    long_description = fd.read()

setuptools.setup(
    name="Flask-Liquid",
    version="1.0.0",
    description="A Flask extension for rendering Liquid templates.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/jg-rp/flask-liquid",
    packages=setuptools.find_packages(exclude=["tests*"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=["flask>=1.0", "MarkupSafe>=2.0.0", "python-liquid>=1.1.0"],
    test_suite="tests",
    python_requires=">=3.7",
    licence="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    project_urls={
        "Documentation": "https://jg-rp.github.io/liquid/guides/flask-liquid",
        "Issue Tracker": "https://github.com/jg-rp/Flask-Liquid/issues",
        "Source Code": "https://github.com/jg-rp/Flask-Liquid",
        "Change Log": "https://github.com/jg-rp/Flask-Liquid/blob/main/CHANGES.rst",
    },
)
