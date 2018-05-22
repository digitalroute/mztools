from setuptools import setup

exec(open('mztools/ver.py').read())

setup(name='mztools',
      version=__version__,
      description='Digital Route PaaS CLI',
      author='Digital Route',
      author_email='aws-paas@digitalroute.com',
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
