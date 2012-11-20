<%inherit file="page.mako"/>

<div class="container">
  <h4>${list_title}
  <a class='btn btn-primary add-btn',
     href="${request.route_url('admin.{}.create'.format(list))}">
    <i class="icon-plus icon-white"></i>
    <span class="hidden-phone">Add New</span>
  </a>
  </h4>
</div>

<div class="container admin-list">
  <ul class="unstyled">
    %for item in items:
    <li class="admin-list">
        <a href="${request.route_url(
                    'admin.{}.edit'.format(list), item=str(item))}">
          ${item}
        </a>
        <a class="btn btn-danger pull-right"
           href="${request.route_url('admin.delete', list=list, item=str(item))}">
          <i class="icon-trash icon-white"></i>
          <span class="hidden-phone">Delete</span>
        </a>
    </li>
    %endfor
  </ul>
</div>
