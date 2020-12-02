from setuptools import setup, find_packages

reqs = [str(ir.req) for ir in install_reqs]
setup(name='funniest',
      version='0.9.9.8.3',
      description='Json Serializer/Deserializer for python',
      url='https://github.com/vhdmsm/pykson',
      author='Sina Rezaei',
      author_email='sinarezaei1991@gmail.com',
      license='MIT',
      packages = find_packages(),
      install_requires=reqs,
      zip_safe=False) 
