import setuptools

VERSION = '0.1'

setuptools.setup(name='TTImpacts',
                 version=VERSION,
                 description='Impacts history service for The Tale',
                 long_description='Impacts history service for The Tale',
                 url='https://github.com/Tiendil/the-tale',
                 author='Aleksey Yeletsky <Tiendil>',
                 author_email='a.eletsky@gmail.com',
                 license='BSD',
                 packages=setuptools.find_packages(),
                 install_requires=[],
                 entry_points={'console_scripts':
 []},
                 include_package_data=True,
                 test_suite='tests')
