from setuptools import setup, find_packages

setup(
    name='postalert',
    version='0.1.2',
    packages=find_packages(),
    include_package_data=True,  # enable including package data
    package_data={
        'postalert': ['config.yml'],  # include config.yml in the postalert package
    },
    install_requires=[
        'requests',
        'PyYAML',
        'tldextract',
        'whispers',
    ],
    entry_points={
        'console_scripts': [
            'postalert=postalert.__main__:main',
        ],
    },
    author='Muthu D.',
    author_email='talktomtuhud@gmail.com',
    description='PostAlert bug bounty secret scanning tool with Discord alerts',
)
