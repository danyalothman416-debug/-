* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: 'Inter', sans-serif;
}

body {
  background-color: #fafafa;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
}

/* شاشەی مۆبایلەکە */
.app-container {
  width: 100%;
  max-width: 414px;
  height: 100vh;
  max-height: 896px;
  background-color: #ffffff;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 0 20px rgba(0,0,0,0.1);
}

/* --- بەشی سەرەوە (Header) --- */
.top-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  background-color: #ffffff;
  position: sticky;
  top: 0;
  z-index: 10;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
}

.logo {
  font-family: 'Grand Hotel', cursive;
  font-size: 32px;
  color: #000;
  font-weight: 400;
}

.logo-container i {
  font-size: 14px;
  color: #000;
  margin-top: 5px;
}

.icon-box {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  background-color: #f0f0f0;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 20px;
  color: #000;
  cursor: pointer;
}

.icon-box.transparent {
  background-color: transparent;
  font-size: 26px;
}

/* --- بەشی ناوەڕاست (Feed) --- */
.main-feed {
  flex-grow: 1;
  overflow-y: auto;
  padding-bottom: 70px; /* بۆشایی بۆ مێنیوی خوارەوە */
}

.main-feed::-webkit-scrollbar {
  display: none;
}

/* --- ستۆرییەکان --- */
.stories-container {
  display: flex;
  gap: 15px;
  padding: 12px 15px;
  overflow-x: auto;
  border-bottom: 1px solid #efefef;
}

.stories-container::-webkit-scrollbar {
  display: none;
}

.story {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  cursor: pointer;
}

/* بازنەی ڕەنگاوڕەنگی ستۆری */
.story-ring {
  width: 74px;
  height: 74px;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
}

.story-ring.active {
  background: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%);
}

.story-ring.my-story {
  background: transparent;
}

.story-ring img {
  width: 66px;
  height: 66px;
  border-radius: 50%;
  border: 3px solid #ffffff;
  object-fit: cover;
}

.plus-badge {
  position: absolute;
  bottom: 2px;
  right: 2px;
  background: #0095f6;
  color: #fff;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 12px;
  border: 2px solid #ffffff;
}

.story-name {
  color: #000;
  font-size: 11px;
  max-width: 74px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.story-name.text-muted {
  color: #737373;
}

/* --- پۆستەکان --- */
.post {
  margin-bottom: 15px;
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.post-profile-pic {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  object-fit: cover;
}

.user-info .username {
  color: #000;
  font-size: 14px;
  font-weight: 600;
}

.verified-badge {
  color: #0095f6;
  font-size: 14px;
}

.post-image img {
  width: 100%;
  height: auto;
  max-height: 500px;
  object-fit: cover;
}

.post-actions {
  display: flex;
  justify-content: space-between;
  padding: 12px 15px;
}

.left-actions {
  display: flex;
  gap: 18px;
}

.post-actions i {
  color: #000;
  font-size: 24px;
  cursor: pointer;
}

.post-details {
  padding: 0 15px;
}

.post-details .likes {
  font-weight: 600;
  font-size: 14px;
  color: #000;
  margin-bottom: 4px;
}

.post-details .caption {
  font-size: 14px;
  color: #000;
  line-height: 1.4;
}

.post-details .more {
  color: #737373;
  cursor: pointer;
}

/* --- بەشی خوارەوە (Bottom Navigation) --- */
.bottom-nav {
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding: 10px 0;
  background-color: #ffffff;
  border-top: 1px solid #efefef;
  position: absolute;
  bottom: 0;
  width: 100%;
  height: 65px;
  z-index: 10;
}

.nav-item {
  color: #000;
  font-size: 24px;
  text-decoration: none;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* شێوازی بازنە ڕەشەکەی خوارەوە بۆ هۆم وەک وێنەکە */
.active-bubble {
  background-color: #000;
  color: #fff;
  width: 50px;
  height: 35px;
  border-radius: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.profile-pic img {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 1px solid #dbdbdb;
  object-fit: cover;
}
