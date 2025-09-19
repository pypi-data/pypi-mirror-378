

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

with open('requirements.txt',encoding='utf-8') as requirements_file:
    all_pkgs = requirements_file.readlines()

requirements = [pkg.replace('\n', '') for pkg in all_pkgs if "#" not in pkg]
test_requirements = []

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
    long_description_content_type="text/markdown",
    test_suite='tests',
    tests_require=test_requirements,
    version='0.0.1',
    zip_safe=False,
    dependency_links=[]
)






