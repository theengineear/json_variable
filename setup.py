from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='json_variable',
    version='0.0.1',
    use_2to3=False,
    author='Andrew Seier',
    author_email='andseier@gmail.com',
    maintainer='Andrew Seier',
    maintainer_email='andseier@gmail.com',
    url='https://github.com/theengineear/json_variable',
    description='Sub-string Extension to JSON Pointer References.',
    long_description=readme(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    install_requires=['jsonpointer'],
    license='MIT',
    packages=['json_variable']
)
