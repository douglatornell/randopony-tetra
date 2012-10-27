<%inherit file="../site.mako"/>

<%block name="title"><title>RandoPony::Admin</title></%block>

${next.body()}


<%def name="page_js()">
  ${self.jquery_js()}
  ${self.persona_js()}
</%def>

<%def name="jquery_js()">
  <script type="text/javascript"
          src="//ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.min.js">
  </script>
</%def>

<%def name="persona_js()">
  <script src="https://login.persona.org/include.js"></script>
  <script>${request.persona_js}</script>
</%def>
