from setuptools import setup, find_packages

try:
    with open('README.md', encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = ''

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='nivo',
    version='1.0.0',
    description='Nivo ORM - A lightweight async ORM for Python using SQLite and aiosqlite.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Mahdi Ahmadi',
    author_email='mahdiahmadi.1208@gmail.com',
    maintainer='Mahdi Ahmadi',
    maintainer_email='mahdiahmadi.1208@gmail.com',
    url='https://github.com/Mahdy-Ahmadi/nivo',
    download_url='https://github.com/Mahdy-Ahmadi/nivo/archive/refs/tags/v1.0.0.zip',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries',
        'Natural Language :: Persian',
    ],
    python_requires='>=3.7',
    install_requires=[
        "aiosqlite"
    ],
    entry_points={
        "console_scripts": [
            "nivo=nivo.__main__:main",
        ],
    },
    keywords="orm async sqlite database nivo",
    project_urls={
        "Bug Tracker": "https://github.com/Mahdy-Ahmadi/nivo/issues",
        "Documentation": "https://github.com/Mahdy-Ahmadi/nivo#readme",
        "Source Code": "https://github.com/Mahdy-Ahmadi/nivo",
    },
    license="MIT",
    zip_safe=False
)