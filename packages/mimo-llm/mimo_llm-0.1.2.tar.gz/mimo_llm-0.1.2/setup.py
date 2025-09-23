from setuptools import setup, find_packages

setup(
    name='mimo-llm',
    version='0.1.2',
    packages=find_packages(),
    description='A language model for code and conversation.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='ABDESSEMED Mohamed Redha',
    author_email='mohamed.abdessemed@eurocybersecurite.fr',
    url='https://github.com/eurocybersecurite/Mimo-llm',
    project_urls={
        "Documentation": "https://github.com/eurocybersecurite/Mimo-llm#readme",
        "Source": "https://github.com/eurocybersecurite/Mimo-llm",
        "Issues": "https://github.com/eurocybersecurite/Mimo-llm/issues",
    },
    license='Apache-2.0',
    license_files=('LICENSE',),
    install_requires=[
        'transformers>=4.35',
        'datasets>=2.14',
        'accelerate>=0.22',
        'bitsandbytes>=0.41',
        'peft>=0.4.0',
        'torch>=2.1',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    python_requires='>=3.8',
    include_package_data=True,
    package_data={
        "assets": ["*.png"],
    },
)
