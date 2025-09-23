from setuptools import setup, find_packages

with open('./README.md') as f:
	long_description = f.read()
with open('LICENSE') as f:
	license_text = f.read()

setup(
	name='py_package_exporter',
	version='0.0.4',
	description='A package to help building your python apps with PyInstaller',
	long_description=long_description,
	long_description_content_type='text/markdown',
	packages=find_packages(),
	url='https://github.com/RadoslawDrab/PyExporter',
	author='Radosław Drab',
	license=license_text,
	keywords=['exporter', 'packages', 'pyinstaller', 'installer']
)