<%inherit file="../site.mako"/>

<%block name="title"><title>RandoPony::Admin</title></%block>

${next.body()}


<%block name="page_js">
  ${jquery_js()}
  ${persona_js()}
</%block>

<%block name="jquery_js">
  <script type="text/javascript"
          src="//ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.min.js">
  </script>
</%block>

<%block name="persona_js">
  <script src="https://login.persona.org/include.js"></script>
  <script>${request.persona_js}</script>
</%block>
