* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: 'Poppins', sans-serif;
}

body {
  background-color: #000; /* باکگراوندی ڕەش بۆ تەواوی شاشەکە */
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
}

/* دروستکردنی شێوەی مۆبایلێک لەناو شاشەدا */
.app-container {
  width: 100%;
  max-width: 414px; /* قەبارەی شاشەی مۆبایل */
  height: 100vh;
  max-height: 896px;
  background-color: #000;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  border-left: 1px solid #222;
  border-right: 1px solid #222;
}

/* --- بەشی سەرەوە (Header) --- */
.top-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 15px;
  border-bottom: 1px solid #262626;
  background-color: #000;
  position: sticky;
  top: 0;
  z-index: 10;
}

.logo {
  font-family: 'Grand Hotel', cursive; /* فۆنتێکی جوان بۆ لۆگۆی Danyal */
  font-size: 32px;
  color: #fff;
  font-weight: 400;
  letter-spacing: 1px;
}

.top-icons {
  display: flex;
  gap: 20px;
}

.top-icons i {
  color: #fff;
  font-size: 24px;
  cursor: pointer;
}

/* --- بەشی ناوەڕاست (Feed) --- */
.main-feed {
  flex-grow: 1;
  overflow-y: auto;
  padding-bottom: 60px; /* جێهێشتنی بۆشایی بۆ مێنیوی خوارەوە */
}

.main-feed::-webkit-scrollbar {
  display: none; /* شاردنەوەی سکڕۆڵباڕ */
}

/* --- ستۆرییەکان --- */
.stories-container {
  display: flex;
  gap: 15px;
  padding: 15px;
  overflow-x: auto;
}

.stories-container::-webkit-scrollbar {
  display: none;
}

.story {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  cursor: pointer;
}

.story-ring {
  width: 68px;
  height: 68px;
  border-radius: 50%;
  background: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
}

.story-ring img {
  width: 62px;
  height: 62px;
  border-radius: 50%;
  border: 3px solid #000;
  object-fit: cover;
}

.add-story {
  background: none; /* سڕینەوەی ڕەنگی ستۆری بۆ هەژماری خۆت */
}

.plus-badge {
  position: absolute;
  bottom: 0;
  right: 0;
  background: #0095f6;
  color: #fff;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 10px;
  border: 2px solid #000;
}

.story-name {
  color: #fff;
  font-size: 11px;
  max-width: 68px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.divider {
  height: 1px;
  background-color: #262626;
}

/* --- پۆستەکان --- */
.post {
  margin-bottom: 20px;
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
  gap: 10px;
}

.user-info img {
  width: 32px;
  height: 32px;
  border-radius: 50%;
}

.user-info .username {
  color: #fff;
  font-size: 13px;
  font-weight: 600;
}

.post-header i {
  color: #fff;
}

.post-image img {
  width: 100%;
  height: auto;
}

.post-actions {
  display: flex;
  justify-content: space-between;
  padding: 12px 15px;
}

.left-actions {
  display: flex;
  gap: 16px;
}

.post-actions i {
  color: #fff;
  font-size: 24px;
  cursor: pointer;
}

.post-actions i:hover {
  color: #888;
}

.post-likes {
  padding: 0 15px;
  color: #fff;
  font-size: 13px;
}

/* --- بەشی خوارەوە (Bottom Navigation) --- */
.bottom-nav {
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding: 10px 0;
  background-color: #000;
  border-top: 1px solid #262626;
  position: absolute;
  bottom: 0;
  width: 100%;
  height: 50px;
}

.nav-item {
  color: #fff;
  font-size: 24px;
  text-decoration: none;
  transition: transform 0.2s;
}

.nav-item:active {
  transform: scale(0.9);
}

.profile-pic img {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  border: 1px solid #fff;
}
