from setuptools import setup

setup(
    name="oifsa",
    packages=['oifsa'],
    version='0.0.1',
    install_requires=[
        'Click',
        'requests',
        'beautifulsoup4',
        'pandas',
        'xmltodict',
        'tqdm'
    ],
    entry_points='''
        [console_scripts]
        oi_fsa = oifsa.cli:cli
    ''',
)
