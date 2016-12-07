<%inherit file="../site.mako"/>

<%block name="title">RandoPony::Admin</%block>

<%block name="page_css">
  <link
  href="${request.static_url('randopony:static/css/admin.css')}"
  rel="stylesheet">
  <%block name="view_css"></%block>
</%block>

<%block name="page_js">
  <%block name="view_js"></%block>
</%block>

<div class="container">
  <div class="navbar navbar-inverse">
    <div class="navbar-inner">
      <a href="${request.route_url('admin.home')}" class="brand">
        RandoPony ${version} Admin
      </a>
      %if request.authenticated_userid:
      <ul class="nav pull-right">
        <li><button class="btn btn-default" onclick="location.href='${request.route_url("admin.logout")}'">Logout</button></li>
      </ul>
      %endif
    </div>
  </div>
  %if request.session.peek_flash():
  ${self.flash(request.session.pop_flash())}
  %endif

  ${next.body()}
</div>


<%def name="flash(data)">
  <div class="row">
    <div class="span4">
      <div class="alert alert-${data[0]} alert-block fade in">
        <span class="close" data-dismiss="alert">&times;</span>
        <h4 class="alert-heading">${data[0]}!</h4>
        %for line in data[1:]:
        ${line}<br>
        %endfor
      </div>
    </div>
  </div>
</%def>
