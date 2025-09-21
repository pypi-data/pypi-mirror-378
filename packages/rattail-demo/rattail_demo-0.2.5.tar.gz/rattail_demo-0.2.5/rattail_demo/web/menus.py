# -*- coding: utf-8; -*-
"""
Web Menus
"""

from tailbone import menus as base
from tailbone_corepos.menus import make_corepos_menu


class DemoMenuHandler(base.TailboneMenuHandler):
    """
    Demo menu handler
    """

    def make_menus(self, request, **kwargs):

        people_menu = self.make_people_menu(request)

        products_menu = self.make_products_menu(request)

        vendors_menu = self.make_vendors_menu(request)

        corepos_menu = make_corepos_menu(request)

        shopfoo_menu = {
            'title': "Shopfoo",
            'type': 'menu',
            'items': [
                {
                    'title': "Products",
                    'route': 'shopfoo.products',
                    'perm': 'shopfoo.products.list',
                },
                {
                    'title': "Product Exports",
                    'route': 'shopfoo.product_exports',
                    'perm': 'shopfoo.product_exports.list',
                },
                {'type': 'sep'},
                {
                    'title': "WooCommerce Products",
                    'route': 'woocommerce.products',
                    'perm': 'woocommerce.products.list',
                },
            ],
        }

        reports_menu = self.make_reports_menu(request, include_trainwreck=True)

        batch_menu = self.make_batches_menu(request)

        tempmon_menu = self.make_tempmon_menu(request)

        other_menu = {
            'title': "Other",
            'type': 'menu',
            'items': [
                {
                    'title': "Documentation",
                    'url': 'https://rattailproject.org/moin/RattailDemo',
                    'target': '_blank',
                },
                {
                    'title': "Source Code",
                    'url': 'https://forgejo.wuttaproject.org/rattail/rattail-demo',
                    'target': '_blank',
                },
                {
                    'title': "RattailProject.org",
                    'url': 'https://rattailproject.org',
                    'target': '_blank',
                },
                {'type': 'sep'},
                {
                    'title': "Generate New Project",
                    'route': 'generated_projects.create',
                    'perm': 'generated_projects.create',
                },
            ],
        }

        admin_menu = self.make_admin_menu(request, include_stores=True)

        menus = [
            people_menu,
            products_menu,
            vendors_menu,
            corepos_menu,
            shopfoo_menu,
            reports_menu,
            batch_menu,
            tempmon_menu,
            other_menu,
            admin_menu,
        ]

        return menus
