<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Premium Lamp Login UI</title>
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  
  <style>
    :root {
      --neon-green: #00f59b;
      --dark-bg: #030608;
      --glass-bg: rgba(15, 22, 28, 0.45);
      --glass-border: rgba(255, 255, 255, 0.08);
    }

    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
      font-family: 'Poppins', sans-serif;
    }

    body {
      background-color: var(--dark-bg);
      min-height: 100vh;
      display: flex;
      justify-content: center;
      align-items: center;
      overflow: hidden;
      transition: background 0.8s cubic-bezier(0.4, 0, 0.2, 1);
    }

    /* پاشبنەمای ژوور کاتێک ڕووناک دەبێتەوە */
    body.light-on {
      background: radial-gradient(circle at 50% 25%, #0a261c 0%, var(--dark-bg) 70%);
    }

    .container {
      position: relative;
      display: flex;
      flex-direction: column;
      align-items: center;
      width: 100%;
      max-width: 400px;
    }

    /* --- بەشی گڵۆپ و ڕۆبۆت --- */
    .lamp-wire {
      width: 3px;
      height: 80px;
      background: linear-gradient(to bottom, #111, #333);
      position: absolute;
      top: -150px;
    }

    .robot-lamp {
      width: 90px;
      height: 90px;
      background: #0a0f12;
      border-radius: 50%;
      position: absolute;
      top: -70px;
      border: 2px solid #1a252f;
      display: flex;
      justify-content: center;
      align-items: center;
      z-index: 10;
      transition: all 0.5s ease;
      box-shadow: inset 0 -10px 20px rgba(0,0,0,0.8);
    }

    .robot-face {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 6px;
      opacity: 0.15;
      transition: all 0.5s ease;
    }

    .eyes {
      display: flex;
      gap: 16px;
      color: var(--neon-green);
      font-weight: 600;
      font-size: 18px;
    }

    .mouth {
      width: 18px;
      height: 8px;
      border-bottom: 3px solid var(--neon-green);
      border-radius: 0 0 10px 10px;
    }

    /* کاریگەری ڕووناکبوونەوەی گڵۆپ */
    body.light-on .robot-lamp {
      background: #002216;
      border-color: var(--neon-green);
      box-shadow: 0 0 50px rgba(0, 245, 155, 0.4), inset 0 0 25px rgba(0, 245, 155, 0.5);
    }

    body.light-on .robot-face {
      opacity: 1;
      filter: drop-shadow(0 0 8px var(--neon-green));
    }

    /* --- پەتی ڕاکێشان --- */
    .pull-cord {
      position: absolute;
      top: -15px;
      right: 90px;
      display: flex;
      flex-direction: column;
      align-items: center;
      cursor: pointer;
      z-index: 20;
    }

    .cord-line {
      width: 2px;
      height: 50px;
      background: #444;
      transition: height 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }

    .cord-knob {
      width: 14px;
      height: 20px;
      background: var(--neon-green);
      border-radius: 4px;
      box-shadow: 0 0 10px rgba(0, 245, 155, 0.3);
      transition: transform 0.2s;
    }

    .pull-cord:hover .cord-knob {
      transform: scale(1.1);
    }

    .pull-cord.pulled .cord-line {
      height: 70px;
    }

    /* --- فۆڕمی چوونەژوورەوە (Glassmorphism) --- */
    .login-box {
      margin-top: 50px;
      width: 100%;
      background: var(--glass-bg);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid var(--glass-border);
      padding: 40px 35px;
      border-radius: 24px;
      opacity: 0.1;
      transform: translateY(30px) scale(0.95);
      pointer-events: none;
      transition: all 0.6s cubic-bezier(0.16, 1, 0.3, 1);
    }

    body.light-on .login-box {
      opacity: 1;
      transform: translateY(0) scale(1);
      pointer-events: all;
      border-color: rgba(0, 245, 155, 0.2);
      box-shadow: 0 25px 50px rgba(0,0,0,0.5), 0 0 40px rgba(0, 245, 155, 0.05);
    }

    .header {
      text-align: center;
      margin-bottom: 30px;
    }

    .header h2 {
      color: #fff;
      font-size: 24px;
      font-weight: 600;
      letter-spacing: 0.5px;
    }

    .header p {
      color: #7a8c9e;
      font-size: 12px;
      margin-top: 4px;
    }

    /* --- کێڵگەکانی فۆڕم --- */
    .input-group {
      margin-bottom: 20px;
      position: relative;
    }

    .input-group label {
      display: block;
      font-size: 11px;
      color: #7a8c9e;
      margin-bottom: 8px;
      font-weight: 500;
      letter-spacing: 1px;
    }

    .input-wrapper {
      position: relative;
    }

    .input-wrapper i {
      position: absolute;
      left: 16px;
      top: 50%;
      transform: translateY(-50%);
      color: #556a7f;
      font-size: 14px;
      transition: 0.3s;
    }

    .input-wrapper input {
      width: 100%;
      padding: 14px 14px 14px 45px;
      background: rgba(0, 0, 0, 0.2);
      border: 1px solid rgba(255, 255, 255, 0.06);
      border-radius: 12px;
      color: #fff;
      font-size: 14px;
      outline: none;
      transition: all 0.3s ease;
    }

    .input-wrapper input::placeholder {
      color: #4a5c6f;
    }

    .input-wrapper input:focus {
      border-color: var(--neon-green);
      background: rgba(0, 245, 155, 0.03);
    }

    .input-wrapper input:focus + i {
      color: var(--neon-green);
    }

    /* --- دوگمەکان --- */
    .btn-login {
      width: 100%;
      padding: 14px;
      background: linear-gradient(135deg, var(--neon-green), #00d282);
      border: none;
      border-radius: 12px;
      color: #030608;
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 10px;
      margin-top: 10px;
      transition: all 0.3s ease;
    }

    .btn-login:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 20px rgba(0, 245, 155, 0.3);
    }

    .social-login {
      display: flex;
      gap: 15px;
      margin-top: 20px;
    }

    .btn-social {
      flex: 1;
      padding: 12px;
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 10px;
      color: #a1b4c7;
      font-size: 13px;
      cursor: pointer;
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 8px;
      transition: all 0.3s ease;
    }

    .btn-social:hover {
      background: rgba(255, 255, 255, 0.08);
      color: #fff;
    }

  </style>
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

    <div class="login-box">
      <div class="header">
        <h2>Welcome Back</h2>
        <p>Pull the cord to illuminate your path</p>
      </div>

      <div class="input-group">
        <label>USERNAME</label>
        <div class="input-wrapper">
          <input type="text" placeholder="Enter username">
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

      <button class="btn-login">
        SIGN IN <i class="fa-solid fa-arrow-right"></i>
      </button>

      <div class="social-login">
        <button class="btn-social"><i class="fa-brands fa-google"></i> Google</button>
        <button class="btn-social"><i class="fa-brands fa-github"></i> GitHub</button>
      </div>
    </div>

  </div>

  <script>
    const cord = document.getElementById('pullCord');
    let isLightOn = false;

    cord.addEventListener('click', () => {
      // ئەنیمەیشنی ڕاکێشان
      cord.classList.add('pulled');
      
      setTimeout(() => {
        cord.classList.remove('pulled');
        
        // داگیرساندن یان کوژاندنەوە
        isLightOn = !isLightOn;
        if(isLightOn) {
          document.body.classList.add('light-on');
        } else {
          document.body.classList.remove('light-on');
        }
      }, 200); // دوای 0.2 چرکە پەتەکە دەگەڕێتەوە
    });
  </script>

</body>
</html>
