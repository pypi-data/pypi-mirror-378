# -*- coding: utf-8; -*-
"""
Rattail Demo model importers
"""

from rattail.importing.model import ToRattail
from rattail_demo.db import model


##############################
# custom models
##############################

class ShopfooProductImporter(ToRattail):
    """
    Importer for ShopfooProduct data
    """
    model_class = model.ShopfooProduct
