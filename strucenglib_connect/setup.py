import setuptools

dependencies = [
    'compas_fea',
    'websockets'
]

setuptools.setup(
    name='strucenglib_connect',
    version='0.1',
    author="StrucEngLib Authors",
    description="",
    install_requires=dependencies,
    url="https://github.com/kfmResearch-NumericsTeam/Struc_Eng_Library_Server",
    packages=['strucenglib_connect'],
)
