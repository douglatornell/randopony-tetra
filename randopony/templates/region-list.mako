<%inherit file="page.mako"/>

<%block name="title">
  RandoPony::Brevets
</%block>

<%block name="subtitle">
  brevet pre-registration
</%block>

<div class="tab-pane active">
  <p>
    Please choose the link for the region where the brevet that you want to
    pre-register for is:
  </p>
  <ul class="nav nav-pills">
    %for region in sorted(regions, key=regions.get):
    %if region_brevets[region].count() > 0:
    <li>
      <a href="${request.route_url('brevet.list', region=region)}">
        ${regions[region]}
      </a>
    </li>
    %endif
    %endfor
  </ul>
  <p>
    This site provides a pre-registration service for brevets that simply lets
    the organizer know that you are intending to ride.
    We collect your name and email address so that we can confirm your
    pre-registration to you and the organizer by email.
  </p>
  <p>
    The brevet pages also provide a link to the event waiver form that you can
    print,
    read carefully,
    complete and sign,
    and bring to the start with you to save time and brain-power in the early
    dawn hours.
    You must be a member of the BC Randonneurs club to ride a brevet.
    If you're not already a member,
    there is also a link to the club membership form that you can also print,
    read carefully,
    complete and sign,
    and bring with you.
  </p>
  <p>
    This is <em>not</em> a credit card payment site,
    so you'll need to bring $15 (cash or a cheque) with you to the start to
    pay for your entry
    (and another $10 if you'll be paying for membership at the start too).
  </p>
  <p>
    Questions about the brevets should be directed to the riderorganizers.
    Feedback about this site can be sent to
    <a href="mailto:${admin_email}">${admin_email}</a>.
  </p>
  <p>
    If you are an brevet organizer and would like set up pre-registration
    for your event,
    please read the <a href="${request.route_url('organizer-info')}">Info
    for Event Organizers</a> page.
  </p>
</div>
