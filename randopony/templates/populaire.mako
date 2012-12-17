<%inherit file="page.mako"/>

<%block name="title">
  RandoPony::${populaire}
</%block>

<%block name="subtitle">
${populaire} ${"{:%d-%b-%Y}".format(populaire.date_time)}
</%block>

<div class="tab-pane active">
  <p>
    <h3>${populaire.event_name}</h3>
    <strong>Distance:</strong>
    ${populaire.distance}
  </p>
  <p>
    <strong>Start:</strong>
    ${"{:%a %d-%b-%Y at %H:%M}".format(populaire.date_time)}
  </p>
  <p>
    <strong>Start Location:</strong>
    ${populaire.start_locn}
    <br>
    <a href="${populaire.start_map_url}" target="_blank">Map</a>
  </p>

  <p>
    Nobody has pre-registered
    <br>
    <a class="btn btn-success" href="#">
      Be the first!
    </a>
  </p>

  <div class="img-container hidden-phone">
    <img src="${request.static_url('randopony:static/img/tandem_tuesday.jpg')}"
         alt="Bob and Alex enjoying a populaire on their tandem"
         class="filler-img">
    <div class="photo-credit muted pull-right">
      <em><small>Karen Smith</small></em>
    </div>
  </div>
</div>
