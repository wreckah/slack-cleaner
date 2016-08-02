from setuptools import setup

setup(
    name='slack-cleaner',
    version='0.0.1',
    description='Clean up old files from Slack',
    long_description=open('readme.md').read().strip(),
    author='Alexander Pokatilov',
    author_email='wreckah@ya.ru',
    url='https://github.com/wreckah/slack-cleaner',
    packages=['slack_cleaner'],
    install_requires=['requests'],
    license='MIT License',
    zip_safe=False,
    keywords='slack old files free space',
    scripts=['bin/slack_cleaner'],
)
