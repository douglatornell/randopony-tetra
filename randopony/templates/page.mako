<%inherit file="site.mako"/>

<%block name="title">RandoPony</%block>

<%block name="page_css">
  <link
  href="${request.static_url('randopony:static/css/site.css')}"
  rel="stylesheet">
  <%block name="view_css"></%block>
</%block>

<%block name="page_js">
  <%block name="view_js"></%block>
</%block>

<div class="container">

  <div class="navbar">
    <div class="navbar-inner">
      <div class="container navbar-wrapper">
        <a href="#" class="brand">
          <h1>bc randonneurs</h1>
          <h3><%block name="subtitle"></%block></h3>
        </a>
        <a class="btn btn-navbar visible-phone"
           data-toggle="collapse" data-target=".nav-collapse">
          <span class="icon-bar"></span>
          <span class="icon-bar"></span>
          <span class="icon-bar"></span>
        </a>
        <div class="nav-collapse collapse visible-phone">
          <ul class="nav">
            ${next.nav_tabs()}
          </ul>
        </div>
      </div>
    </div>
  </div>

  <div class="tabbable tabs-right">
    <ul class="nav nav-tabs hidden-phone">
      ${next.nav_tabs()}
    </ul>

  <div class="tab-content">
    ${next.body()}
  </div>

    <div class="footer">
      <p>
        &copy; 2013 douglatornell.ca
      </p>
      <p>
        <a href="http://www.pylonsproject.org/" title="Not Built by Aliens">
          <img src="${request.static_url('randopony:static/img/pyramid-small.png')}"
               alt="pyramid powered">
        </a>
      </p>
  </div>
</div>
