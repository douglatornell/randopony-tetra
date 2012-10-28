<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta content="width=device-width initial-scale=1.0" name="viewport">
  <%block name="title"><title>RandoPony</title></%block>
  <link
    href="${request.static_url('randopony:static/css/bootstrap.min.css')}"
    rel="stylesheet">
  <link
    href="${request.static_url('randopony:static/css/bootstrap-responsive.min.css')}"
    rel="stylesheet">
  <%block name="page_css"></%block>
  <!-- TODO: Need a favicon and Apple touch icons -->
</head>
<body>
  ${next.body()}

  <script src="//ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.min.js"
          type="text/javascript">
  </script>
  <script src="${request.static_url('randopony:static/js/bootstrap.min.js')}"></script>
  <%block name="page_js"></%block>
</body>
</html>
