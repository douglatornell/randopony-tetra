<%inherit file="page.mako"/>

<%block name="title">
  RandoPony::${brevet}
</%block>

<%block name="subtitle">
${brevet}
</%block>

<div class="tab-pane active">
  <p>
    <h3>${REGIONS[brevet.region]} ${brevet.distance}</h3>
    <strong>Route:</strong>
    ${brevet.route_name}
  </p>
  <p>
    <strong>Start:</strong>
    ${"{:%a %d-%b-%Y at %H:%M}".format(brevet.date_time)}
  </p>
  <p>
    <strong>Start Location:</strong>
    ${brevet.start_locn}
    <br>
    <a href="${brevet.start_map_url}" target="_blank">Map</a>
  </p>

  %if registration_closed and not event_started:
  ${self.registration_closed_msg()}
  %endif

  %if request.session.peek_flash():
    %if request.session.peek_flash()[0] == 'success':
    ${self.confirmation(request.session.pop_flash())}
    %elif request.session.peek_flash()[0] == 'duplicate':
    ${self.duplicate(request.session.pop_flash())}
    %endif
  %endif

  %if len(brevet.riders) == 0:
    <p>
      Nobody has pre-registered
    </p>
    %if not registration_closed:
    <p class="register-btn">
      <a class="btn btn-success"
         href="${request.route_url('brevet.entry',
                                   region=brevet.region,
                                   distance=brevet.distance,
                                   date=brevet.date_time.strftime('%d%b%Y'))}">
        Be the first!
      </a>
    </p>
    %endif
  %else:
    %if not registration_closed:
    <p class="register-btn">
      <a class="btn btn-success"
         href="${request.route_url('brevet.entry',
                                   region=brevet.region,
                                   distance=brevet.distance,
                                   date=brevet.date_time.strftime('%d%b%Y'))}">
        Register
      </a>
    </p>
    %endif

    <table class="table table-striped">
      <thead>
        <tr>
        <th colspan="2">
          ${len(brevet.riders)} Pre-registered
          %if len(brevet.riders) > 1:
          Riders
          %else:
          Rider
          %endif
        </th>
        </tr>
      </thead>
    <tbody>
      %for rider in brevet.riders:
      <tr>
        %if rider.bike_type == 'other':
        <td>${rider.full_name} riding something indescribable</td>
        %else:
        <td>${rider.full_name} riding a ${rider.bike_type}</td>
        %endif
      </tr>
      %endfor
    </tbody>
    </table>
  %endif

  %if len(brevet.riders) < 15:
  <div class="img-container hidden-phone">
    <img src="${request.static_url('randopony:static/img/BrevetPeloton.jpg')}"
         alt="Brevet peloton rolling out"
         class="filler-img">
    <div class="photo-credit muted pull-right">
      <em><small>Susan Allen</small></em>
    </div>
  </div>
  %endif
</div>


<%def name="registration_closed_msg()">
<div class="row">
  <div class="span6 notice">
    <p>
      Pre-registration for this brevet is closed.
      But you can still print out the <a href="${entry_form_url}"
      title="Event Waiver Form">event waiver form</a> from the club web site,
      read it carefully,
      fill it out,
      bring it with you to the start,
      and register for the event there.
    </p>
    <p>
      See you on the road!
    </p>
  </div>
</div>
</%def>


<%def name="confirmation(notice_data)">
<%
  email = notice_data[1]
  member_status = notice_data[2]
  membership_link = notice_data[3]
%>
<div class="row">
  <div class="span6 alert alert-success alert-block fade in">
    <span class="close" data-dismiss="alert">&times;</span>
    <h4 class="alert-heading">Yay!</h4>
    <p>
      You have pre-registered for this brevet.
      Your name should be on the list below.
    </p>
    <p>
      A confirmation email has been sent to you at
      <kbd>${email}</kbd>
      and to the brevet organizer(s).
    </p>
    %if member_status is None:
    <p>
      Your name couldn't be found in the club database.
      You need to be a member of the BC Randonneurs Club to ride this brevet.
      Please join at
      <a href="${membership_link}" title="Club Membership Page">
        ${membership_link}
      </a>
    </p>
    %elif not member_status:
    <p>
      Your BC Randonneurs club membership has expired.
      Please renew it at
      <a href="${membership_link}" title="Club Membership Page">
        ${membership_link}
      </a>
    </p>
    %endif
    <p>
      You can print out the
      <a href="${entry_form_url}" title="Event Waiver Form">
        event waiver form
      </a>
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


<%def name="duplicate(notice_data)">
<%
  name = notice_data[1]
  email = notice_data[2]
%>
<div class="row">
  <div class="span6 alert alert-danger alert-block fade in">
    <span class="close" data-dismiss="alert">&times;</span>
    <h4 class="alert-heading">Hmm...</h4>
    <p>
      Someone using the name ${name} and the email address
      <kbd>${email}</kbd> has already pre-registered for this brevet.
      Are you sure that you are registering for the event you intended to?
    </p>
    <p>
      If you are trying to change your email address by re-registering,
      please contact the event organizer.
      If you are trying to change the comment you embedded in your name,
      sorry,
      you can't do that.
    </p>
  </div>
</div>
</%def>
