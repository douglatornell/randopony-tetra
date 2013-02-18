<%inherit file="page.mako"/>
<%namespace name="admin_btns" file="admin_buttons.mako"/>

<%block name="title">RandoPony::Admin::${populaire}</%block>

<h4>Populaire</h4>
<p>
  <a href="${request.route_url('populaire', short_name=populaire.short_name)}"
     target="_blank">
    ${populaire.event_name} (${populaire})
  </a>
</p>

<h4>Date and Start Time</h4>
<p>${"{:%a %d-%b-%Y %H:%M}".format(populaire.date_time)}</p>

<h4>Distance(s)</h4>
<p>${populaire.distance}</p>

<h4>Start Location</h4>
<p>
  ${populaire.start_locn}
  <br>
  <a href="${populaire.start_map_url}" target="_blank">Map</a>
</p>

<h4>Organizer Email(s)</h4>
<p>${populaire.organizer_email}</p>

<h4>Registration Closes</h4>
<p>${"{:%a %d-%b-%Y %H:%M}".format(populaire.registration_end)}</p>

<h4>Entry Form URL</h4>
<p>${populaire.entry_form_url}</p>

<h4>Google Drive Rider List Id</h4>
%if populaire.google_doc_id:
<p>
  <a href="${'https://spreadsheets.google.com/ccc?key={0}'.format(populaire.google_doc_id.split(':')[1])}"
     target="_blank">
    ${populaire.google_doc_id}
  </a>
</p>
%else:
<p class="text-warning">Not created yet!</p>
%endif

<h4>Riders Email Address List UUID</h4>
<p>
  <a href="${request.route_url('populaire.rider_emails',
                               short_name=populaire.short_name,
                               uuid=populaire.uuid)}"
     target="_blank">
    ${populaire.uuid}
  </a>
</p>

<div class="btn-toolbar">
  ${admin_btns.edit('populaires', populaire)}
  ${admin_btns.event_list('populaires')}
  <div class="btn-group dropup">
    <button class="btn btn-primary dropdown-toggle" data-toggle="dropdown">
      Admin Actions <span class="caret"></span>
    </button>
    <ul class="dropdown-menu">
      <li>${admin_btns.setup_123('populaires', populaire)}</li>
      <li>${admin_btns.create_rider_list('populaires', populaire)}</li>
      <li>${admin_btns.email_to_organizer('populaires', populaire)}</li>
      <li>${admin_btns.email_to_webmaster('populaires', populaire)}</li>
    </ul>
  </div>
</div>
