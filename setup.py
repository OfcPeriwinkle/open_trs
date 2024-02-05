from setuptools import setup, find_packages

setup(
    name='open_trs',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'flask',
    ],
    entry_points={
        'console_scripts': [
            # 'open_trs=open_trs.server:main',
        ],
    },
)