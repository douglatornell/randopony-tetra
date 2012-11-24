<%inherit file="page.mako"/>

<%block name="title">RandoPony::Admin::${brevet}</%block>

<h4>Region, Distance, and Date</h4>
<p>${brevet}</p>

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

%if brevet.google_doc_id:
<h4>Google Rider List Id</h4>
<p>${brevet.google_doc_id}</p>
%endif

<h4>Riders Email Addresses</h4>
<p></p>

<div class="btn-toolbar">
  <a href="${request.route_url('admin.brevets.edit', item=str(brevet))}"
     class="btn btn-info">
   <i class="icon-edit icon-white"></i>
   <span class="hidden-phone">Edit</span>
  </a>

  <a href="${request.route_url('admin.list', list='brevets')}"
     class="btn">
   <i class="icon-arrow-left"></i>
   <span class="hidden-phone">Brevet List</span>
  </a>

  <div class="btn-group dropup">
    <a href="#" class="btn btn-primary dropdown-toggle" data-toggle="dropdown">
      Admin Actions
      <span class="caret"></span>
    </a>
    <ul class="dropdown-menu">
      <li><a href="#" tabindex="-1">Setup 1-2-3</a></li>
      <li><a href="#" tabindex="-1">Copy Google Template</a></li>
      <li><a href="#" tabindex="-1">Email Organizer(s)</a></li>
      <li><a href="#" tabindex="-1">Email Webmaster</a></li>
    </ul>
  </div>
</div>
