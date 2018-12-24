from setuptools import setup, find_packages

# I attempted to separate test and install dependencies but couldn't figure it out (in 10 minutes). Keeping them
# toegether for now - pytest is lightweight.
setup(name="svc", version=0.1, description="Strict Venn Classes", author='Dane Austin',
      author_email='dane_austin@fastmail.com.au', url='https://github.com/draustin/svc', license='BSD',
      packages=find_packages(), install_requires=['pytest', 'toposort', 'decorators'], python_requires='>=3.4')
