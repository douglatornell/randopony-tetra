<div class="deformSet">
  <input type="hidden" name="__start__" value="${field.name}:rename"/>
  % for index, choice in enumerate(field.widget.values):
  <label for="${field.oid}-${index}" class="${field.widget.css_class}">
  <input
    % if cstruct == choice[0]:
    checked
    % endif
    type="radio"
    name="${field.oid}"
    value="${choice[0]}"
    id="${field.oid}-${index}"/>
    ${choice[1]}
  </label>
  % endfor
  <input type="hidden" name="__end__"/>
</div>
