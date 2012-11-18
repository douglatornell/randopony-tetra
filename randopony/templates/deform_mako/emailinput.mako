<div class="input-prepend">
  <span class="add-on"><i class="icon-envelope"></i></span>
  <input
    type="email"
    name="${field.name}"
    value="${cstruct}"
    placeholder="tom@example.com"
    autofocus
    %if field.widget.size:
    size=${field.widget.size}
    %endif
  >
</div>
