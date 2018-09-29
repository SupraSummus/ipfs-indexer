from setuptools import setup


setup(
    name='ipfs-indexer',
    version='0.1.0',
    description='Content indexer for IPFS',
    license='MIT',
    url='https://github.com/SupraSummus/ipfs-indexer',
    keywords='ipfs',
    py_modules=['db'],
    install_requires=[
        'ipfsapi',
    ],
)
