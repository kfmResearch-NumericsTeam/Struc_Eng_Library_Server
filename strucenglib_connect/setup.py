import setuptools

dependencies = [
    'compas_fea',
    'websockets',
    'requests'
]

setuptools.setup(
    name='strucenglib_connect',
    version='0.1',
    author="StrucEngLib Authors",
    description="",
    install_requires=dependencies,
    url="https://github.com/kfmResearch-NumericsTeam/Struc_Eng_Library_Server",
    packages=['strucenglib_connect'],

    entry_points={
        'console_scripts': ['strucenglib_server=strucenglib_connect.wsserver:main'],
    }
)
