from distutils.core import setup
import py2exe

setup(name='WhoisScanner',
      version='4.0.0',
      description='Scan Whois',
      author='Saman Dadmand',
      author_email='saman.dadmand@gmail.com',
      console=["Main.py"],
      requires=['tabulate', 'mysql', 'cryptography', 'colorama', 'colorama']
      )
