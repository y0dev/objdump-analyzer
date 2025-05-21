from setuptools import setup, find_packages

setup(
    name='objdump-analyzer',
    version='1.0.0',
    description='Fast object dump analysis tool',
    author='Devontae Reid',
    packages=find_packages(),
    install_requires=[],  # No external packages required
    entry_points={
        'console_scripts': [
            'objdump-analyzer = main:main'
        ]
    }
)