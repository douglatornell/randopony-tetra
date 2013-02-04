<%inherit file="../site.mako"/>

<%block name="title">RandoPony::Admin</%block>

<%block name="page_css">
  <link
  href="${request.static_url('randopony:static/css/admin.css')}"
  rel="stylesheet">
  <%block name="view_css"></%block>
</%block>

<%block name="page_js">
  <script src="https://login.persona.org/include.js"></script>
  <script>${request.persona_js}</script>
  <%block name="view_js"></%block>
</%block>

<div class="container">
  <div class="navbar navbar-inverse">
    <div class="navbar-inner">
      <a href="${request.route_url('admin.home')}" class="brand">
        RandoPony ${version} Admin
      </a>
      %if logout_btn:
      <ul class="nav pull-right">
        <li><button id="signout" class="btn">Logout</button></li>
      </ul>
      %endif
    </div>
  </div>
  ${next.body()}
</div>
