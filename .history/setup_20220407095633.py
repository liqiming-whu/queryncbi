import os
import subprocess
from glob import glob
from setuptools import setup, find_packages
from setuptools.command.install import install


def install_dependency():  
    cmd = "pip install -r requirements.txt"
    path = os.path.dirname(os.path.abspath(__file__))
    subprocess.check_call(cmd, cwd=path, shell=True) 


class CustomInstall(install): 
    def run(self):
        install_dependency()
        super().run() 


setup(
    name = "qnc",
    version = "1.0",
    url = "https://github.com/liqiming-whu/queryncbi",
    author_email ="liqiming@whu.edu.cn",
    cmdclass={'install': CustomInstall},
    packages=find_packages(),
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'search_pubmed = biotk.queryncbi:run_pubmed',
            'search_geo = biotk.queryncbi:run_geo',
            ]
        },
    )