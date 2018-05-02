from setuptools import find_packages, setup

tests_requirements = [
    'pytest',
    'pytest-cov',
    'pytest-flake8',
    'pytest-isort',
]

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
        'Flask-Cache',
        'libsass',
        'docutils',
        'feedparser',
        'python-dateutil',
    ],
    scripts=['afpy.py'],
    setup_requires=['pytest-runner'],
    tests_require=tests_requirements,
    extras_require={'test': tests_requirements}
)
