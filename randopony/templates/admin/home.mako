<%inherit file="page.mako"/>

<ul class="unstyled admin-list">
  <li><a href="${request.route_url('admin.brevets')}">Brevets</a></li>
  <li><a href="${request.route_url('admin.club_events')}">Club Events</a></li>
  <li><a href="${request.route_url('admin.populaires')}">Populaires</a></li>
  <li><a href="${request.route_url('admin.wranglers')}">Pony Wranglers</a></li>
</ul>