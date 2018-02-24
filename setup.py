"""
Package config for selfie bot
"""
import setuptools

setuptools.setup(
    name='trans_girls_rule_the_world',
    version='5.0.0',
    description='A tumblr bot to reblog trans girl\'s selfies',
    url='https://github.com/Deafjams/trans_girls_rule_the_world',
    author='Emma Foster',
    license='Public Domain',
    install_requires=[
        'pytumblr>=0.0.7,<0.1.0',
        'emoji>=0.4.5,<1.0',
        'plan>=0.5,<1.0',
        'flask>=0.12.2,<1.0'
    ],
    package_dir={
        'trans_girls_rule_the_world': 'trans_girls_rule_the_world'
    },
    packages=setuptools.find_packages(),
    classifiers=(
        "Development Status :: 5 - Production",
        "License :: Public Domain",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.6"
    )
)
