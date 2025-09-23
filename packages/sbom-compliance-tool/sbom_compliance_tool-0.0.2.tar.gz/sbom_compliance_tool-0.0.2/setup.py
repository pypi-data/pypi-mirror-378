# SPDX-FileCopyrightText: 2025 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import setuptools

from sbom_compliance_tool.config import sbom_compliance_tool_version
from sbom_compliance_tool.config import description
from sbom_compliance_tool.config import module_name

requirements = []
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

requirements_dev = []
with open('requirements-dev.txt') as f:
    requirements_dev = f.read().splitlines()

with open("README.md") as f:
    _long_description = f.read()

setuptools.setup(
    name='sbom_compliance_tool',
    version=sbom_compliance_tool_version,
    author="Henrik Sanklef",
    author_email="hesa@sandklef.com",
    description=description.replace('\n', ' '),
    long_description=_long_description,
    long_description_content_type="text/markdown",
    license_files=('LICENSES/GPL-3.0-or-later.txt',),
    url="https://github.com/hesa/licomp-toolkit",
    packages=['sbom_compliance_tool'],
    entry_points={
        "console_scripts": [
            "licomp-toolkit = sbom_compliance_tool.__main__:main",
        ],
    },
    package_data={
        f'{module_name}': ['data/*.json'],
    },
    install_requires=requirements,
    extras_require={
        'dev': requirements_dev,
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Legal Industry",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Quality Assurance",
    ],
    python_requires='>=3.6',
)
