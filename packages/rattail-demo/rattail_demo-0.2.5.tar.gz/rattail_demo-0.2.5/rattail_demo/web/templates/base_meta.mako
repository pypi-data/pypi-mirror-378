## -*- coding: utf-8; -*-
<%inherit file="tailbone:templates/base_meta.mako" />

<%def name="header_logo()">
  ${h.image(request.static_url('tailbone:static/img/rattail.ico'), "Header Logo", style="height: 55px;")}
</%def>
