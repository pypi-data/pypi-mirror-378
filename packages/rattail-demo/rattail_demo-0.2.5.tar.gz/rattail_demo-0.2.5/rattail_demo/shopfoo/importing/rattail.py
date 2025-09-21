# -*- coding: utf-8; -*-
"""
Rattail -> Shopfoo importing
"""

from collections import OrderedDict

from rattail import importing

from rattail_demo.db import model
from rattail_demo.shopfoo import importing as shopfoo_importing
from rattail.shopfoo.importing.rattail import ProductImporterMixin


class FromRattailToShopfoo(importing.FromRattailHandler):
    """
    Rattail -> Shopfoo import handler
    """
    host_title = "Rattail"
    local_title = "Shopfoo"
    direction = 'export'

    def get_importers(self):
        importers = OrderedDict()
        importers['Product'] = ProductImporter
        return importers


class FromRattail(importing.FromSQLAlchemy):
    """
    Base class for Shopfoo -> Rattail importers
    """


class ProductImporter(ProductImporterMixin, FromRattail, shopfoo_importing.model.ProductImporter):
    """
    Product data importer
    """
    host_model_class = model.ShopfooProduct
    supported_fields = [
        'uuid',
        'product_uuid',
        'upc',
        'description',
        'price',
        'enabled',
    ]

    def query(self):
        return self.host_session.query(model.ShopfooProduct)\
                                .order_by(model.ShopfooProduct.upc)

    def normalize_host_object(self, product):

        # copy all values "as-is" from our cache record
        data = dict([(field, getattr(product, field))
                     for field in self.fields])

        # TODO: is it ever a good idea to set this flag?  doing so will mean
        # the record is *not* included in CSV output file
        # data['_deleted_'] = product.deleted_from_shopfoo

        return data
