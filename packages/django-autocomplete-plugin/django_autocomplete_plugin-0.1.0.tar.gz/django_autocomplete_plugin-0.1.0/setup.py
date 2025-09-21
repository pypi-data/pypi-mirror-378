from setuptools import setup, find_packages

setup(
    name="django-autocomplete-plugin",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django>=3.2',
    ],
    description="Django autocomplete plugin for VS Code",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/django-autocomplete-plugin",
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)