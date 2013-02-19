<%inherit file="page.mako"/>
<%namespace name="admin_btns" file="admin_buttons.mako"/>

<%block name="title">RandoPony::Admin::${brevet}</%block>

<h4>Region, Distance, and Date</h4>
<p>
  <a href="${request.route_url('brevet',
                               region=brevet.region,
                               distance=brevet.distance,
                               date=brevet.date_time.strftime('%d%b%Y'))}"
     target="_blank">
    ${brevet}
  </a>
</p>

<h4>Start Time</h4>
<p>${"{:%H:%M}".format(brevet.date_time)}</p>

<h4>Route Name</h4>
<p>${brevet.route_name}</p>

<h4>Start Location</h4>
<p>
  ${brevet.start_locn}
  <br>
  <a href="${brevet.start_map_url}" target="_blank">Map</a>
</p>

<h4>Organizer Email(s)</h4>
<p>${brevet.organizer_email}</p>

<h4>Registration Closes</h4>
<p>${"{:%d-%b-%Y %H:%M}".format(brevet.registration_end)}</p>

%if brevet.info_question:
<h4>Info Question</h4>
<p>${brevet.info_question}</p>
%endif

<h4>Google Drive Rider List Id</h4>
%if brevet.google_doc_id:
<p>
  <a href="${'https://spreadsheets.google.com/ccc?key={0}'.format(brevet.google_doc_id.split(':')[1])}"
     target="_blank">
    ${brevet.google_doc_id}
  </a>
</p>
%else:
<p class="text-warning">Not created yet!</p>
%endif

<h4>Riders Email Address List UUID</h4>
<p>
  <a href="${request.route_url('brevet.entry',
                               region=brevet.region,
                               distance=brevet.distance,
                               date=brevet.date_time.strftime('%d%b%Y'))}
                               uuid=brevet.uuid)}"
     target="_blank">
    ${brevet.uuid}
  </a>
</p>

<div class="btn-toolbar">
  ${admin_btns.edit('brevets', brevet)}
  ${admin_btns.event_list('brevets')}
  <div class="btn-group dropup">
    <button class="btn btn-primary dropdown-toggle" data-toggle="dropdown">
      Admin Actions <span class="caret"></span>
    </button>
    <ul class="dropdown-menu">
      <li>${admin_btns.setup_123('brevets', brevet)}</li>
      <li>${admin_btns.create_rider_list('brevets', brevet)}</li>
      <li>${admin_btns.email_to_organizer('brevets', brevet)}</li>
      <li>${admin_btns.email_to_webmaster('brevets', brevet)}</li>
    </ul>
  </div>
</div>
