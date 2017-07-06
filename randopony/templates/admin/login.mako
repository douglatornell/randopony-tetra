<%inherit file="page.mako"/>

<div class="container">
  <div class="row">
    <div class="span6 offset3">
        <form action="${request.route_url('admin.login.handler')}" class="form-horizontal" id="login-form" method="POST">
          <div id="email-group" class="control-group">
            <label for="email" class="control-label">Email</label>
            <div class="controls">
              <input type="email" id="email" name="email" placeholder="you@example.com" required autofocus>
              <p class="help-block hidden"></p>
            </div>
          </div>

          <div id="password-group" class="control-group">
            <label for="password" class="control-label">Password</label>
            <div class="controls">
              <input type="password" id="password" name="password" placeholder="password" required>
              <p class="help-block hidden"></p>
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


<%block name="page_js">
  <script>
    $( document ).ready(function() {
      // Make pressing and releasing the enter key equivalent to
      // clicking the sign-in button
      $( "#login-submit" ).on("keyup", function(event) {
        if (event.keyCode == 13) {
          $("#login-submit").click();
        }
      });

      // Cancel button redirects to landing page
      $( "#login-cancel" ).click(function(event) {
        window.location = "${request.route_url('admin.login')}";
        event.preventDefault();
      });

      // Server-side validation error handling
      %if unknown_email:
        $("#email-group")
          .addClass("has-error")
          .find(">>.help-block")
            .text("Unknown email address")
            .removeClass("hidden");
        $("#email").focus();
      %endif
      %if incorrect_password:
        $("#password-group")
          .addClass("has-error")
          .find(">>.help-block")
            .text("Incorrect password")
            .removeClass("hidden");
        $("#password").focus();
      %endif
    });
  </script>
</%block>
