<%inherit file="page.mako"/>

<%block name="title"><title>RandoPony::Brevet</title></%block>

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
    $("#deformcancel").click(function(event){
      window.location = '${cancel_url}';
      event.preventDefault();
    });
  });
</script>
