# -*- coding: utf-8; -*-
"""
Shopfoo views
"""


def includeme(config):
    config.include('rattail_demo.web.views.shopfoo.products')
    config.include('rattail_demo.web.views.shopfoo.exports')
