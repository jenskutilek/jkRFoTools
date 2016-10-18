#! /usr/bin/env python

from distutils.core import setup

setup(
		name = "jkRFoTools",
		version = "0.1",
		description = "Support libraries for RoboFont scripts.",
		author = "Jens Kutilek",
		url = "https://github.com/jenskutilek/jkRFoTools",
		license = "MIT",
		platforms = ["Mac"],
		packages = [
			"jkRFoTools",
			"jkRFoTools/pens",
		],
		package_dir = {"": "Lib"},
	)
