<%inherit file="page.mako"/>

<ul class="unstyled admin-list">
  <li>
    <a href="${request.route_url('admin.list', list='brevets')}">
      Brevets
    </a>
  </li>
  <li>
    <a href="${request.route_url('admin.list', list='club_events')}">
      Club Events
    </a>
  </li>
  <li>
    <a href="${request.route_url('admin.list', list='populaires')}">
      Populaires
    </a>
  </li>
  <li>
    <a href="${request.route_url('admin.list', list='wranglers')}">
      Pony Wranglers (aka Administrators)
    </a>
  </li>
</ul>