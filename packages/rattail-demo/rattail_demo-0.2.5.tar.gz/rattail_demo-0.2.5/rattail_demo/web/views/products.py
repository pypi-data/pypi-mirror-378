# -*- coding: utf-8; -*-
"""
Product views
"""

from webhelpers2.html import tags

from tailbone.views import products as base


class ProductView(base.ProductView):
    """
    Product overrides for online demo
    """

    def get_xref_links(self, product):
        links = super(ProductView, self).get_xref_links(product)

        if product.demo_shopfoo_product:
            url = self.request.route_url('shopfoo.products.view',
                                         uuid=product.demo_shopfoo_product.uuid)
            links.append(tags.link_to("View Shopfoo Product", url))

        return links


def includeme(config):
    base.defaults(config, **{'ProductView': ProductView})
