from distutils.core import setup
import py2exe

setup(name='WhoisScanner',
      version='3.7',
      description='Scan Whois',
      author='Saman Dadmand',
      author_email='saman.dadmand@gmail.com',
      console=["ListMain.py"],
      requires=['tabulate', 'mysql', 'cryptography']
      )
