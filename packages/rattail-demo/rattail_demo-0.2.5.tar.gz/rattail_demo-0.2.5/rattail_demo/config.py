# -*- coding: utf-8; -*-
"""
Rattail Demo config extension
"""

from wuttjamaican.conf import WuttaConfigExtension


class DemoConfigExtension(WuttaConfigExtension):
    """
    Rattail Demo config extension
    """
    key = 'rattail-demo'

    def configure(self, config):

        config.setdefault('rattail', 'app_package', 'rattail_demo')

        # tell rattail where our stuff lives
        config.setdefault('rattail', 'model_spec', 'rattail_demo.db.model')
        config.setdefault('rattail.trainwreck', 'model', 'rattail.trainwreck.db.model.defaults')
        config.setdefault('tailbone.static_libcache.module', 'rattail_demo.web.static')

        # menus
        config.setdefault('rattail.web.menus.handler_spec', 'rattail_demo.web.menus:DemoMenuHandler')

        # default app handlers
        config.setdefault('rattail', 'products.handler', 'rattail_corepos.products:CoreProductsHandler')

        # default import handlers
        config.setdefault('rattail.importing', 'versions.handler', 'rattail_demo.importing.versions:FromRattailDemoToRattailDemoVersions')
        config.setdefault('rattail.importing', 'corepos_api.handler', 'rattail_demo.importing.corepos_api:FromCOREPOSToRattail')
