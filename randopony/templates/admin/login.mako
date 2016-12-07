<%inherit file="page.mako"/>

<div class="container">
  <div class="row">
    <div class="span6 offset3">
        <form action="${request.route_url('admin.login.handler')}" class="form-horizontal" id="login-form" method="POST">
          <div class="control-group"><label for="email" class="control-label">Email</label>
            <div class="controls">
              <input type="email" id="email" name="email" placeholder="you@example.com" required autofocus>
            </div>
          </div>
          <div class="control-group"><label for="password" class="control-label">Password</label>
            <div class="controls">
              <input type="password" id="password" name="password" placeholder="password" required>
            </div>
          </div>
          <div class="controls">
            <button type="submit" class="btn btn-primary" id="login-submit">Log In</button>
            <button type="button" class="btn btn-default" id="login-cancel"> Cancel</button>
          </div>
        </form>
    </div>
  </div>
</div>
