from setuptools import setup, find_packages

def readme ():
    with open('README.md') as me:
        return me.read()

setup(name='seselab',
      version='0.1.2',
      description='SeseLab: a software platform for teaching physical attacks',
      long_description=readme(),
      long_description_content_type='text/markdown',
      url='https://pablo.rauzy.name/software.html#seselab',
      author='Pablo Rauzy',
      author_email='pr_NOSPAM'+chr(64)+'up8.edu',
      license='GNU AGPL v3+',
      packages=find_packages(),
      include_package_data=True,
      entry_points={
          'console_scripts': [
              'seselab = seselab.bench:main'
          ]
      })
