<div class="input-prepend">
  <span class="add-on"><i class="icon-calendar"></i></span>
  <input
    type="text"
    id="${field.oid}"
    name="${field.name}"
    value="${cstruct}"
    %if getattr(field.widget, "autofocus", False):
    autofocus
    % endif
    %if field.widget.size:
    size=${field.widget.size}
    %endif
    %if field.widget.css_class:
    class="${field.widget.css_class}"
    %endif
    %if field.widget.style:
    style="${field.widget.style}"
    %endif
  >
</div>
<script type="text/javascript">
  deform.addCallback(
    '${field.oid}',
    function(oid) {
      $('#' + oid).datetimepicker(${options | n});
    }
  );
</script>
