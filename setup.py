from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='asteroid_tracker',
    version='0.0.1',
    description='Asteroid tracker',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Joe Singleton',
    author_email='joesingo@gmail.com',
    install_requires=[
        'PyYAML==5.1.1',
        'Jinja2==2.11.3',
        'requests==2.22.0',
    ],
    extras_require={
        'test': [
            'pytest',
            'coverage',
        ],
    },
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "ast-tracker=asteroid_tracker.build_site:main",
        ]
    }
)
