<%inherit file="page.mako"/>

<%block name="title">
  RandoPony::${event}
</%block>

<%block name="subtitle">
  ${event}
</%block>

<div class="tab-pane active">
  <p>
    The ${event} event is over,
    and the RandoPony has moved on!
  </p>
  <p>
    You should be able to find a link to the results of that event at:
  </p>
  <p>
    <a href="${results_link}">${results_link}</a>
  </p>

  <div class="img-container hidden-phone">
    <img src="${request.static_url('randopony:static/img/ItsOver.jpg')}"
         alt="It's Over!"
         class="filler-img">
    <div class="photo-credit muted pull-right">
      <em><small>Eric Fergusson</small></em>
    </div>
  </div>
</div>
