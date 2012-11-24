<%inherit file="page.mako"/>

<%block name="title">RandoPony::Brevet</%block>

<%block name="view_css">
  <link href="//ajax.googleapis.com/ajax/libs/jqueryui/1.9.1/themes/south-street/jquery-ui.css"
        rel="stylesheet">
  <link
  href="${request.static_url('randopony:static/css/jquery-ui-timepicker-addon.css')}"
  rel="stylesheet">
</%block>

<%block name="view_js">
  <script src="//ajax.googleapis.com/ajax/libs/jqueryui/1.9.1/jquery-ui.min.js">
          type="text/javascript">
  </script>
  <script src="${request.static_url('randopony:static/js/jquery-ui-timepicker-addon.js')}">
  </script>
</%block>

${form | n}

<script>
  $(document).ready(function(){
    function setMapURL(start_map_url) {
      $("input[name=start_map_url]")
          .next("span.help-block")
          .children("a")
          .attr("href", start_map_url);
    };
    setMapURL($("input[name=start_map_url]").val());

    $("input[name=start_map_url]").change(function(event){
      setMapURL($(this).val());
    });

    $("#deformcancel").click(function(event){
      // Redirect to brevets list on Cancel buton click.
      window.location = "${cancel_url}";
      event.preventDefault();
    });
  });
</script>
