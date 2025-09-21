# -*- coding: utf-8 -*-
"""
Pyramid Event Subscribers
"""

from __future__ import unicode_literals, absolute_import


def includeme(config):
    config.include('tailbone.subscribers')
    config.add_subscriber('tailbone.subscribers.add_inbox_count', 'pyramid.events.BeforeRender')
