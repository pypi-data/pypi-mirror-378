"""
Setup file for eox_core Django plugin.
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re

from setuptools import setup,find_packages

VERSION = "0.12.0"



setup(
    name="nextere-oauth",
    python_requires='>=3.10',
    version=VERSION,
    
    packages=find_packages(),
    include_package_data=True,
    entry_points={
       "lms.djangoapp": [
            "nextere_oauth = nextere_oauth.apps:LMSAuthConfig",
        ],
    }
)
