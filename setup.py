from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='tparse',
      version='0.3',
      description='Natural language parser for Things 3.',
      long_description=readme(),
      url='https://github.com/dustinknopoff/py-thingsparser',
      author='Dustin Knopoff',
      author_email='knopoffdustin1@gmail.com',
      license='MIT',
      packages=['tparse'],
      install_requires=[
          'pyperclip',
          'python-dateutil'
      ],
      entry_points={
          'console_scripts': [
                'tparse=tparse.tparse:main'
            ],
      },
      zip_safe=False,
      setup_requires='pytest-runner',
      tests_require=['pytest'])
