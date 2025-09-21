# -*- coding: utf-8; -*-
"""
Shopfoo model importers
"""

from rattail_demo.db import model
from rattail.importing.exporters import ToCSV
from rattail.shopfoo.importing.model import ProductImporterMixin


class ToShopfoo(ToCSV):
    pass


class ProductImporter(ProductImporterMixin, ToShopfoo):
    """
    Shopfoo product data importer
    """
    key = 'uuid'
    simple_fields = [
        'uuid',
        'product_uuid',
        'upc',
        'description',
        'price',
        'enabled',
    ]
    export_model_class = model.ShopfooProductExport
