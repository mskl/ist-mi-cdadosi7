from setuptools import setup, find_packages

setup(
    name='ipynb-function',
    version='0.1.0',
    description='Package / Module importer for importing code from Jupyter Notebook files (.ipynb). This is a fork of ipynb that supports importing ipynb files as functions',
    url='http://github.com/jiaminglu/ipynb',
    author='Yuvi Panda, Jiaming Lu',
    author_email='yuvipanda@gmail.com;jiaminglu@live.com',
    license='BSD',
    packages=find_packages(),
    python_requires='>=3.4'
)
