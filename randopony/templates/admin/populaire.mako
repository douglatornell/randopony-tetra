<%inherit file="page.mako"/>

<%block name="title">RandoPony::Admin::${populaire}</%block>

%if request.session.peek_flash():
${self.flash(request.session.pop_flash())}
%endif

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

%if populaire.google_doc_id:
<h4>Google Rider List Id</h4>
<p>
  <a href="${'https://spreadsheets.google.com/ccc?key={0}'.format(populaire.google_doc_id.split(':')[1])}"
     target="_blank">
    ${populaire.google_doc_id}
  </a>
</p>
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
  <a href="${request.route_url('admin.populaires.edit', item=str(populaire))}"
     class="btn btn-info">
   <i class="icon-edit icon-white"></i>
   <span class="hidden-phone">Edit</span>
  </a>

  <a href="${request.route_url('admin.list', list='populaires')}"
     class="btn">
   <i class="icon-arrow-left"></i>
   <span class="hidden-phone">Populaire List</span>
  </a>

  <div class="btn-group dropup">
    <a href="#" class="btn btn-primary dropdown-toggle" data-toggle="dropdown">
      Admin Actions
      <span class="caret"></span>
    </a>
    <ul class="dropdown-menu">
      <li><a href="#" tabindex="-1">Setup 1-2-3</a></li>
      <li>
        <a href="${request.route_url('admin.populaires.create_rider_list',
                                     item=str(populaire))}"
           tabindex="-1">
           Copy Google Template
         </a>
       </li>
      <li><a href="#" tabindex="-1">Email Organizer(s)</a></li>
      <li><a href="#" tabindex="-1">Email Webmaster</a></li>
    </ul>
  </div>
</div>


<%def name="flash(data)">
  <div class="row">
    <div class="span4">
      <div class="alert alert-${data[0]} alert-block fade in">
        <a href="#" class="close" data-dismiss="alert">&times;</a>
        <h4 class="alert-heading">${data[0]}!</h4>
        ${data[1]}
      </div>
    </div>
  </div>
</%def>
