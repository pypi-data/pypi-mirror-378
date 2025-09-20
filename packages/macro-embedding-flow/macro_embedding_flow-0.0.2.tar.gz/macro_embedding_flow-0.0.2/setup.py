from setuptools import setup , find_packages
from pathlib import Path


this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name='macro-embedding-flow',
    version='0.0.2',
    description='ETL Para banco macro, transforma los chunks de pdf bancarios y los tranforma en embeddings de 768 dimenciones y la sube a s3',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Walter Facundo Vega',
    author_email='facundo.vega1234@gmail.com',
    url='https://github.com/facuvegaingenieer/macro-embedding-flow',
    license='MIT', 
    packages=find_packages(),
    install_requires=[
    'torch==2.8.0',
    'sentence-transformers',
    'transformers',
    'boto3',
    'pandas',
    'pyarrow',
    'python-dotenv',
    ],
    entry_points={
        'console_scripts': [
            'trackflow=track_flow.main:main',
        ],
    },
    python_requires='>=3.8',
    
    classifiers=[
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.8',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
],
)