# -*- coding: utf-8; -*-
"""
Database schema extensions for Shopfoo integration
"""

import sqlalchemy as sa

from rattail.db import model
from rattail.db.model.shopfoo import ShopfooProductBase, ShopfooProductExportBase


class ShopfooProduct(ShopfooProductBase, model.Base):
    """
    Shopfoo-specific product cache table.  Each record in this table *should*
    match exactly, what is in the actual "Shopfoo" system (even though that's
    made-up in this case).
    """
    __tablename__ = 'demo_shopfoo_product'
    __versioned__ = {}

    upc = sa.Column(sa.String(length=14), nullable=True)

    description = sa.Column(sa.String(length=255), nullable=True)

    price = sa.Column(sa.Numeric(precision=13, scale=2), nullable=True)

    enabled = sa.Column(sa.Boolean(), nullable=True)

    def __str__(self):
        return self.description or self.upc or ""


class ShopfooProductExport(ShopfooProductExportBase, model.Base):
    """
    Shopfoo product exports
    """
    __tablename__ = 'demo_shopfoo_product_export'
