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

  %if request.session.peek_flash():
  ${self.confirmation(request.session.pop_flash())}
  %endif

  %if len(populaire.riders) == 0:
    <p>
      Nobody has pre-registered
    </p>
    <p>
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


<%def name="confirmation(notice_data)">
<div class="row">
  <div class="span6 notice">
    <p>
      You have pre-registered for this populaire.
      Cool!
      Your name should be on the list below.
    </p>
    <p>
      A confirmation email has been sent to you at
      <kbd>${notice_data[0]}</kbd>
      and to the populaire organizer(s).
    </p>
    <p>
      You can print out the
      <a href="${notice_data[1]}">event waiver form</a>
      from the club web site,
      read it carefully,
      fill it out,
      and bring it with you to the start to save time and make the organizers
      like you even more.
    </p>
    <p>
      Have a great ride!
    </p>
  </div>
</div>
</%def>
