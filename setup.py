from setuptools import setup

with open('README.md', 'r', encoding = 'utf-8') as readme:
    long_description = readme.read()

setup(
    name = 'marude',
    version = '0.3.0',
    description = 'An http api client which allows to automatically convert russian short texts into speech using vk cloud',
    url = 'https://github.com/zeionara/marude',
    author = 'Zeio Nara',
    authon_email = 'zeionara@gmail.com',
    packages = [
        'marude'
    ],
    install_requires = [
        'click',
        'tastier',
        'requests'
    ],
    classifiers = [
        'Programming Language :: Python :: 3.10'
    ],
    long_description = long_description,
    long_description_content_type = 'text/markdown'
)
