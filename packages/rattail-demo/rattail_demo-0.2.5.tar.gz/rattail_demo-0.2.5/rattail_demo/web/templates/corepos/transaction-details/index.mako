## -*- coding: utf-8; -*-
<%inherit file="/master/index.mako" />

<%def name="context_menu_items()">
  ${parent.context_menu_items()}
  % if request.has_perm('{}.import_file'.format(permission_prefix)):
      <li>${h.link_to("Import {} from Square CSV".format(model_title_plural), url('{}.import_square'.format(route_prefix)))}</li>
  % endif
</%def>

${parent.body()}
