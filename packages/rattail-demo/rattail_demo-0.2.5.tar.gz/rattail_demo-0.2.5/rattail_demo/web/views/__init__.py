# -*- coding: utf-8; -*-
"""
Web views
"""

from tailbone.views import essentials


def includeme(config):

    # tailbone essentials
    essentials.defaults(config, **{
        'tailbone.views.upgrades': 'rattail_demo.web.views.upgrades',
    })

    # main table views
    config.include('tailbone.views.brands')
    config.include('tailbone.views.categories')
    config.include('tailbone.views.customers')
    config.include('tailbone.views.customergroups')
    config.include('tailbone.views.departments')
    config.include('tailbone.views.employees')
    config.include('tailbone.views.families')
    config.include('tailbone.views.members')
    config.include('tailbone.views.messages')
    config.include('rattail_demo.web.views.products')
    config.include('tailbone.views.reportcodes')
    config.include('tailbone.views.stores')
    config.include('tailbone.views.subdepartments')
    config.include('tailbone.views.tempmon')
    config.include('tailbone.views.vendors')
    config.include('tailbone.views.uoms')

    # purchasing / receiving
    config.include('tailbone_corepos.views.purchases')
    config.include('tailbone.views.purchases.credits')
    config.include('tailbone.views.purchasing')

    # core-pos views
    config.include('tailbone_corepos.views')
    config.include('tailbone_corepos.views.corepos')

    # shopfoo views
    config.include('rattail_demo.web.views.shopfoo')

    # woocommerce views
    config.include('tailbone_woocommerce.views')
    config.include('tailbone_woocommerce.views.woocommerce')

    # batch views
    config.include('tailbone.views.batch.handheld')
    config.include('tailbone.views.batch.inventory')
    config.include('tailbone.views.batch.importer')
    config.include('tailbone.views.batch.vendorcatalog')

    # trainwreck
    config.include('tailbone.views.trainwreck.defaults')
