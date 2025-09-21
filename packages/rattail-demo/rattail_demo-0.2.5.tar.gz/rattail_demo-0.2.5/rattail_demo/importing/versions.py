# -*- coding: utf-8; -*-
"""
Rattail Demo -> Rattail Demo "versions" data import
"""

from rattail_demo.db import model
from rattail.importing import versions as base
from rattail_corepos.importing.versions import CoreposVersionMixin
from rattail_woocommerce.importing.versions import WooVersionMixin


class FromRattailDemoToRattailDemoVersions(base.FromRattailToRattailVersions,
                                           CoreposVersionMixin,
                                           WooVersionMixin):
    """
    Handler for Rattail Demo -> Rattail Demo "versions" data import
    """

    def get_importers(self):
        importers = super(FromRattailDemoToRattailDemoVersions, self).get_importers()
        importers = self.add_corepos_importers(importers)
        importers = self.add_woocommerce_importers(importers)
        importers['ShopfooProduct'] = ShopfooProductImporter
        return importers


class ShopfooProductImporter(base.VersionImporter):
    host_model_class = model.ShopfooProduct
