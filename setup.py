from setuptools import setup, find_packages

setup(
    name='nnUNet_translation',
    version='0.1',
    packages=find_packages(include=['nnunetv2', 'nnunetv2.*']),  # Include specific packages
    install_requires=[
        # Your other dependencies
    ],
    # Add other setup parameters if necessary
)
