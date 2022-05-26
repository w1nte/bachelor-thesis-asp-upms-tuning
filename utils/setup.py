from setuptools import setup

setup(
    name='mwinters-thesis-utils',
    version='1.1',
    packages=[''],
    url='',
    install_requires=[
        'pandas~=1.2.4',
        'matplotlib~=3.4.1'
    ],
    license='',
    author='winte',
    author_email='',
    description='',
    entry_points={
        'console_scripts': [
            'gantt=gantt:main'
        ]
    }
)
