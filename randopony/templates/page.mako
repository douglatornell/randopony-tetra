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
            ${self.nav_tabs(active_tab)}
          </ul>
        </div>
      </div>
    </div>
  </div>

  <div class="tabbable tabs-right">
    <ul class="nav nav-tabs hidden-phone">
      ${self.nav_tabs(active_tab)}
    </ul>

  <div class="tab-content">
    ${next.body()}
  </div>

    <div class="footer">
      <p>
        &copy; 2013
        <a href="http://douglatornell.ca" class="footer">douglatornell.ca</a>
      </p>
      <p>
        <a href="http://www.pylonsproject.org/" title="Not Built by Aliens">
          <img src="${request.static_url('randopony:static/img/pyramid-small.png')}"
               alt="pyramid powered">
        </a>
      </p>
  </div>
</div>

<%def name="nav_tabs(active_tab)">
  <li id="home">
    <a href="${request.route_url('home')}" class="nav-tab">
      Home
    </a>
  </li>
  %if brevets.count() > 0:
  <li id="brevets">
    <a href="${request.route_url('brevet-list')}" class="nav-tab">
      Brevets
    </a>
  </li>
  %endif
  <li id="club-site">
    <a href="http://randonneurs.bc.ca/" class="nav-tab">
      randonneurs.bc.ca
    </a>
  </li>
  <li id="organizer-info">
    <a href="${request.route_url('organizer-info')}" class="nav-tab">
      Info for Event Organizers
    </a>
  </li>
  <li id="about">
    <a href="${request.route_url('about')}" class="nav-tab">
    What's up with the pony?
    </a>
  </li>

  <script>
    $(document).ready(function(){
      $("li#${active_tab}").addClass("active");
    });
  </script>
</%def>
