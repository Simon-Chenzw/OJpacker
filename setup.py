from setuptools import setup, find_packages

with open("README.md", "r") as fp:
    long_description = fp.read()

setup(
    # package
    name="ojpacker",
    version="0.1.3",
    packages=find_packages(),
    entry_points={
        'console_scripts': ['ojpacker = ojpacker:start'],
    },
    # requires
    python_requires='>=3.6.9',
    install_requires=[
        'rich>=4.1',
    ],
    # description
    description=
    "a script can packer test data for Olympic informatics Online Judge",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="GNU Lesser General Public License v3 (LGPLv3)",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
        # "Operating System :: OS Independent",
    ],
    # about
    author="Simon_Chen",
    author_email="1020359403@qq.com",
    url="https://github.com/Simon-Chenzw/OJpacker",
)
