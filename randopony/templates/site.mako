<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta content="width=device-width initial-scale=1.0" name="viewport">
  <title><%block name="title">RandoPony</%block></title>
  <link rel="stylesheet"
    href="${request.static_url('randopony:static/css/bootstrap.min.css')}">
  <link rel="stylesheet"
    href="${request.static_url(
            'randopony:static/css/bootstrap-responsive.min.css')}">
  <link rel="stylesheet"
    href="${request.static_url('deform:static/css/form.css')}">
  <%block name="page_css"></%block>

  <script src="//ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.min.js"
          type="text/javascript">
  </script>
  <script src="${request.static_url('randopony:static/js/bootstrap.min.js')}">
  </script>
  <script src="${request.static_url('deform:static/scripts/deform.js')}">
  </script>
  <script>deform.load()</script>
  <%block name="page_js"></%block>
  <!-- TODO: Need a favicon and Apple touch icons -->
</head>

<body>
  ${next.body()}
</body>
</html>
