from setuptools import setup, find_packages


setup(
    name = "qnc",
    version = "1.0",
    url = "https://github.com/liqiming-whu/queryncbi",
    author_email ="liqiming@whu.edu.cn",
    packages=find_packages(),
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'search_pubmed = biotk.queryncbi:run_pubmed',
            'search_geo = biotk.queryncbi:run_geo',
            ]
        },
    )