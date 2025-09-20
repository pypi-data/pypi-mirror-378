from setuptools import setup, find_packages

setup(
    name='mytsoss',
    version='0.1.2',
    author='Your Name',
    author_email='your.email@example.com',
    description='A Discord bot library for managing executable programs.',
    packages=find_packages(),
    install_requires=[
        'discord.py',  # Discord API wrapper
        'requests',     # For downloading files
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)