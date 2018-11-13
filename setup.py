from setuptools import setup

exec(open('mztools/ver.py').read())

with open('README.md') as file:
    long_description = file.read()

setup(name='mztools',
      version=__version__,
      description='Digital Route PaaS CLI',
      author='Digital Route',
      author_email='aws-paas@digitalroute.com',
      long_description=long_description,
      license='MIT',
      url='https://github.com/digitalroute/mztools',
      packages=['mztools'],
      scripts=['bin/mztools'],
      zip_safe=False,
      install_requires=[
        "boto3",
        "termcolor",
      ],
      )
