# -*- coding: utf-8; -*-
"""
Pyramid web application
"""

from tailbone import app
from tailbone_corepos.db import CoreOfficeSession, CoreTransSession


def main(global_config, **settings):
    """
    This function returns a Pyramid WSGI application.
    """
    # prefer demo templates over tailbone
    settings.setdefault('mako.directories', ['rattail_demo.web:templates',
                                             'tailbone_corepos:templates',
                                             'tailbone_woocommerce:templates',
                                             'tailbone:templates',])

    # for graceful handling of postgres restart
    settings.setdefault('retry.attempts', 2)

    # make config objects
    rattail_config = app.make_rattail_config(settings)
    pyramid_config = app.make_pyramid_config(settings)

    # configure database sessions
    CoreOfficeSession.configure(bind=rattail_config.corepos_engine)
    CoreTransSession.configure(bind=rattail_config.coretrans_engine)

    # bring in rest of rattail-demo
    pyramid_config.include('rattail_demo.web.static')
    pyramid_config.include('rattail_demo.web.subscribers')
    pyramid_config.include('rattail_demo.web.views')

    # for graceful handling of postgres restart
    pyramid_config.add_tween('tailbone.tweens.sqlerror_tween_factory',
                             under='pyramid_tm.tm_tween_factory')

    return pyramid_config.make_wsgi_app()


def asgi_main():
    """
    This function returns an ASGI application.
    """
    from tailbone.asgi import make_asgi_app

    return make_asgi_app(main)
