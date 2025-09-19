
from __future__ import annotations
import os
from pathlib import Path
from typing import List, Tuple

from setuptools import find_packages, setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

with open('requirements.txt', encoding='utf-8') as requirements_file:
    all_pkgs = requirements_file.readlines()

requirements = [pkg.replace('\n', '') for pkg in all_pkgs if '#' not in pkg]
test_requirements: List[str] = []


def build_config_data_files() -> List[Tuple[str, List[str]]]:
    config_root = Path('configs')
    if not config_root.exists():
        return []

    data_files: List[Tuple[str, List[str]]] = []
    for root, _, files in os.walk(config_root):
        if not files:
            continue
        rel_dir = Path(root).relative_to(config_root)
        install_dir = Path('configs') / rel_dir if rel_dir != Path('.') else Path('configs')
        file_list = [str(Path(root) / file_name) for file_name in files]
        data_files.append((str(install_dir), sorted(file_list)))

    data_files.sort(key=lambda item: item[0])
    return data_files


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
    long_description_content_type='text/markdown',
    test_suite='tests',
    tests_require=test_requirements,
    version='0.0.3',
    zip_safe=False,
    dependency_links=[],
    data_files=build_config_data_files(),
)
