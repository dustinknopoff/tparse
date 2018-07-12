from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='tparse',
      version='0.1',
      description='Natural language parser for Things 3.',
      long_description=readme(),
      url='https://github.com/dustinknopoff/py-thingsparser',
      author='Dustin Knopoff',
      author_email='knopoffdustin1@gmail.com',
      license='MIT',
      packages=['things_parser'],
      install_requires=[
          'pyperclip',
          'python-dateutil'
      ],
      entry_points={
          'console_scripts': [
                'tparse=things_parser.things_parser:main'
            ],
      },
      zip_safe=False)
