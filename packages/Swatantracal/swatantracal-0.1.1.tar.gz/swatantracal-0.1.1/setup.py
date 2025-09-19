from setuptools import setup, find_packages

setup(
    name='Swatantracal',
    version='0.1.1',  # bump version since PyPI doesn’t allow re-uploading the same version
    author='Swatantra',
    author_email="swatantra3577@gmail.com",  # fixed email
    description='A simple calculator package for basic math operations',
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'Swatantracal=Swatantracal.calculator:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Education',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Education',
        'Topic :: Utilities',
    ],
    keywords="calculator math arithmetic add subtract multiply divide",
)
