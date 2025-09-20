from setuptools import setup, find_packages

with open("README.md") as file:
    read_me_description = file.read()

setup(
    name='dictnavigator',
    version='1.0',
    packages=['dictnavigator'],
    url='https://gitlab.com/asurnovsurnov/dictnavigetor.git',
    author='Aleksei Surnov',
    author_email='asurnovsurnov@gmail.com',
    description='dictnavigator is a tool for working with nested dictionaries in Python. The DictNavigatorKey class allows easy retrieval, updating, and deletion of values by keys at any depth, even inside nested types (tuple, list, dictionary). It also provides a list of all keys at any nesting level. Especially useful for working with JSON data from APIs, simplifying access and modification of needed values.',
    long_description=read_me_description,
    long_description_content_type="text/markdown",
    python_requires='>=3.5.2',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    license='MIT License'
)
