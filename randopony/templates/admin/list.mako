<%inherit file="page.mako"/>

<div class="container admin-list">
  <ul class="unstyled">
    %for item in items:
    <li>
        <a href="${request.route_url(
                    'admin.{}.{}'.format(list, action), item=str(item))}">
          ${item.persona_email}
        </a>
        <button class="btn btn-danger pull-right">Delete</button>
    </li>
    %endfor
  </ul>
</div>
