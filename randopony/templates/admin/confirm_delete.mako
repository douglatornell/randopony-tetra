<%inherit file="page.mako"/>

<form method="POST" action="${request.route_url('admin.delete', list=list,
                                                item=item)}">
  <p>Really delete ${item_type} ${str(item)}?</p>
  <div class="buttons">
    <button class="btn btn-primary" type="submit" value="delete" name="delete">
      <i class="icon-ok icon-white"></i> Yes
    </button>
    <button class="btn btn-danger" type="submit" value="cancel" name="cancel">
      <i class="icon-remove icon-white"></i> No
    </button>
  </div>
</form>