<%inherit file="page.mako"/>

<%block name="title">
  RandoPony::Coming Soon
</%block>

<%block name="subtitle">
  coming soon...
</%block>

<div class="tab-pane active">
  <p>
    There's no page yet for the ${maybe_brevet} brevet.
  </p>
  <p>
    It'll be delivered shortly after the brevet organizer requests it.
  </p>

  <div class="img-container hidden-phone">
    <img src="${request.static_url('randopony:static/img/pregnant_ponies.jpg')}"
         alt="Coming soon..."
         class="filler-img">
    <div class="photo-credit muted pull-right">
      <em><small>
        <a href="http://www.flickr.com/people/thomissen/">Joe Thomissen</a>
      </small></em>
    </div>
  </div>
</div>
