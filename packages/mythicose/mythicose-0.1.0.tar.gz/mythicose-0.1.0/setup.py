from setuptools import setup, find_packages

setup(
    name='mythicose',
    version='0.1.0',
    description='mythic is a good',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='M5TL',
    author_email='your@email.com',
    url='https://github.com/yourusername/discord_program_manager',
    packages=find_packages(),
    install_requires=[
        'discord.py',
        'requests'
    ],
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)