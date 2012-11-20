<%inherit file="page.mako"/>

${form | n}

<script>
  $(document).ready(function(){
    $("#deformcancel").click(function(event){
      window.location = '${list_url}';
      event.preventDefault();
    });
  });
</script>
