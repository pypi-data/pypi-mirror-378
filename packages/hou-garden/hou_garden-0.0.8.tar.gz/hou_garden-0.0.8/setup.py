
from __future__ import annotations

import shutil
from pathlib import Path
from typing import List

from setuptools import find_packages, setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

with open('requirements.txt', encoding='utf-8') as requirements_file:
    all_pkgs = requirements_file.readlines()

requirements = [pkg.replace('\n', '') for pkg in all_pkgs if '#' not in pkg]

test_requirements: List[str] = []

CONFIG_PATTERNS: List[str] = [
    'configs/**/*.yaml',
    'configs/**/*.yml',
    'configs/**/*.json',
    'configs/**/*.md',
]


def sync_package_configs() -> List[str]:
    """Copy configs into the package so Hydra can load them post-install."""

    src_root = Path('configs')
    if not src_root.exists():
        return []

    dst_root = Path('hou_garden') / 'configs'

    if dst_root.exists():
        try:
            if dst_root.resolve() == src_root.resolve():
                return CONFIG_PATTERNS
        except OSError:
            pass
        shutil.rmtree(dst_root)

    shutil.copytree(src_root, dst_root)
    return CONFIG_PATTERNS


package_data_patterns = sync_package_configs()

setup(
    name='hou-garden',
    author='Cheng Chen',
    author_email='cheng.chen@hougarden.com',
    description='',
    python_requires='>=3.10',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.10',
    ],
    entry_points={
        'console_scripts': [
            'hougarden-finder=hou_garden.apps.hougarden_cli:cli',
        ],
    },
    install_requires=requirements,
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    packages=find_packages(include=['hou_garden', 'hou_garden.*']),
    package_data={'hou_garden': package_data_patterns or []},
    long_description_content_type='text/markdown',
    test_suite='tests',
    tests_require=test_requirements,
    version='0.0.8',
    zip_safe=False,
    dependency_links=[],
)
