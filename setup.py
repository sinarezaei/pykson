from setuptools import setup, find_packages
with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(name='funniest',
      version='0.9.9.8.4',
      description='Json Serializer/Deserializer for python',
      url='https://github.com/vhdmsm/pykson',
      author='Sina Rezaei',
      author_email='sinarezaei1991@gmail.com',
      license='MIT',
      packages = find_packages(),
      install_requires=required,
      zip_safe=False) 
