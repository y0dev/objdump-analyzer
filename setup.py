from setuptools import setup, find_packages

setup(
    name='objdump-analyzer',
    version='1.0.0',
    description='Fast object dump analysis tool',
    author='Your Name',
    packages=find_packages(),
    install_requires=[
        'click',
        'subprocess',
        'logging',
        'json'
    ],
    entry_points={
        'console_scripts': [
            'objdump-analyzer = main:main'
        ]
    }
)
