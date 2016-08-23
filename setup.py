from setuptools import setup, find_packages
setup(
    name="supervisord-touch-reload",
    version="0.0.1",
    packages=find_packages(),
    author="Anton Stavinsky",
    author_email="stavinsky@gmail.com",
    keywords="supervisor supervisord",
    install_requires=['supervisor>=3'],
)
