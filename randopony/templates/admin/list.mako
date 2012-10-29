<%inherit file="page.mako"/>

<div class="container">
  <h4>${list_title}
  <a class='btn btn-primary add-btn',
     href="${request.route_url('admin.{}.new'.format(list))}">
    <i class="icon-plus icon-white hidden-phone"></i> Add New
  </a>
  </h4>
</div>

<div class="container admin-list">
  <ul class="unstyled">
    %for item in items:
    <li>
        <a href="${request.route_url(
                    'admin.{}.{}'.format(list, action), item=str(item))}">
          ${item.persona_email}
        </a>
        <button class="btn btn-danger pull-right">
          <i class="icon-trash icon-white hidden-phone"></i> Delete
        </button>
    </li>
    %endfor
  </ul>
</div>
