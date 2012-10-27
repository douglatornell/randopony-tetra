<%inherit file="../site.mako"/>

<%block name="title"><title>RandoPony::Admin</title></%block>

${next.body()}

<%block name="page_js">
  ${persona_js()}
</%block>


<%block name="persona_js">
  <script src="https://login.persona.org/include.js"></script>
  <script>${request.persona_js}</script>
</%block>
