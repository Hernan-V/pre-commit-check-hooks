from setuptools import setup

setup(
    name='pre-commit-check-hooks',
    version='1.0.0',
    author='Hernan Valenzuela',
    author_email='hernan.valenzuela@example.com',
    description='Pre-commit hooks for checking code quality without modifications',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Hernan-V/pre-commit-check-hooks',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Quality Assurance',
        'Intended Audience :: Developers',
    ],
    install_requires=[
        'case-converter>=1.1.0',
    ],
    python_requires='>=3.7',
)
