from setuptools import find_packages, setup

setup(
    name='afpy',
    version='0.1.dev0',
    description='Site web de l\'Afpy',
    url='https://www.afpy.org',
    author='Afpy',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Flask',
        'libsass',
        'docutils',
    ],
    scripts=['afpy.py'],
)
