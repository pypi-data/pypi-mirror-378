# -*- coding: utf-8; -*-
"""
Rattail Demo data model
"""

# bring in all the normal stuff from Rattail
from rattail.db.model import *

# also bring in CORE-POS integration models
from rattail_corepos.db.model import *

# also bring in WooCommerce integration models
from rattail_woocommerce.db.model import *

# now bring in Demo-specific models
from .shopfoo import ShopfooProduct, ShopfooProductExport
