#!/usr/bin/env python

# Copyright (c) 2013-2014 Alex Corley
# All rights reserved.

from __future__ import with_statement

try:
    from setuptools import setup
    extra = dict(test_suite="tests.test.suite", include_package_data=True)
except ImportError:
    from distutils.core import setup
    extra = {}

import os
import sys
import platform

from AWSSQSAlert import __version__

if sys.version_info <= (2, 4):
    error = "ERROR: aws-sqs-alert requires Python Version 2.5 or above...exiting."
    print >> sys.stderr, error
    sys.exit(1)

data_files = [('share/aws-sqs-alert', ['LICENSE.txt', 'README.md', 'CHANGES.txt'])]
distro = platform.dist()[0]
distro_major_version = platform.dist()[1].split('.')[0]
data_files.append(('/etc/aws-sqs-alert', ['sampleconfig.json']))
data_files.append(('/etc/aws-sqs-alert/handlers', ['README.md']))
data_files.append(('/etc/init.d', ['bin/init.d/aws-sqs-alert']))
    
def readme():
    with open("README.md") as f:
        return f.read()

setup(name = "aws-sqs-alert",
      version = __version__,
      description = "Amazon Web Services - Alert on AutoScale or Cloudwatch via SQS",
      long_description = readme(),
      author = "Alex Corley",
      author_email = "acorley@anthroprose.com",
      scripts = ["bin/aws-sqs-alert"],
      url = "https://github.com/Jumpshot/aws-sqs-alert",
      packages = ["AWSSQSAlert", "AWSSQSAlert.handlers", "AWSSQSAlert.test"],
      package_data = {},
      data_files=data_files,
      install_requires=['boto', 'logstash_formatter'],
      license = "GPLv2",
      platforms = "Posix; MacOS X; Windows",
      classifiers = ["Development Status :: 5 - Production/Stable",
                     "Intended Audience :: Developers",
                     "Operating System :: OS Independent",
                     "Topic :: Internet",
                     "Programming Language :: Python :: 2",
                     "Programming Language :: Python :: 2.5",
                     "Programming Language :: Python :: 2.6",
                     "Programming Language :: Python :: 2.7"],
      **extra
      )