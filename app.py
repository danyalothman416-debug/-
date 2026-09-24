<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Danyal - Instagram UI</title>
  <link href="https://fonts.googleapis.com/css2?family=Grand+Hotel&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <link rel="stylesheet" href="home.css">
</head>
<body>

  <div class="app-container">
    
    <header class="top-header">
      <div class="icon-box">
        <i class="fa-solid fa-plus"></i>
      </div>
      <div class="logo-container">
        <h1 class="logo">Danyal</h1>
        <i class="fa-solid fa-chevron-down"></i>
      </div>
      <div class="icon-box transparent">
        <i class="fa-regular fa-heart"></i>
      </div>
    </header>

    <main class="main-feed">
      
      <div class="stories-container">
        <div class="story">
          <div class="story-ring my-story">
            <img src="https://i.pravatar.cc/150?img=11" alt="Your Story">
            <div class="plus-badge"><i class="fa-solid fa-plus"></i></div>
          </div>
          <span class="story-name text-muted">Your story</span>
        </div>
        
        <div class="story">
          <div class="story-ring active"><img src="https://i.pravatar.cc/150?img=32" alt="User"></div>
          <span class="story-name">with.love.khawla</span>
        </div>
        <div class="story">
          <div class="story-ring active"><img src="https://i.pravatar.cc/150?img=5" alt="User"></div>
          <span class="story-name">the_pharmacist_re...</span>
        </div>
        <div class="story">
          <div class="story-ring active"><img src="https://i.pravatar.cc/150?img=8" alt="User"></div>
          <span class="story-name">paymangay_s...</span>
        </div>
      </div>

      <div class="divider"></div>

      <div class="post">
        <div class="post-header">
          <div class="user-info">
            <img src="https://ui-avatars.com/api/?name=Scoop&background=c1121f&color=fff" alt="Profile" class="post-profile-pic">
            <span class="username">scoop.krd</span>
            <i class="fa-solid fa-circle-check verified-badge"></i>
          </div>
          <i class="fa-solid fa-ellipsis"></i>
        </div>
        
        <div class="post-image">
          <img src="https://images.unsplash.com/photo-1585829365295-ab7cd400c167?q=80&w=1000&auto=format&fit=crop" alt="News Post">
        </div>
        
        <div class="post-actions">
          <div class="left-actions">
            <i class="fa-regular fa-heart"></i>
            <i class="fa-regular fa-comment"></i>
            <i class="fa-regular fa-paper-plane"></i>
          </div>
          <i class="fa-regular fa-bookmark"></i>
        </div>
        
        <div class="post-details">
          <p class="likes">1,402 likes</p>
          <p class="caption">
            <span class="username">scoop.krd</span> عەلی زەیدی 27 ملیار دینار لە عالیە نوسەیف دەسەنێتەوە... <span class="more">more</span>
          </p>
        </div>
      </div>
      
    </main>

    <nav class="bottom-nav">
      <a href="#" class="nav-item active">
        <div class="active-bubble">
          <i class="fa-solid fa-house"></i>
        </div>
      </a>
      <a href="#" class="nav-item"><i class="fa-solid fa-magnifying-glass"></i></a>
      <a href="#" class="nav-item"><i class="fa-brands fa-instagram"></i></a>
      <a href="#" class="nav-item"><i class="fa-brands fa-youtube"></i></a>
      <a href="#" class="nav-item profile-pic"><img src="https://i.pravatar.cc/150?img=11" alt="Profile"></a>
    </nav>

  </div>

</body>
</html>
