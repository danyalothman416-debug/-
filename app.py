<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Interactive Lamp Login</title>
  <!-- فۆنتی مۆدێرن -->
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <!-- ئایکۆنەکانی FontAwesome بۆ کێڵگەکان -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
      font-family: 'Poppins', sans-serif;
    }

    body {
      background-color: #070a0d;
      min-height: 100vh;
      display: flex;
      justify-content: center;
      align-items: center;
      overflow: hidden;
      position: relative;
      transition: background 0.5s ease;
    }

    /* پاشبنەمای ژوور کاتێک ڕووناک دەبێتەوە */
    body.light-on {
      background: radial-gradient(circle at 35% 40%, #0d1e1c 0%, #070a0d 80%);
    }

    /* دیزاینی گشتی لاپەڕە */
    .page-wrapper {
      position: relative;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 60px;
      width: 100%;
      max-width: 950px;
      padding: 20px;
    }

    /* بەشی گڵۆپ و پەتەکە */
    .lamp-container {
      position: relative;
      display: flex;
      flex-direction: column;
      align-items: center;
      margin-top: -60px;
    }

    /* تێلی گڵۆپەکە لە سەرەوە */
    .lamp-wire {
      width: 4px;
      height: 140px;
      background: #232d38;
      border-radius: 2px;
    }

    /* کڵاوی گڵۆپەکە */
    .lamp-cap {
      width: 70px;
      height: 25px;
      background: #18222c;
      border-radius: 12px 12px 4px 4px;
      border: 1px solid #2d3b4a;
    }

    /* سەری ڕۆبۆت / گڵۆپی سەرەکی */
    .lamp-bulb {
      width: 110px;
      height: 110px;
      background: #121920;
      border-radius: 50%;
      margin-top: -5px;
      display: flex;
      justify-content: center;
      align-items: center;
      position: relative;
      border: 2px solid #233140;
      transition: all 0.4s ease;
      z-index: 2;
    }

    /* ڕووخساری ناو گڵۆپەکە */
    .robot-face {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 8px;
      opacity: 0.2;
      transition: opacity 0.4s ease, filter 0.4s ease;
    }

    .eyes {
      display: flex;
      gap: 24px;
    }

    .eye {
      font-size: 20px;
      font-weight: 700;
      color: #00f59b;
      line-height: 1;
    }

    .mouth {
      width: 24px;
      height: 10px;
      border-bottom: 3.5px solid #00f59b;
      border-radius: 0 0 16px 16px;
    }

    /* ڕووناکبوونەوەی گڵۆپەکە کاتێک داگیرسا */
    .light-on .lamp-bulb {
      background: #002d20;
      border-color: #00f59b;
      box-shadow: 0 0 35px #00f59b, inset 0 0 25px #00f59b;
    }

    .light-on .robot-face {
      opacity: 1;
      filter: drop-shadow(0 0 8px #00f59b);
    }

    /* تیشکی ڕووناکی */
    .light-beam {
      position: absolute;
      top: 200px;
      width: 450px;
      height: 450px;
      background: radial-gradient(circle, rgba(0, 245, 155, 0.12) 0%, transparent 70%);
      border-radius: 50%;
      pointer-events: none;
      opacity: 0;
      transform: scale(0.6);
      transition: opacity 0.5s ease, transform 0.5s ease;
      z-index: 1;
    }

    .light-on .light-beam {
      opacity: 1;
      transform: scale(1.1);
    }

    /* پەتی ڕاکێشان (Cord) */
    .pull-cord-wrapper {
      position: absolute;
      top: 155px;
      right: -25px;
      display: flex;
      flex-direction: column;
      align-items: center;
      cursor: pointer;
      z-index: 10;
      transition: transform 0.15s ease;
    }

    .cord-string {
      width: 2px;
      height: 75px;
      background: #475a6c;
    }

    .cord-handle {
      width: 14px;
      height: 18px;
      background: #00f59b;
      border-radius: 5px;
      box-shadow: 0 0 10px rgba(0, 245, 155, 0.6);
      transition: transform 0.2s ease;
    }

    .pull-cord-wrapper:hover .cord-handle {
      transform: scale(1.15);
    }

    /* ئەنیمەیشنی ڕاکێشانی پەتەکە */
    .pull-cord-wrapper.pulled {
      transform: translateY(22px);
    }

    /* سندوقی فۆڕمی Login */
    .login-container {
      background: rgba(16, 23, 30, 0.7);
      backdrop-filter: blur(12px);
      border: 1px solid rgba(255, 255, 255, 0.05);
      border-radius: 20px;
      padding: 40px;
      width: 380px;
      color: #fff;
      opacity: 0.15;
      filter: blur(2px);
      pointer-events: none;
      transform: translateY(15px);
      transition: all 0.5s cubic-bezier(0.2, 0.8, 0.2, 1);
    }

    /* کاتێک ڕووناک دەبێتەوە */
    .light-on .login-container {
      opacity: 1;
      filter: blur(0);
      pointer-events: all;
      transform: translateY(0);
      border-color: rgba(0, 245, 155, 0.25);
      box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6), 0 0 30px rgba(0, 245, 155, 0.1);
    }

    .login-header h2 {
      font-size: 26px;
      font-weight: 600;
      margin-bottom: 4px;
      color: #00f59b;
    }

    .login-header p {
      font-size: 13px;
      color: #8b9bb0;
      margin-bottom: 25px;
    }

    .input-group {
      margin-bottom: 18px;
      text-align: left;
    }

    .input-group label {
      display: block;
      font-size: 11px;
      font-weight: 600;
      letter-spacing: 0.8px;
      color: #63778d;
      margin-bottom: 6px;
    }

    .input-box {
      position: relative;
      display: flex;
      align-items: center;
    }

    .input-box i {
      position: absolute;
      left: 14px;
      color: #495a6c;
      font-size: 14px;
      transition: color 0.3s;
    }

    .input-box input {
      width: 100%;
      padding: 12px 14px 12px 42px;
      background: #0d1217;
      border: 1px solid #1e2833;
      border-radius: 10px;
      color: #fff;
      font-size: 14px;
      outline: none;
      transition: all 0.3s ease;
    }

    .input-box input:focus {
      border-color: #00f59b;
      box-shadow: 0 0 12px rgba(0, 245, 155, 0.2);
    }

    .input-box input:focus + i {
      color: #00f59b;
    }

    /* دوگمەی سەرەکی چوونەژوورەوە */
    .sign-in-btn {
      width: 100%;
      padding: 13px;
      margin-top: 10px;
      background: linear-gradient(90deg, #00d282, #00f59b);
      border: none;
      border-radius: 10px;
      color: #070a0d;
      font-size: 14px;
      font-weight: 600;
      letter-spacing: 0.5px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
      transition: all 0.3s ease;
    }

    .sign-in-btn:hover {
      box-shadow: 0 0 20px rgba(0, 245, 155, 0.45);
      transform: translateY(-2px);
    }

    /* دوگمەکانی Social Login */
    .social-section {
      display: flex;
      gap: 12px;
      margin-top: 20px;
    }

    .social-btn {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      padding: 10px;
      background: #0d1217;
      border: 1px solid #1e2833;
      border-radius: 8px;
      color: #9cb1c9;
      font-size: 12px;
      cursor: pointer;
      transition: all 0.3s;
    }

    .social-btn:hover {
      background: #141b22;
      border-color: #314253;
      color: #fff;
    }

    /* هێڵی خوارەوە */
    .signup-text {
      margin-top: 22px;
      font-size: 12px;
      color: #63778d;
      text-align: center;
    }

    .signup-text a {
      color: #00f59b;
      text-decoration: none;
      font-weight: 500;
    }

    .signup-text a:hover {
      text-decoration: underline;
    }
  </style>
</head>
<body>

  <div class="page-wrapper">
    <!-- بەشی گڵۆپە ڕۆبۆتییەکە لەگەڵ پەتەکەی -->
    <div class="lamp-container">
      <div class="lamp-wire"></div>
      <div class="lamp-cap"></div>
      
      <!-- ڕووخساری ڕۆبۆتەکە -->
      <div class="lamp-bulb" id="lampBulb">
        <div class="robot-face">
          <div class="eyes">
            <span class="eye">^</span>
            <span class="eye">^</span>
          </div>
          <div class="mouth"></div>
        </div>
      </div>

      <!-- تیشکی ڕووناکی کە بڵاودەبێتەوە -->
      <div class="light-beam"></div>

      <!-- پەتی ڕاکێشان (Pull Cord) -->
      <div class="pull-cord-wrapper" id="pullCord" title="Pull me!">
        <div class="cord-string"></div>
        <div class="cord-handle"></div>
      </div>
    </div>

    <!-- فۆڕمی چوونەژوورەوەی Login -->
    <div class="login-container">
      <div class="login-header">
        <h2>Welcome Back.</h2>
        <p>Pull the cord to illuminate your path</p>
      </div>

      <form onsubmit="event.preventDefault();">
        <div class="input-group">
          <label>USERNAME</label>
          <div class="input-box">
            <input type="text" placeholder="Enter your username" required>
            <i class="fa-solid fa-user"></i>
          </div>
        </div>

        <div class="input-group">
          <label>PASSWORD</label>
          <div class="input-box">
            <input type="password" placeholder="••••••••" required>
            <i class="fa-solid fa-lock"></i>
          </div>
        </div>

        <button type="submit" class="sign-in-btn">
          SIGN IN <i class="fa-solid fa-arrow-right"></i>
        </button>

        <div class="social-section">
          <button type="button" class="social-btn">
            <i class="fa-brands fa-google"></i> Google
          </button>
          <button type="button" class="social-btn">
            <i class="fa-brands fa-github"></i> GitHub
          </button>
        </div>

        <div class="signup-text">
          Don't have an account? <a href="#">Sign up</a>
        </div>
      </form>
    </div>
  </div>

  <!-- کۆدی کارلێککردن (JavaScript) -->
  <script>
    const pullCord = document.getElementById('pullCord');
    let isLightOn = false;

    pullCord.addEventListener('click', () => {
      // ئەنیمەیشنی ڕاکێشانی پەتەکە بەرەو خوارەوە
      pullCord.classList.add('pulled');

      setTimeout(() => {
        // گەڕاندنەوەی پەتەکە بۆ شوێنی خۆی
        pullCord.classList.remove('pulled');
        
        // هەڵکردن و کوژاندنەوەی ڕووناکییەکە
        isLightOn = !isLightOn;
        document.body.classList.toggle('light-on', isLightOn);
      }, 180);
    });
  </script>
</body>
</html>
