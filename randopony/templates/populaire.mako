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

  %if len(populaire.riders) == 0:
  <p>
    Nobody has pre-registered
    <br>
    <a class="btn btn-success"
       href="${request.route_url('populaire.entry',
                                 short_name=populaire.short_name)}">
      Be the first!
    </a>
  </p>
  %else:
  <p>
    <a class="btn btn-success"
       href="${request.route_url('populaire.entry',
                                 short_name=populaire.short_name)}">
      Register
    </a>
  </p>
  <table class="table table-striped">
    <thead>
      <tr>
        <th colspan="2">
          ${len(populaire.riders)} Pre-registered
          %if len(populaire.riders) > 1:
          Riders
          %else:
          Rider
          %endif
        </th>
      </tr>
    </thead>
    <tbody>
      %for rider in populaire.riders:
      <tr>
        <td>${rider.full_name}</td>
        %if ',' in populaire.distance:
        <td>${rider.distance} km</td>
        %endif
      </tr>
      %endfor
    </tbody>
  </table>
  %endif

  %if len(populaire.riders) < 15:
  <div class="img-container hidden-phone">
    <img src="${request.static_url('randopony:static/img/tandem_tuesday.jpg')}"
         alt="Bob and Alex enjoying a populaire on their tandem"
         class="filler-img">
    <div class="photo-credit muted pull-right">
      <em><small>Karen Smith</small></em>
    </div>
  </div>
  %endif
</div>
