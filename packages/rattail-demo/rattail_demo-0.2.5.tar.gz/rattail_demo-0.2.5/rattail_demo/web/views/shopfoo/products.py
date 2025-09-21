# -*- coding: utf-8; -*-
"""
Shopfoo product views
"""

from rattail_demo.db import model

from tailbone.views import MasterView


class ShopfooProductView(MasterView):
    """
    Shopfoo Product views
    """
    model_class = model.ShopfooProduct
    url_prefix = '/shopfoo/products'
    route_prefix = 'shopfoo.products'
    creatable = False
    editable = False
    bulk_deletable = True
    has_versions = True

    labels = {
        'upc': "UPC",
    }

    grid_columns = [
        'upc',
        'description',
        'price',
        'enabled',
    ]

    form_fields = [
        'product',
        'upc',
        'description',
        'price',
        'enabled',
    ]

    def configure_grid(self, g):
        super(ShopfooProductView, self).configure_grid(g)

        g.filters['upc'].default_active = True
        g.filters['upc'].default_verb = 'equal'

        g.filters['description'].default_active = True
        g.filters['description'].default_verb = 'contains'

        g.set_sort_defaults('upc')

        g.set_type('price', 'currency')

        g.set_link('upc')
        g.set_link('description')

    def grid_extra_class(self, product, i):
        if not product.enabled:
            return 'warning'

    def configure_form(self, f):
        super(ShopfooProductView, self).configure_form(f)

        f.set_renderer('product', self.render_product)
        f.set_type('price', 'currency')


def includeme(config):
    ShopfooProductView.defaults(config)
