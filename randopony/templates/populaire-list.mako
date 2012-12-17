<%inherit file="page.mako"/>

<%block name="title">
  RandoPony::Populaires
</%block>

<%block name="subtitle">
  populaire pre-registration
</%block>

<div class="tab-pane active">
  <p>
    Please choose the link for the populaire that you want to pre-register
    for:
  </p>
  <ul class="nav nav-pills">
    %for populaire in populaires:
    <li>
      <a href="${request.route_url(
                  'populaire',
                  short_name=populaire.short_name)}">
        ${populaire.event_name}
      </a>
    </li>
    %endfor
  </ul>
  <p>
    This site provides a pre-registration service for populaires that
    simply lets the organizer know that you are intending to ride.
    We collect your name and email address so that we can confirm your
    pre-registration to you and the organizer by email.
  </p>
  <p>
    This is <em>not</em> a credit card payment site,
    so you'll need to bring cash or a cheque with you to the start to
    pay for your entry.
  </p>
  <p>
    Questions about the events should be directed to the ride organizers.
    Feedback about this site can be sent to
    <a href="mailto:${admin_email}">${admin_email}</a>.
  </p>
</div>
