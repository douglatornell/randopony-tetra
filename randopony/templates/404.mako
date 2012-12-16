<%inherit file="page.mako"/>

<%block name="title">
  RandoPony::Page Not Found
</%block>

<%block name="subtitle">
  page not found
</%block>

<div class="tab-pane active">
  Sorry... there is no there there.

  <div class="img-container hidden-phone">
    <img src="${request.static_url('randopony:static/img/404_pony.jpg')}"
         alt="Nothing to see"
         class="filler-img">
    <div class="photo-credit muted pull-right">
      <em><small>
        <a href="http://www.flickr.com/people/45325473@N04/">blinkingidiot</a>
      </small></em>
    </div>
  </div>
</div>
