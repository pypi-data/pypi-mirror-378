from setuptools import setup, find_packages

setup(
    name='simple-calculator-ramzy-elyatim',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[],
    author='Ramzy Alytym',
    author_email='your.email@example.com', # يمكنك تغيير هذا لاحقاً
    description='A simple calculator package for basic math operations',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/simple-calculator-ramzy-elyatim', # يمكنك تغيير هذا لاحقاً
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)


