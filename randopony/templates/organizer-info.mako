<%inherit file="page.mako"/>

<%block name="title">
  RandoPony::Event Organizer Info
</%block>

<%block name="subtitle">
  getting the randopony to help with your brevet
</%block>

<%def name="nav_tabs()">
  <li>
    <a href="${request.route_url('home')}" class="nav-tab">
      Home
    </a>
  </li>
  <li>
    <a href="http://randonneurs.bc.ca/" class="nav-tab">
      randonneurs.bc.ca
    </a>
  </li>
  <li class="active">
    <a href="${request.route_url('organizer-info')}" class="nav-tab">
      Info for Event Organizers
    </a>
  </li>
  <li>
    <a href="${request.route_url('about')}" class="nav-tab">
    What's up with the pony?
    </a>
  </li>
</%def>

<div id="tab3" class="tab-pane active">
  <p>
    So you've read the blurb on the <a href="${request.route_url('home')}">
    Home</a> page and maybe even pre-registered for a brevet or two.
    But you're also the organizer of a future BC Randonneurs brevet,
    and now you're thinking
    "This is cool!  Can I get my brevet added to the
    <a href="${request.route_url('about')}">RandoPony</a>?".
    You betcha!
  </p>
  <p>
    Just send an email to <a href="mailto:${admin_email}">${admin_email}</a>
    with the following information:
  </p>
  <ul>
    <li>
      Region, distance and date of your brevet; e.g. VI200 21-Aug-2010
    </li>
    <li>Route name</li>
    <li>Start location and time</li>
    <li>
      Email address(es) that you want to receive rider pre-registration
      notices at (you can specify more than 1 if you want)
    </li>
  </ul>

  <p>
    We'll add the brevet and pre-registration form pages for your event to the
    pony,
    and notify the <a href="http://randonneurs.bc.ca/">randonneurs.bc.ca</a>
    webmaster so that they can make links from the club pages to your brevet
    page here.
    You'll get an email from the pony to let you know that the brevet page has
    been set up.
    That message will also include a link to a rider list spreadsheet that the
    pony will build on Google Drive as riders sign up.
    Also in the setup message will be a link that will give you a list of the
    pre-registered riders email addresses in case you want to send a bulk message
    to them
    - please use the list responsibly by pasting it in the <strong>bcc</strong>
    field to avoid unnecessary distribution of people's email addresses.
  </p>
  <p>
    As riders pre-register for your event their names will appear in
    the list on the page for your brevet,
    and you'll receive email messages from the pony letting you know their name,
    email address,
    and club membership status.
    Easy, eh!?
  </p>

  <p>
    Pre-registration for brevets auto-magically closes at noon on the
    day before the event so you can do your paperwork without having to
    worry about riders registering in the middle of the night,
    mere hours before the start.
    If you prefer a different time for pre-registration to close,
    just include that in your email to
    <a href="mailto:${admin_email}">${admin_email}</a>.
  </p>

  <p>
    If you're visiting from another cycling club and are interested in
    getting a pony of your own,
    please read the <a href="request.route_url('about')">
    What's up with the pony?</a> page for information on how you can get and
    deploy this open-source software.
  </p>

  <p>
    The RandoPony can also help out on populaires that aren't big enough to
    warrant using the club's pre-registration payment service provider.
    Likewise,
    it can provide web sign-ups for other club events like the AGM,
    the Spring Social, etc.
    Send email to <a href="mailto:${admin_email}">${admin_email}</a>
    learn more.
  </p>
</div>
