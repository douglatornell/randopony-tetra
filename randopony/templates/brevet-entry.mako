<%inherit file="page.mako"/>

<%block name="title">
  RandoPony::${brevet}::Entry
</%block>

<%block name="subtitle">
${brevet}
</%block>

<div class="tab-pane active">

${form | n}

  <div class="img-container hidden-phone">
    <img src="${request.static_url('randopony:static/img/BrevetSignOn.jpg')}"
         alt="2004 Rocky Mtn 1200 Sign-on"
         class="filler-img">
    <div class="photo-credit muted pull-right">
      <em><small>Alex Pope</small></em>
    </div>
  </div>
</div>

<script>
  $(document).ready(function(){
    $("#deformcancel").click(function(event){
      // Redirect to brevet event page on Cancel button click.
      window.location = "${cancel_url}";
      event.preventDefault();
    });
  });
</script>
