# -*- coding: utf-8; -*-
"""
Rattail Demo web API
"""

from tailbone import webapi as base


def main(global_config, **settings):
    """
    This function returns a Pyramid WSGI application.
    """
    return base.main(global_config, **settings)
