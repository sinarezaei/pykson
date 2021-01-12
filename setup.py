import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(name='pykson',
                 version='0.9.9.8.3',
                 author='Sina Rezaei',
                 author_email='sinarezaei1991@gmail.com',
                 long_description_content_type="text/markdown",
                 long_description=long_description,
                 description='Pykson: A JSON Serializer/Deserializer for Python',
                 url='https://github.com/sinarezaei/pykson',
                 license='MIT',
                 packages=setuptools.find_packages(),
                 classifiers=[
                     "Programming Language :: Python :: 3",
                     "License :: OSI Approved :: MIT License",
                     "Operating System :: OS Independent",
                 ],
                 install_requires=[
                     'typing>=3.6.2',
                     'six>=1.12.0',
                     'pytz>=2019.3',
                     'dateutil>=2.8.1',
                 ],
                 python_requires='>=3.6',
                 zip_safe=False)
