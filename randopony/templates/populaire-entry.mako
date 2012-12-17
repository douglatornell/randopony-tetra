<%inherit file="page.mako"/>

<%block name="title">
  RandoPony::${populaire}::Entry
</%block>

<%block name="subtitle">
${populaire} ${"{:%d-%b-%Y}".format(populaire.date_time)}
</%block>

<div class="tab-pane active">

${form | n}

  <div class="img-container hidden-phone">
    <img src="${request.static_url('randopony:static/img/banana_smiles.jpg')}"
         alt="Karen and Judy invite you to ride"
         class="filler-img">
    <div class="photo-credit muted pull-right">
      <em><small>Dan McGuire</small></em>
    </div>
  </div>
</div>

<script>
  $(document).ready(function(){
    $("#deformcancel").click(function(event){
      // Redirect to brevets list on Cancel buton click.
      window.location = "${cancel_url}";
      event.preventDefault();
    });
  });
</script>
