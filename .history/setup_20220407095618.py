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
            'bam_anno = biotk.bam_anno:run',
            'bed2bedgraph = biotk.bed2bedgraph:run',
            'fragment_sizes = biotk.fragment_sizes:run',
            'gtfparser = biotk.gtfparser:run',
            'merge_row = biotk.merge_row:run',
            'merge_subseq = biotk.merge_subseq:run',
            'merge_tables = biotk.merge_table_with_header:run',
            'search_pubmed = biotk.queryncbi:run_pubmed',
            'search_geo = biotk.queryncbi:run_geo',
            'remove_duplicated_reads = biotk.remove_duplicated_reads:run',
            'remove_no_chimeric = biotk.remove_no_chimeric:run',
            'rmats_filter = biotk.rmats_filter:run',
            'xlsx2tsv = biotk.xlsx2tsv:run'
            ]
        },
    # install_requires = ['pysam',
    #                     'bx-python',
    #                     'pandas',
    #                     'biopython',
    #                     'openpyxl',
    #                     ], 
    )