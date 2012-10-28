<%inherit file="page.mako"/>

<ul class="unstyled admin-list">
  %for wrangler in wranglers:
  <li>
    <a href="${request.route_url('admin.wrangler.edit', item=str(wrangler))}">
      ${wrangler.persona_email}
    </a>
  </li>
  %endfor
</ul>
