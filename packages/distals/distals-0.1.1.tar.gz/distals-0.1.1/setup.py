from setuptools import setup, find_packages

with open('README.md') as f:
    description = f.read()

setup(
    name='distals',
    version='0.1.1',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'scipy >= 1.8.0',
        'numpy >= 2.0.0',
        'scikit-learn >= 1.0.0'
    ],
    entry_points={
        'console_scripts': [
            'distals = distals:main'
        ]
    },
    long_description=description,
    long_description_content_type='text/markdown',
)

