<%inherit file="page.mako"/>

<%block name="title">
  RandoPony::About
</%block>

<%block name="subtitle">
  randopony ???
</%block>

<%def name="nav_tabs()">
  <li>
    <a href="${request.route_url('home')}" class="nav-tab">
      Home
    </a>
  </li>
  <li>
    <a href="http://randonneurs.bc.ca/" class="nav-tab">
      randonneurs.bc.ca
    </a>
  </li>
  <li>
    <a href="${request.route_url('organizer-info')}" class="nav-tab">
      Info for Event Organizers
    </a>
  </li>
  <li class="active">
    <a href="${request.route_url('about')}" class="nav-tab">
    What's up with the pony?
    </a>
  </li>
</%def>

<div id="tab4" class="tab-pane active">
  <p>
    The RandoPony site is written in <a href="http://python.org/">Python</a>.
    It was originally implemented using the Django web framework,
    and Django's unofficial mascot is a
    <a href="http://djangopony.com/">magical pony</a>,
    so... RandoPony.
  </p>

  <p>
    Besides, everybody (even a randonneur) wants a pony...
  </p>

  <p>
    Times change,
    technololy moves on,
    and the site is now implemented using the
    <a href="http://www.pylonsproject.org/">Pyramid</a> web framework,
    and the <a href="http://www.sqlalchemy.org/">SQLAlchemy</a> database toolkit,
    but it's still the RandoPony!
  </p>

  <p>
    RandoPony is open-source software.
    It's released under a
    <a href="http://www.opensource.org/licenses/bsd-license.php">
    New BSD License</a>.
    The source code is available at
    <a href="http://bitbucket.org/douglatornell/randopony-tetra/">
    http://bitbucket.org/douglatornell/randopony-tetra/</a>,
    and you can report issues using the
    <a href="http://bitbucket.org/douglatornell/randopony-tetra/issues/">
    Bitbucket issue tracker</a>,
    or by email to <a href="mailto:djl@douglatornell.ca">
    <kbd>djl@douglatornell.ca</kbd></a>
  </p>

  <p>
    This instance of RandoPony is hosted on Webfaction.
    If you're looking for powerful,
    reasonably priced hosting with very up to date software,
    and great support,
    you can use this
    <a href="http://www.webfaction.com?affiliate=dlatornell">
    affiliate link</a> to check them out.
  </p>
</div>
