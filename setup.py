from setuptools import find_packages, setup

tests_requirements = [
    'pytest',
    'pytest-cov',
    'pytest-flake8',
    'pytest-isort',
    'black',
    'isort',
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
        'Flask-Caching',
        'libsass',
        'docutils',
        'feedparser',
        'python-dateutil',
        'itsdangerous',
    ],
    scripts=['afpy.py'],
    setup_requires=['pytest-runner'],
    tests_require=tests_requirements,
    extras_require={'test': tests_requirements,
                    'sentry': 'sentry-sdk[flask]'}
)
