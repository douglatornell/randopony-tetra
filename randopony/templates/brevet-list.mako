<%inherit file="page.mako"/>

<%block name="title">
  RandoPony::${regions[region]}
</%block>

<%block name="subtitle">
  ${regions[region].lower()} brevets
</%block>

<div class="tab-pane active">
  <p>
    Please choose the link for the brevet that you want to pre-register for:
  </p>
  <ul class="nav nav-pills nav-stacked">
    %for brevet in region_brevets:
    <li>
      <a href="${request.route_url(
                  'brevet',
                  region=brevet.region,
                  distance=brevet.distance,
                  date='{:%d%b%Y}'.format(brevet.date_time))}">
        ${brevet}
      </a>
    </li>
    %endfor
  </ul>

  <div class="img-container hidden-phone">
    <img src="${request.static_url('randopony:static/img/' + image['file'])}"
         alt="${image['alt']}"
         class="filler-img">
    <div class="photo-credit muted pull-right">
      <em><small>${image['credit']}</small></em>
    </div>
  </div>
</div>
