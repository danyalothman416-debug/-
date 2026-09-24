<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Premium Login & Register UI</title>
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <link rel="stylesheet" href="style.css">
</head>
<body>

  <div class="container">
    
    <div class="lamp-wire"></div>
    <div class="robot-lamp">
      <div class="robot-face">
        <div class="eyes">
          <span>^</span>
          <span>^</span>
        </div>
        <div class="mouth"></div>
      </div>
    </div>

    <div class="pull-cord" id="pullCord">
      <div class="cord-line"></div>
      <div class="cord-knob"></div>
    </div>

    <div class="form-box">
      
      <div class="form-container" id="loginForm">
        <div class="header">
          <h2>Welcome Back</h2>
          <p>Sign in to continue</p>
        </div>

        <div class="input-group">
          <label>USERNAME OR EMAIL</label>
          <div class="input-wrapper">
            <input type="text" placeholder="Enter username or email">
            <i class="fa-solid fa-user"></i>
          </div>
        </div>

        <div class="input-group">
          <label>PASSWORD</label>
          <div class="input-wrapper">
            <input type="password" placeholder="••••••••">
            <i class="fa-solid fa-lock"></i>
          </div>
        </div>

        <button class="btn-main">
          SIGN IN <i class="fa-solid fa-arrow-right"></i>
        </button>

        <div class="divider"><span>OR CONTINUE WITH</span></div>

        <div class="social-login">
          <button class="btn-social google"><i class="fa-brands fa-google"></i></button>
          <button class="btn-social apple"><i class="fa-brands fa-apple"></i></button>
          <button class="btn-social facebook"><i class="fa-brands fa-facebook-f"></i></button>
        </div>

        <p class="switch-text">
          Don't have an account? <span onclick="toggleForm()">Sign up here</span>
        </p>
      </div>


      <div class="form-container hidden" id="registerForm">
        <div class="header">
          <h2>Create Account</h2>
          <p>Join us today!</p>
        </div>

        <div class="input-group">
          <label>USERNAME</label>
          <div class="input-wrapper">
            <input type="text" placeholder="Choose a username">
            <i class="fa-solid fa-user-plus"></i>
          </div>
        </div>

        <div class="input-group">
          <label>EMAIL</label>
          <div class="input-wrapper">
            <input type="email" placeholder="Enter your email">
            <i class="fa-solid fa-envelope"></i>
          </div>
        </div>

        <div class="input-group">
          <label>PASSWORD</label>
          <div class="input-wrapper">
            <input type="password" placeholder="Create a password">
            <i class="fa-solid fa-lock"></i>
          </div>
        </div>

        <button class="btn-main">
          SIGN UP <i class="fa-solid fa-arrow-right"></i>
        </button>

        <div class="divider"><span>OR SIGN UP WITH</span></div>

        <div class="social-login">
          <button class="btn-social google"><i class="fa-brands fa-google"></i></button>
          <button class="btn-social apple"><i class="fa-brands fa-apple"></i></button>
          <button class="btn-social facebook"><i class="fa-brands fa-facebook-f"></i></button>
        </div>

        <p class="switch-text">
          Already have an account? <span onclick="toggleForm()">Sign in</span>
        </p>
      </div>

    </div>
  </div>

  <script src="script.js"></script>
</body>
</html>
