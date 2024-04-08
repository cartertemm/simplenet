from setuptools import setup, find_packages


setup(
	name="Simplenet",
	version="0.1",
	packages=find_packages(),
	install_requires=open("requirements.txt", "r").read().split("\n"),
	author="Carter Temm",
	author_email="cartertemm@gmail.com",
	description="The simplest python wrapper around ENet",
	license="MIT",
	url="http://github.com/cartertemm/simplenet",
	long_description=open("readme.md", "r").read(),
	long_description_content_type="text/markdown",
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Development Status :: 3 - Alpha",
		"Topic :: System :: Networking",
		
	]
)