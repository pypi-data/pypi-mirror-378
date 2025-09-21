# -*- coding: utf-8; -*-
"""
Rattail Demo -> Rattail Demo "self" data import
"""

from collections import OrderedDict

from rattail.importing.local import FromRattailSelfToRattail, FromRattailSelf
from rattail.importing.shopfoo import ShopfooProductImporterMixin
from rattail_demo import importing as rattail_demo_importing


class FromRattailDemoToSelf(FromRattailSelfToRattail):
    """
    Handler for Rattail Demo -> Rattail Demo ("self") imports
    """

    def get_importers(self):
        importers = OrderedDict()
        importers['ShopfooProduct'] = ShopfooProductImporter
        return importers


class ShopfooProductImporter(ShopfooProductImporterMixin, FromRattailSelf, rattail_demo_importing.model.ShopfooProductImporter):
    """
    Product -> ShopfooProduct
    """
    supported_fields = [
        'uuid',
        'product_uuid',
        'upc',
        'description',
        'price',
        'enabled',
    ]

    def normalize_base_product_data(self, product):

        price = None
        if product.regular_price:
            price = product.regular_price.price

        return {
            'product_uuid': product.uuid,
            'upc': str(product.upc or '') or None,
            'description': product.full_description,
            'price': price,
            'enabled': True,    # will maybe unset this in mark_unwanted()
        }

    def product_is_unwanted(self, product, data):
        if super(ShopfooProductImporter, self).product_is_unwanted(product, data):
            return True
        if not data['price']:   # let's say this is a required field for Shopfoo
            return True
        return False

    def mark_unwanted(self, product, data):
        data = super(ShopfooProductImporter, self).mark_unwanted(product, data)
        data['enabled'] = False
        return data
