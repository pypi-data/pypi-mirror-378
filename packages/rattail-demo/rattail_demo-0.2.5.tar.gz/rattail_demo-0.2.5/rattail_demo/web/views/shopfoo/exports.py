# -*- coding: utf-8 -*-
"""
Views for Shopfoo product exports
"""

from rattail_demo.db import model

from tailbone.views.exports import ExportMasterView


class ShopfooProductExportView(ExportMasterView):
    """
    Master view for Shopfoo product exports.
    """
    model_class = model.ShopfooProductExport
    route_prefix = 'shopfoo.product_exports'
    url_prefix = '/shopfoo/exports/product'
    downloadable = True
    editable = True
    delete_export_files = True

    grid_columns = [
        'id',
        'created',
        'created_by',
        'filename',
        'record_count',
        'uploaded',
    ]

    form_fields = [
        'id',
        'created',
        'created_by',
        'record_count',
        'filename',
        'uploaded',
    ]


def includeme(config):
    ShopfooProductExportView.defaults(config)
