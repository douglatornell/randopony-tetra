## Admin page buttons

<%def name="edit(event_type, event)">
  <a href="${request.route_url('admin.{}.edit'.format(event_type),
                               item=str(event))}"
     class="btn btn-info">
   <i class="icon-edit icon-white"></i>
   <span class="hidden-phone">Edit</span>
  </a>
</%def>


<%def name="event_list(event_type)">
  <a href="${request.route_url('admin.list', list=event_type)}"
     class="btn">
   <i class="icon-arrow-left"></i>
   <span class="hidden-phone">${event_type.title()} List</span>
  </a>
</%def>


<%def name="setup_123(event_type, event)">
  <a href="${request.route_url('admin.{}.setup_123'.format(event_type),
                               item=str(event))}"
     tabindex="-1">
     Setup 1-2-3
  </a>
</%def>


<%def name="create_rider_list(event_type, event)">
  <a href="${request.route_url('admin.{}.create_rider_list'.format(event_type),
                               item=str(event))}"
     tabindex="-1">
     Create Rider List
   </a>
</%def>


<%def name="email_to_organizer(event_type, event)">
  <a href="${request.route_url('admin.{}.email_to_organizer'.format(event_type),
                               item=str(event))}"
     tabindex="-1">
     Email Organizer(s)
   </a>
</%def>


<%def name="email_to_webmaster(event_type, event)">
  <a href="${request.route_url('admin.{}.email_to_webmaster'.format(event_type),
                               item=str(event))}"
     tabindex="-1">
     Email Webmaster
  </a>
</%def>
