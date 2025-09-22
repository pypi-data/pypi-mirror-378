from setuptools import setup, find_packages

setup(
    name='threshopt',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'scikit-learn',
        'matplotlib',
        'numpy',
    ],
    author='Salvatore Zizzi',
    author_email='salvo.zizzi@gmail.com', 
    description='Automatic threshold optimization for binary classifiers.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/salvo-zizzi/threshopt', 
    license='Apache 2.0',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
