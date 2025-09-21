## -*- coding: utf-8; -*-
<%inherit file="tailbone:templates/login.mako" />

<%def name="extra_styles()">
  ${parent.extra_styles()}
  <style type="text/css">
    .tips {
        margin-top: 2em;
        text-align: center;
    }
  </style>
</%def>

<%def name="page_content()">
  ${parent.page_content()}
  <p class="tips">
    Login with <strong>chuck / admin</strong> for full demo access
  </p>
</%def>


${parent.body()}
