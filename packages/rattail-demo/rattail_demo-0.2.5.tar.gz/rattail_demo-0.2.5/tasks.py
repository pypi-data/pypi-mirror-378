# -*- coding: utf-8; -*-
"""
Tasks for rattail-demo
"""

import os
import shutil

from invoke import task


@task
def release(c):
    """
    Release a new version of 'rattail-demo'
    """
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('rattail_demo.egg-info'):
        shutil.rmtree('rattail_demo.egg-info')

    c.run('python -m build --sdist')
    c.run('twine upload dist/*')
