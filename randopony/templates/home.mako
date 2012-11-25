<%inherit file="page.mako"/>

<%block name="title">
  RandoPony
</%block>

<%block name="subtitle">
  event pre-registration
</%block>

<div class="tab-pane active">
  <p>
    Welcome to the pre-registration site for the BC Randonneurs Cycling
    Club brevets,
    populaires,
    and other events.
  </p>
  <p>
    This site provides a pre-registration service for events that simply lets
    the organizer know that you are intending to participate.
    We collect your name and email address so that we can confirm your
    pre-registration to you and the organizer by email.
  </p>
  <p>
    This is <em>not</em> a credit card payment site,
    so you'll need to bring cash or a cheque with you to the event to pay for
    the your participation.
  </p>
  <p>
    If you are an event organizer and would like set up pre-registration
    for your event,
    please read the <a href="${request.route_url('organizer-info')}">Info
    for Event Organizers</a> page.
  </p>

  <div class="img-container hidden-phone">
    <img src="${request.static_url('randopony:static/img/HomeClimb.jpg')}"
         alt="BC Randonneurs brevets, populaires, and events"
         class="filler-img">
    <div class="photo-credit muted pull-right">
      <em><small>Nobo Yonemitsu</small></em>
    </div>
  </div>
</div>
