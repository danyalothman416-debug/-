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

body.light-on {
  background: radial-gradient(circle at 50% 25%, #0a261c 0%, var(--dark-bg) 70%);
}

.container {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  max-width: 420px;
}

/* گڵۆپ و پەتەکە */
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

body.light-on .robot-lamp {
  background: #002216;
  border-color: var(--neon-green);
  box-shadow: 0 0 50px rgba(0, 245, 155, 0.4), inset 0 0 25px rgba(0, 245, 155, 0.5);
}

body.light-on .robot-face {
  opacity: 1;
  filter: drop-shadow(0 0 8px var(--neon-green));
}

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

/* سندوقی فۆڕمەکان */
.form-box {
  margin-top: 50px;
  width: 100%;
  background: var(--glass-bg);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid var(--glass-border);
  border-radius: 24px;
  opacity: 0.1;
  transform: translateY(30px) scale(0.95);
  pointer-events: none;
  transition: all 0.6s cubic-bezier(0.16, 1, 0.3, 1);
  overflow: hidden; /* گرنگە بۆ شاردنەوەی فۆڕمەکان */
  position: relative;
}

body.light-on .form-box {
  opacity: 1;
  transform: translateY(0) scale(1);
  pointer-events: all;
  border-color: rgba(0, 245, 155, 0.2);
  box-shadow: 0 25px 50px rgba(0,0,0,0.5), 0 0 40px rgba(0, 245, 155, 0.05);
}

.form-container {
  padding: 40px 35px;
  width: 100%;
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.form-container.hidden {
  display: none;
}

.header {
  text-align: center;
  margin-bottom: 25px;
}

.header h2 {
  color: #fff;
  font-size: 24px;
  font-weight: 600;
}

.header p {
  color: #7a8c9e;
  font-size: 12px;
  margin-top: 4px;
}

/* کێڵگەکان */
.input-group {
  margin-bottom: 18px;
}

.input-group label {
  display: block;
  font-size: 11px;
  color: #7a8c9e;
  margin-bottom: 6px;
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
  padding: 12px 14px 12px 45px;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 10px;
  color: #fff;
  font-size: 14px;
  outline: none;
  transition: all 0.3s ease;
}

.input-wrapper input:focus {
  border-color: var(--neon-green);
  background: rgba(0, 245, 155, 0.03);
}

.input-wrapper input:focus + i {
  color: var(--neon-green);
}

/* دوگمەی سەرەکی */
.btn-main {
  width: 100%;
  padding: 13px;
  background: linear-gradient(135deg, var(--neon-green), #00d282);
  border: none;
  border-radius: 10px;
  color: #030608;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  margin-top: 15px;
  transition: all 0.3s ease;
}

.btn-main:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 245, 155, 0.3);
}

/* بەشی سۆشیاڵ میدیا */
.divider {
  text-align: center;
  margin: 20px 0;
  position: relative;
}

.divider::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  width: 100%;
  height: 1px;
  background: rgba(255, 255, 255, 0.1);
  z-index: 1;
}

.divider span {
  background: var(--dark-bg); /* دەبێت هەمان ڕەنگی باکگراوند بێت یان کەمێک جیاواز */
  padding: 0 10px;
  color: #556a7f;
  font-size: 10px;
  font-weight: 600;
  position: relative;
  z-index: 2;
  letter-spacing: 1px;
}

.social-login {
  display: flex;
  gap: 15px;
  justify-content: center;
}

.btn-social {
  width: 45px;
  height: 45px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 50%; /* شێوەی بازنەیی */
  color: #a1b4c7;
  font-size: 18px;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: all 0.3s ease;
}

.btn-social:hover {
  transform: translateY(-3px);
  color: #fff;
}

.btn-social.google:hover { border-color: #ea4335; box-shadow: 0 5px 15px rgba(234, 67, 53, 0.3); }
.btn-social.apple:hover { border-color: #fff; box-shadow: 0 5px 15px rgba(255, 255, 255, 0.3); }
.btn-social.facebook:hover { border-color: #1877f2; box-shadow: 0 5px 15px rgba(24, 119, 242, 0.3); }

/* تێکستی گۆڕین */
.switch-text {
  text-align: center;
  margin-top: 25px;
  font-size: 12px;
  color: #7a8c9e;
}

.switch-text span {
  color: var(--neon-green);
  font-weight: 500;
  cursor: pointer;
  transition: 0.3s;
}

.switch-text span:hover {
  text-decoration: underline;
}
