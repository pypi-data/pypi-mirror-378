# -*- coding: utf-8; -*-
"""
Static assets
"""

from fanstatic import Library, Resource


# libcache
libcache = Library('rattail_demo_libcache', 'libcache')
bb_vue_js = Resource(libcache, 'vue.esm-browser-3.4.31.prod.js')
bb_oruga_js = Resource(libcache, 'oruga-0.8.12.js')
bb_oruga_bulma_js = Resource(libcache, 'oruga-bulma-0.3.0.js')
bb_oruga_bulma_css = Resource(libcache, 'oruga-bulma-0.3.0.css')
bb_fontawesome_svg_core_js = Resource(libcache, 'fontawesome-svg-core-6.5.2.js')
bb_free_solid_svg_icons_js = Resource(libcache, 'free-solid-svg-icons-6.5.2.js')
bb_vue_fontawesome_js = Resource(libcache, 'vue-fontawesome-3.0.6.index.es.js')


def includeme(config):
    config.include('tailbone.static')
    config.add_static_view('rattail_demo', 'rattail_demo.web:static', cache_max_age=3600)
