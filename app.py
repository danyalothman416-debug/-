<!DOCTYPE html>
<html lang="ckb" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>ڕێبەری گەشتیاری و کلتووری کەرکووک</title>
  
  <!-- وێبفۆنتی کوردی Vazirmatn -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;600;700;900&display=swap" rel="stylesheet">
  
  <!-- ئایکۆنەکانی FontAwesome -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
  
  <!-- ستایلی Tailwind CSS -->
  <script src="https://cdn.tailwindcss.com"></script>
  
  <!-- نەخشەی کارلێککاری Leaflet.js -->
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          fontFamily: {
            sans: ['Vazirmatn', 'sans-serif'],
          },
          colors: {
            primary: {
              50: '#ecfdf5',
              100: '#d1fae5',
              500: '#10b981',
              600: '#059669',
              700: '#047857',
              800: '#065f46',
            },
            accent: {
              amber: '#f59e0b',
              navy: '#0f172a',
            }
          }
        }
      }
    }
  </script>

  <style>
    body {
      font-family: 'Vazirmatn', sans-serif;
      -webkit-tap-highlight-color: transparent;
      user-select: none;
    }
    
    /* ڕێکخستنی سکرۆڵبار */
    ::-webkit-scrollbar {
      width: 5px;
      height: 5px;
    }
    ::-webkit-scrollbar-thumb {
      background: #cbd5e1;
      border-radius: 10px;
    }
    .hide-scrollbar::-webkit-scrollbar {
      display: none;
    }
    .hide-scrollbar {
      -ms-overflow-style: none;
      scrollbar-width: none;
    }

    #map-container {
      height: 100%;
      width: 100%;
      z-index: 10;
    }

    .pulsing-dot {
      width: 14px;
      height: 14px;
      background: #10b981;
      border-radius: 50%;
      box-shadow: 0 0 0 rgba(16, 185, 129, 0.4);
      animation: pulse 1.8s infinite;
    }
    @keyframes pulse {
      0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
      70% { box-shadow: 0 0 0 12px rgba(16, 185, 129, 0); }
      100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }
  </style>
</head>
<body class="bg-slate-100 text-slate-800 antialiased min-h-screen flex justify-center selection:bg-emerald-500 selection:text-white">

  <!-- کانتینەری سەرەکی شێوازی مۆبایل -->
  <div class="w-full max-w-md bg-white min-h-screen shadow-2xl relative flex flex-col pb-20 border-x border-slate-200">
    
    <!-- سەردێڕ و لۆگۆ -->
    <header class="sticky top-0 z-40 bg-white/90 backdrop-blur-md border-b border-slate-100 px-4 py-3">
      <div class="flex items-center justify-between">
        
        <!-- لۆگۆ و ناوی پڕۆژە -->
        <div class="flex items-center gap-3">
          <div class="relative group cursor-pointer" onclick="document.getElementById('logoFileInput').click()" title="کلیک بکە بۆ گۆڕینی لۆگۆ">
            <img id="appLogo" src="logo.png" alt="لۆگۆی پڕۆژە" 
                 onerror="this.onerror=null; this.src='https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=120&auto=format&fit=crop&q=80';"
                 class="w-11 h-11 rounded-2xl object-cover ring-2 ring-emerald-500 shadow-md transition-transform active:scale-95">
            <span class="absolute -bottom-1 -left-1 bg-emerald-600 text-white p-1 rounded-full text-[9px] shadow">
              <i class="fa-solid fa-camera"></i>
            </span>
          </div>
          <div>
            <h1 class="font-bold text-lg text-slate-900 leading-tight">ڕێبەری کەرکووک</h1>
            <p class="text-xs text-emerald-600 font-semibold flex items-center gap-1">
              <span class="pulsing-dot inline-block !w-2 !h-2"></span> پایتەختی کلتووری و دێرین
            </p>
          </div>
        </div>

        <!-- دوگمەی ڕێکخستنی لۆگۆ و فلتەر -->
        <div class="flex items-center gap-2">
          <button onclick="document.getElementById('logoFileInput').click()" 
                  class="bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs px-2.5 py-1.5 rounded-xl font-medium transition flex items-center gap-1 shadow-sm">
            <i class="fa-solid fa-arrow-up-from-bracket text-emerald-600"></i>
            <span>لۆگۆ</span>
          </button>
          <input type="file" id="logoFileInput" accept="image/*" class="hidden" onchange="handleLogoUpload(event)">
        </div>
      </div>

      <!-- خانەی گەڕان -->
      <div class="mt-3 relative">
        <i class="fa-solid fa-magnifying-glass absolute right-3.5 top-3.5 text-slate-400 text-sm"></i>
        <input type="text" id="searchInput" oninput="handleSearch()" 
               placeholder="گەڕان بۆ شوێنەوار، خواردن، پارک، مۆڵ..." 
               class="w-full bg-slate-100 border border-slate-200 text-slate-800 text-sm rounded-2xl pr-10 pl-9 py-2.5 outline-none focus:border-emerald-500 focus:bg-white transition-all">
        <button id="clearSearchBtn" onclick="clearSearch()" class="hidden absolute left-3 top-2.5 text-slate-400 hover:text-slate-600 p-1">
          <i class="fa-solid fa-circle-xmark text-sm"></i>
        </button>
      </div>

      <!-- پۆلێنەکان (فلتەرەکان) -->
      <div class="flex gap-2 overflow-x-auto hide-scrollbar mt-3 pb-1 text-xs font-medium">
        <button onclick="filterCategory('all')" class="cat-pill active px-3.5 py-1.5 rounded-full bg-emerald-600 text-white whitespace-nowrap shadow-sm transition">
          هەموو (<span id="count-all">0</span>)
        </button>
        <button onclick="filterCategory('historical')" class="cat-pill px-3.5 py-1.5 rounded-full bg-slate-100 text-slate-600 hover:bg-slate-200 whitespace-nowrap transition">
          <i class="fa-solid fa-landmark text-amber-600 ml-1"></i> شوێنەوار
        </button>
        <button onclick="filterCategory('nature')" class="cat-pill px-3.5 py-1.5 rounded-full bg-slate-100 text-slate-600 hover:bg-slate-200 whitespace-nowrap transition">
          <i class="fa-solid fa-tree text-emerald-600 ml-1"></i> سروشت و سەیرانگا
        </button>
        <button onclick="filterCategory('food')" class="cat-pill px-3.5 py-1.5 rounded-full bg-slate-100 text-slate-600 hover:bg-slate-200 whitespace-nowrap transition">
          <i class="fa-solid fa-utensils text-rose-500 ml-1"></i> کەباب و خواردن
        </button>
        <button onclick="filterCategory('market')" class="cat-pill px-3.5 py-1.5 rounded-full bg-slate-100 text-slate-600 hover:bg-slate-200 whitespace-nowrap transition">
          <i class="fa-solid fa-bag-shopping text-blue-500 ml-1"></i> مۆڵ و بازاڕ
        </button>
        <button onclick="filterCategory('hotel')" class="cat-pill px-3.5 py-1.5 rounded-full bg-slate-100 text-slate-600 hover:bg-slate-200 whitespace-nowrap transition">
          <i class="fa-solid fa-hotel text-indigo-500 ml-1"></i> هۆتێل
        </button>
      </div>
    </header>

    <!-- ناوەڕۆکی لاپەڕەکان -->
    <main class="flex-1 overflow-y-auto px-4 py-3">
      
      <!-- ١. پیشاندانی شوێنەکان (Cards View) -->
      <section id="view-places">
        <!-- ستۆری و شوێنە دیارەکان -->
        <div class="mb-4">
          <div class="flex items-center justify-between mb-2">
            <h2 class="text-xs font-bold uppercase tracking-wider text-slate-400">شوێنە تایبەتەکان</h2>
            <span class="text-[11px] text-emerald-600 font-semibold cursor-pointer">تایبەتمەندییە دەنگییەکان</span>
          </div>
          <div class="flex gap-3 overflow-x-auto hide-scrollbar pb-2" id="storiesContainer">
            <!-- ستۆرییەکان لێرە بە شێوەی دینامیکی دادەنرێن -->
          </div>
        </div>

        <!-- لیستی سەرەکی کارتەکان -->
        <div id="placesGrid" class="space-y-4">
          <!-- کارتەکان لێرە بە جاڤاسکریپت دێن -->
        </div>

        <!-- پەیامی نەدۆزینەوە -->
        <div id="noResults" class="hidden text-center py-16">
          <i class="fa-regular fa-compass text-5xl text-slate-300 mb-3 animate-spin"></i>
          <p class="font-bold text-slate-600">هیچ شوێنێک نەدۆزرایەوە!</p>
          <p class="text-xs text-slate-400 mt-1">تکایە وشەیەکی تر بنووسە یان فلتەرەکە بگۆڕە</p>
        </div>
      </section>

      <!-- ٢. لاپەڕەی نەخشەی زیندوو (Map View) -->
      <section id="view-map" class="hidden h-[calc(100vh-170px)] -mx-4 -my-3 relative">
        <div id="leafletMap" class="w-full h-full"></div>
        <!-- کارتی خێرای زانیاری سەر نەخشە -->
        <div id="mapFloatingCard" class="hidden absolute bottom-4 left-4 right-4 bg-white/95 backdrop-blur-md rounded-2xl p-3 shadow-xl z-20 border border-slate-200">
          <div class="flex gap-3 items-center">
            <img id="mapCardImg" src="" class="w-16 h-16 rounded-xl object-cover">
            <div class="flex-1">
              <h4 id="mapCardTitle" class="font-bold text-sm text-slate-900"></h4>
              <p id="mapCardDesc" class="text-xs text-slate-500 line-clamp-1 mt-0.5"></p>
              <div class="flex gap-2 mt-2">
                <button id="mapCardNavBtn" class="bg-emerald-600 text-white text-[11px] px-3 py-1 rounded-lg font-medium flex items-center gap-1">
                  <i class="fa-solid fa-diamond-turn-right"></i> ڕێگەپیشاندەر
                </button>
                <button id="mapCardDetailsBtn" class="bg-slate-100 text-slate-700 text-[11px] px-3 py-1 rounded-lg font-medium">
                  وردەکاری
                </button>
              </div>
            </div>
            <button onclick="closeMapCard()" class="text-slate-400 self-start p-1 hover:text-slate-600">
              <i class="fa-solid fa-xmark"></i>
            </button>
          </div>
        </div>
      </section>

      <!-- ٣. لاپەڕەی دڵخوازەکان (Favorites View) -->
      <section id="view-favorites" class="hidden">
        <div class="flex items-center justify-between mb-4">
          <h2 class="font-bold text-slate-800 text-base">شوێنە پاشەکەوتکراوەکان</h2>
          <span id="favCount" class="text-xs bg-emerald-100 text-emerald-700 font-bold px-2 py-0.5 rounded-full">0 شوێن</span>
        </div>
        <div id="favoritesList" class="space-y-3">
          <!-- دڵخوازەکان لێرە بە شێوەی خۆکارانە باردەکرێن -->
        </div>
        <div id="emptyFavorites" class="hidden text-center py-20">
          <i class="fa-regular fa-bookmark text-5xl text-slate-300 mb-3"></i>
          <p class="font-bold text-slate-600">هیچ شوێنێکت پاشەکەوت نەکردووە</p>
          <p class="text-xs text-slate-400 mt-1">ئایکۆنی پاشەکەوتکردن لەسەر هەر شوێنێک دابگرە بۆ ئەوەی لێرە بمێنێتەوە</p>
        </div>
      </section>

      <!-- ٤. لاپەڕەی زانیاری و مێژووی شار (About View) -->
      <section id="view-about" class="hidden space-y-4">
        <div class="relative rounded-2xl overflow-hidden shadow-lg h-44">
          <img src="https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=800&auto=format&fit=crop&q=80" class="w-full h-full object-cover">
          <div class="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-900/40 to-transparent flex flex-col justify-end p-4 text-white">
            <h3 class="text-xl font-extrabold">کەرکووکی دێرین</h3>
            <p class="text-xs text-slate-200">شارستانیەتی زیاتر لە ٤٥٠٠ ساڵ و مۆزاییکی برایەتی</p>
          </div>
        </div>

        <div class="bg-white rounded-2xl p-4 border border-slate-200 space-y-3 text-sm leading-relaxed text-slate-600">
          <h4 class="font-bold text-slate-800 flex items-center gap-2">
            <i class="fa-solid fa-feather text-emerald-600"></i> کورتەیەک دەربارەی شارەکە
          </h4>
          <p>
            کەرکووک یەکێکە لە کۆنترین شارە ئاوەدانەکانی جیهان. لە سەردەمی سۆمەری و بابل و ئاشوورییەکان بە ناوی (ئەرەپخا) ناسراوە. ئەم شارە بە کەلەپوورە دەوڵەمەندەکەی، قەڵا بەرزەکەی، نەوتی بابا گوڕگوڕ و پێکەوەژیانی ئاشتیانەی نەتەوە جیاوازەکانی ناسراوە.
          </p>
        </div>

        <!-- کارتی مۆڵەت و گەشەپێدان -->
        <div class="bg-gradient-to-r from-emerald-700 to-teal-800 text-white rounded-2xl p-4 shadow-md">
          <div class="flex items-center gap-3 mb-2">
            <div class="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center text-lg">
              <i class="fa-solid fa-code"></i>
            </div>
            <div>
              <h4 class="font-bold text-sm">ئەپڵیکەیشنی ڕێبەری گەشتیاری</h4>
              <p class="text-[11px] text-emerald-200">ئامادەکراو بۆ تاقیکردنەوە لە VS Code</p>
            </div>
          </div>
          <p class="text-xs text-slate-100 leading-normal">
            دەتوانیت هەر شوێنێک دەتەوێت زیادی بکەیت لە ناو ڕیزبەندی داتای <code>placesData</code> لە کۆدی جاڤاسکریپتەکەدا.
          </p>
        </div>
      </section>

    </main>

    <!-- مۆداڵی پیشاندانی وردەکاری شوێن (Modal) -->
    <div id="detailsModal" class="hidden fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-end sm:items-center justify-center p-0 sm:p-4">
      <div class="bg-white w-full max-w-md rounded-t-3xl sm:rounded-3xl max-h-[90vh] overflow-y-auto overflow-x-hidden animate-in slide-in-from-bottom duration-300">
        <div class="relative h-60">
          <img id="modalImg" src="" class="w-full h-full object-cover">
          <button onclick="closeModal()" class="absolute top-4 left-4 bg-black/50 text-white w-9 h-9 rounded-full flex items-center justify-center hover:bg-black/70">
            <i class="fa-solid fa-xmark"></i>
          </button>
          <div class="absolute bottom-3 right-4 bg-emerald-600 text-white text-xs px-3 py-1 rounded-full font-bold shadow" id="modalCategoryBadge"></div>
        </div>

        <div class="p-5 space-y-4">
          <div class="flex items-start justify-between">
            <div>
              <h3 id="modalTitle" class="text-xl font-bold text-slate-900"></h3>
              <p id="modalSubtitle" class="text-xs text-slate-400 mt-1 flex items-center gap-1">
                <i class="fa-solid fa-location-dot text-rose-500"></i>
                <span id="modalLocationName">کەرکووک</span>
              </p>
            </div>
            <button id="modalFavBtn" class="text-2xl text-slate-300 hover:text-rose-500 transition">
              <i class="fa-solid fa-heart"></i>
            </button>
          </div>

          <!-- دوگمەی ڕێبەری دەنگی بە کوردی -->
          <div class="bg-emerald-50 border border-emerald-200 rounded-2xl p-3 flex items-center justify-between">
            <div class="flex items-center gap-3">
              <button id="audioSpeakBtn" onclick="toggleAudioGuide()" class="w-10 h-10 rounded-xl bg-emerald-600 text-white flex items-center justify-center shadow-md hover:bg-emerald-700 transition">
                <i id="audioIcon" class="fa-solid fa-volume-high"></i>
              </button>
              <div>
                <p class="text-xs font-bold text-emerald-950">ڕێبەری دەنگی (دەنگی ژیری دەستکرد)</p>
                <p class="text-[11px] text-emerald-600">گوێبیستی کورتەمێژووی ئەم شوێنە ببە</p>
              </div>
            </div>
            <span id="audioStatus" class="text-[10px] text-slate-400 font-medium">ئامادەیە</span>
          </div>

          <!-- باس و مێژوو -->
          <div>
            <h4 class="font-bold text-slate-800 text-sm mb-1">دەربارەی شوێنەکە:</h4>
            <p id="modalDesc" class="text-slate-600 text-sm leading-relaxed text-justify"></p>
          </div>

          <!-- دوگمەی نەخشە و ڕێنمایی ڕێگا -->
          <div class="pt-2 flex gap-3">
            <a id="modalNavBtn" href="#" target="_blank" class="flex-1 bg-emerald-600 hover:bg-emerald-700 text-white text-center py-3 rounded-2xl font-bold text-sm shadow-md shadow-emerald-500/20 flex items-center justify-center gap-2">
              <i class="fa-solid fa-diamond-turn-right text-base"></i>
              <span>ڕێگام پێ نیشان بدە (Google Maps)</span>
            </a>
          </div>
        </div>
      </div>
    </div>

    <!-- مێنیوی خوارەوەی مۆبایل (Bottom Nav Bar) -->
    <nav class="fixed bottom-0 w-full max-w-md bg-white/95 backdrop-blur-lg border-t border-slate-200 px-6 py-2.5 flex justify-between items-center z-40">
      <button onclick="switchTab('places')" id="nav-places" class="nav-item active flex flex-col items-center gap-1 text-emerald-600 transition">
        <i class="fa-solid fa-compass text-lg"></i>
        <span class="text-[10px] font-bold">گەڕان</span>
      </button>

      <button onclick="switchTab('map')" id="nav-map" class="nav-item flex flex-col items-center gap-1 text-slate-400 hover:text-slate-600 transition">
        <i class="fa-solid fa-map-location-dot text-lg"></i>
        <span class="text-[10px] font-bold">نەخشە</span>
      </button>

      <button onclick="switchTab('favorites')" id="nav-favorites" class="nav-item flex flex-col items-center gap-1 text-slate-400 hover:text-slate-600 transition relative">
        <i class="fa-solid fa-heart text-lg"></i>
        <span class="text-[10px] font-bold">دڵخوازەکان</span>
        <span id="navFavBadge" class="hidden absolute -top-1 -right-1 bg-rose-500 text-white text-[9px] w-4 h-4 rounded-full flex items-center justify-center font-bold">0</span>
      </button>

      <button onclick="switchTab('about')" id="nav-about" class="nav-item flex flex-col items-center gap-1 text-slate-400 hover:text-slate-600 transition">
        <i class="fa-solid fa-circle-info text-lg"></i>
        <span class="text-[10px] font-bold">شارەکە</span>
      </button>
    </nav>

  </div>

  <!-- کۆدی پڕۆگرامسازی و داتاکان (JavaScript) -->
  <script>
    // لیستی ۳۲ شوێنی ڕاستەقینەی شاری کەرکووک بە پۆوتانی GPS و وێنە و وردەکاری تەواو
    const placesData = [
      {
        id: 1,
        title: "قەڵای دێرینی کەرکووک",
        category: "historical",
        categoryName: "شوێنەوار",
        lat: 35.4708,
        lng: 44.3942,
        address: "ناوەندی شاری کەرکووک",
        image: "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=600&auto=format&fit=crop&q=80",
        desc: "قەڵای کەرکووک دەکەوێتە ناوجەرگەی شار و لەسەر تەپۆڵکەیەکی بەرز بنیادنراوە کە مێژووەکەی بۆ سەردەمی گوتییەکان و ئاشوورییەکان (نزیکەی ٤٥٠٠ ساڵ پێش ئێستا) دەگەڕێتەوە. لە ناو قەڵاکەدا کەنیسەی کۆن، گۆڕی پێغەمبەر دانیال و خانوو و کۆڵانە کلتوورییەکان جێگیر بوون.",
        rating: 4.9,
        featured: true
      },
      {
        id: 2,
        title: "ئاگری نەکوژاوەی بابا گوڕگوڕ",
        category: "nature",
        categoryName: "سروشت و کلتوور",
        lat: 35.5518,
        lng: 44.3164,
        address: "باپووری نەوتی باکوور - بابا گوڕگوڕ",
        image: "https://images.unsplash.com/photo-1508873696983-2df570464756?w=600&auto=format&fit=crop&q=80",
        desc: "ئاگری هەمیشەیی بابا گوڕگوڕ یەکێکە لە کۆنترین دیاردە سروشتییەکانی جیهان کە هەزاران ساڵە بەهۆی دزەکردنی گازی سروشتییەوە دەسوتێت بەبێ کوژانەوە. هێرۆدۆتسی مێژوونووسیش ئاماژەی پێکردووە.",
        rating: 4.8,
        featured: true
      },
      {
        id: 3,
        title: "بازاڕی قەیسەری کۆن",
        category: "market",
        categoryName: "مۆڵ و بازاڕ",
        lat: 35.4688,
        lng: 44.3951,
        address: "بەرامبەر قەڵای کەرکووک",
        image: "https://images.unsplash.com/photo-1533900298318-6b8da08a523e?w=600&auto=format&fit=crop&q=80",
        desc: "بازاڕی قەیسەری مێژووەکەی دەگەڕێتەوە بۆ سەردەمی عوسمانی (١٨٥٥). خاوەنی سەدان دووکان و تاقی بەردینە، ناوەندی کڕین و فرۆشتنی زێڕ و قوماش و بەهارات و دیارییە کەلەپوورییەکانە.",
        rating: 4.7,
        featured: true
      },
      {
        id: 4,
        title: "قشڵەی کەرکووک",
        category: "historical",
        categoryName: "شوێنەوار",
        lat: 35.4665,
        lng: 44.3905,
        address: "شەقامی سەرەکی ناوەند",
        image: "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?w=600&auto=format&fit=crop&q=80",
        desc: "قشڵەی مێژوویی کەرکووک لە ساڵی ١٨٦٣ لەلایەن عوسمانییەکانەوە وەک بارەگای سەربازی دروستکراوە. تەلارسازییە تایبەتەکەی و تاقە گەورەکانی مۆرکێکی دێرین بە شارەکە دەبەخشن.",
        rating: 4.6,
        featured: false
      },
      {
        id: 5,
        title: "مەقامی پێغەمبەر دانیال",
        category: "historical",
        categoryName: "شوێنەوار",
        lat: 35.4695,
        lng: 44.3927,
        address: "ناوەوەی قەڵای کەرکووک",
        image: "https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=600&auto=format&fit=crop&q=80",
        desc: "ئەم مەقام و مزگەوتە لەسەر قەڵای کەرکووک هەڵکەوتووە، خاوەنی گومەزی فیرۆزەیی دێرینە و بە مەقامی پێغەمبەر دانیال و حەنینا ناسراوە کە ڕێزێکی تایبەتی لەلای هەموو پێکهاتەکان هەیە.",
        rating: 4.8,
        featured: true
      },
      {
        id: 6,
        title: "پردی بەردین (پردی کۆن)",
        category: "historical",
        categoryName: "شوێنەوار",
        lat: 35.4725,
        lng: 44.3970,
        address: "لەسەر چەمی خاسە",
        image: "https://images.unsplash.com/photo-1513694203232-719a280e022f?w=600&auto=format&fit=crop&q=80",
        desc: "پردی بەردین کە بە 'تاش کۆپری' ناسراوە، لەسەر چەمی خاسە دروستکراوە و بەشی قەڵا و شاری کۆن بە گەڕەکەکانی قۆرییە و ئەحمەد ئاغا دەبەستێتەوە.",
        rating: 4.5,
        featured: false
      },
      {
        id: 7,
        title: "سەیرانگای چەمی ڕێدار (شوان)",
        category: "nature",
        categoryName: "سروشت و سەیرانگا",
        lat: 35.6850,
        lng: 44.7500,
        address: "ناحیەی شوان - باکووری کەرکووک",
        image: "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=600&auto=format&fit=crop&q=80",
        desc: "ناوچەیەکی سەرسەوز و شاخاوی دڵڕفێن لە نێوان کەرکووک و چەمچەماڵ کە ئاوی سازگار و درەختی چنار و سروشتی کێوی لێیە، گەشتیاران لە بەهار و هاویندا بۆ پشوو ڕووی تێدەکەن.",
        rating: 4.7,
        featured: true
      },
      {
        id: 8,
        title: "بەنداوی دووبز و سەیرانگای زێ",
        category: "nature",
        categoryName: "سروشت و سەیرانگا",
        lat: 35.7600,
        lng: 44.0500,
        address: "قەزای دووبز",
        image: "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=600&auto=format&fit=crop&q=80",
        desc: "بەنداوی دووبز لەسەر زێی بچووک بنیادنراوە، ناوچەیەکی فێنک و سەرنجڕاکێشە بۆ بەلەمسواری و ماسیگرتن و بەسەربردنی کاتی خۆش لە کەنار ئاوەکە.",
        rating: 4.6,
        featured: false
      },
      {
        id: 9,
        title: "باخی گشتی کەرکووک",
        category: "nature",
        categoryName: "سروشت و سەیرانگا",
        lat: 35.4620,
        lng: 44.3850,
        address: "شەقامی سەرەکی ئەتڵەس",
        image: "https://images.unsplash.com/photo-1448375240586-882707db888b?w=600&auto=format&fit=crop&q=80",
        desc: "کۆنترین باخی گشتی کەرکووکە کە پڕە لە درەختی تەمەندرێژ و شوێنی پشوودانی خێزانەکان، لە ناوەندی شاردا کەشێکی ئارام و سەوزایی فەراهەم دەکات.",
        rating: 4.3,
        featured: false
      },
      {
        id: 10,
        title: "بەنداوی دۆڵی خاسە",
        category: "nature",
        categoryName: "سروشت و سەیرانگا",
        lat: 35.5800,
        lng: 44.4200,
        address: "باکووری کەرکووک - خاسە",
        image: "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=600&auto=format&fit=crop&q=80",
        desc: "دیمەنێکی ئاوی پان و بەرفراوان کە دەورەدراوە بە گرد و تەپۆڵکەکان، بۆ هەوادارانی وێنەگری و گەشتی ئێواران شوێنێکی زۆر دڵگیرە.",
        rating: 4.4,
        featured: false
      },
      {
        id: 11,
        title: "سەیرانگای پردێ (ئاڵتوون کۆپری)",
        category: "nature",
        categoryName: "سروشت و سەیرانگا",
        lat: 35.7520,
        lng: 44.1480,
        address: "ناحیەی پردێ",
        image: "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=600&auto=format&fit=crop&q=80",
        desc: "پردێ وەک دوورگەیەک لە نێوان دوو لقە ئاوی زێی بچووک هەڵکەوتووە، بە دارستانە چڕەکانی بەڕوو و ماسییە بەتامەکەی ناو زێیەکە ناوبانگی دەرکردووە.",
        rating: 4.6,
        featured: false
      },
      {
        id: 12,
        title: "پارکی شۆراو",
        category: "nature",
        categoryName: "سروشت و سەیرانگا",
        lat: 35.5120,
        lng: 44.4050,
        address: "ناوچەی شۆراو",
        image: "https://images.unsplash.com/photo-1519331379826-f10be5486c6f?w=600&auto=format&fit=crop&q=80",
        desc: "پارکێکی هاوچەرخ کە یاریگای منداڵان و ڕێڕەوی پیادەڕۆیی و کافتریای خێزانی لەخۆدەگرێت، شوێنێکی زۆر گونجاوە بۆ گەشتی ڕۆژانی هەینی.",
        rating: 4.2,
        featured: false
      },
      {
        id: 13,
        title: "کەبابی بەناوبانگی ئەحمەد سمێڵ",
        category: "food",
        categoryName: "کەباب و خواردن",
        lat: 35.4810,
        lng: 44.4120,
        address: "گەڕەکی شۆرجە",
        image: "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=600&auto=format&fit=crop&q=80",
        desc: "کەبابی کەرکووک بە تام و چێژە تایبەتەکەی لە سەرتاسەری کوردستان و عێراق ناوبانگی هەیە. کەبابی ئەحمەد سمێڵ یەکێک لە ناوە هەرە دێرین و ئاشناکانی ئەم شارەیە.",
        rating: 4.9,
        featured: true
      },
      {
        id: 14,
        title: "کەبابی مێژوویی ئیحسان",
        category: "food",
        categoryName: "کەباب و خواردن",
        lat: 35.4690,
        lng: 44.3960,
        address: "نزیک بازاڕی قەیسەری",
        image: "https://images.unsplash.com/photo-1544025162-d76694265947?w=600&auto=format&fit=crop&q=80",
        desc: "دەستڕەنگینی لە دروستکردنی کەبابی بەرخی تازە بە نانی تیری و پیازی سماقدار. چەندین دەیەیە پێشوازی لە میوانان و گەشتیارانی شار دەکات.",
        rating: 4.8,
        featured: false
      },
      {
        id: 15,
        title: "چێشتخانەی سلێمانی لە کەرکووک",
        category: "food",
        categoryName: "کەباب و خواردن",
        lat: 35.4450,
        lng: 44.3750,
        address: "شەقامی ڕێگای بەغدا",
        image: "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=600&auto=format&fit=crop&q=80",
        desc: "پێشکەشکردنی هەموو جۆرە خواردنە کوردی و ڕۆژهەڵاتییەکان وەک برنج و شلە، قۆزی بەرخ، ماسی مەسگوف، و خواردنی ئامادەکراوی کوردی.",
        rating: 4.6,
        featured: false
      },
      {
        id: 16,
        title: "دۆندرمە و شەکەرلەمی فەریق",
        category: "food",
        categoryName: "کەباب و خواردن",
        lat: 35.4678,
        lng: 44.3938,
        address: "ناوەندی شار - نزیک قەڵا",
        image: "https://images.unsplash.com/photo-1501443762994-82bd5dace89a?w=600&auto=format&fit=crop&q=80",
        desc: "تامی لەبیرنەکراوی دۆندرمەی سروشتی شیر و سەعلەبی کەرکووک بە دارچین و فستقی حەلەبییەوە کە مێژووەکەی زیاتر لە نیو سەدەیە.",
        rating: 4.7,
        featured: false
      },
      {
        id: 17,
        title: "کەرکووک مۆڵ (Kirkuk Mall)",
        category: "market",
        categoryName: "مۆڵ و بازاڕ",
        lat: 35.4420,
        lng: 44.3710,
        address: "شەقامی ڕێگای بەغدا",
        image: "https://images.unsplash.com/photo-1519567241046-7f570eee3ce6?w=600&auto=format&fit=crop&q=80",
        desc: "گەورەترین مۆڵی هاوچەرخی شاری کەرکووک کە پێکهاتووە لە براندە جیهانییەکان، سینەمای نوێ، یاریگای سەردەمیانەی منداڵان و کۆمەڵێک چێشتخانەی خێرا.",
        rating: 4.7,
        featured: true
      },
      {
        id: 18,
        title: "تایم سێنتەر مۆڵ (Time Center)",
        category: "market",
        categoryName: "مۆڵ و بازاڕ",
        lat: 35.4800,
        lng: 44.3850,
        address: "گەڕەکی ڕێگای موسڵ",
        image: "https://images.unsplash.com/photo-1567449303078-57ad995bd301?w=600&auto=format&fit=crop&q=80",
        desc: "مۆڵێکی مۆدێرن بۆ بازاڕکردنی جلوبەرگ، کەرەستەی جوانکاری و هایپەرمارکێتی گەورە لەگەڵ کافتریای ئاست بەرز بۆ خێزانەکان.",
        rating: 4.5,
        featured: false
      },
      {
        id: 19,
        title: "بازاڕی ئەتڵەس و ئەسحاب",
        category: "market",
        categoryName: "مۆڵ و بازاڕ",
        lat: 35.4670,
        lng: 44.3880,
        address: "شەقامی ئەتڵەس",
        image: "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=600&auto=format&fit=crop&q=80",
        desc: "شەقامێکی پڕ لە جموجۆڵی بازرگانی کە پڕە لە دووکانی پێڵاو، جلوبەرگ، مۆبایل و کەلوپەلی ئەلیکترۆنی لە دڵی شاری کەرکووکدا.",
        rating: 4.4,
        featured: false
      },
      {
        id: 20,
        title: "هۆتێل پلازا کەرکووک (Plaza Hotel)",
        category: "hotel",
        categoryName: "هۆتێل و مانەوە",
        lat: 35.4600,
        lng: 44.3820,
        address: "ناوەندی شار",
        image: "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=600&auto=format&fit=crop&q=80",
        desc: "هۆتێلێکی ٤ ئەستێرەی پلە یەک بە خزمەتگوزاری مۆدێرن، ژووری ئارام و خاوێن، هۆڵی کۆبوونەوە و چێشتخانەی تایبەتی میوانداری بیانی و ناوخۆیی.",
        rating: 4.5,
        featured: false
      },
      {
        id: 21,
        title: "هۆتێل پالاسی کەرکووک",
        category: "hotel",
        categoryName: "هۆتێل و مانەوە",
        lat: 35.4650,
        lng: 44.3790,
        address: "شەقامی کۆماری",
        image: "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=600&auto=format&fit=crop&q=80",
        desc: "شوێنێکی گونجاو و ئارام بۆ مانەوەی گەشتیاران بە نرخی گونجاو و لە نزیک ناوەندە بازرگانی و کارگێڕییەکانی شارەکە.",
        rating: 4.3,
        featured: false
      },
      {
        id: 22,
        title: "کەنیسەی دێرینی ئوم ئەلئەحزان",
        category: "historical",
        categoryName: "شوێنەوار",
        lat: 35.4715,
        lng: 44.3930,
        address: "ناو قەڵای کەرکووک",
        image: "https://images.unsplash.com/photo-1548625361-19597a7a505b?w=600&auto=format&fit=crop&q=80",
        desc: "کۆنترین کەنیسەی مەسیحییە کلدانی و ئاشوورییەکانە لە قەڵای کەرکووک کە پێناسەی پێکەوەژیانی ئایینی هەزاران ساڵەی ئەم شارەیە.",
        rating: 4.7,
        featured: false
      },
      {
        id: 23,
        title: "یاریگای نێودەوڵەتی کەرکووک (ئۆڵۆمپی)",
        category: "nature",
        categoryName: "وەرزش و سەیرانگا",
        lat: 35.4520,
        lng: 44.3680,
        address: "نزیک گەڕەکی حورییە",
        image: "https://images.unsplash.com/photo-1522778119026-d647f0596c20?w=600&auto=format&fit=crop&q=80",
        desc: "یاریگایەکی گەورە و هاوچەرخی ٢٥ هەزار کەسییە کە تایبەتە بە چالاکییە وەرزشییەکان و یارییەکانی تۆپی پێی عێراق و کوردستان.",
        rating: 4.4,
        featured: false
      },
      {
        id: 24,
        title: "شیرنەمەنی بەناوبانگی تەحریر",
        category: "food",
        categoryName: "کەباب و خواردن",
        lat: 35.4750,
        lng: 44.3890,
        address: "شەقامی تەحریر",
        image: "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=600&auto=format&fit=crop&q=80",
        desc: "باشترین بەقڵاوەی گوێز و فستق، کنافەی گەرم بە پەنیر و شیرینییە کلتوورییەکانی شار بە ڕۆنی کوردی پاک.",
        rating: 4.8,
        featured: false
      }
    ];

    // دۆخی ئەپڵیکەیشن
    let currentCategory = 'all';
    let searchQuery = '';
    let currentPlaceForAudio = null;
    let leafletMap = null;
    let markersLayer = null;
    let favorites = JSON.parse(localStorage.getItem('kirkuk_favorites') || '[]');

    // دەستپێکردنی ئەپڵیکەیشن
    window.addEventListener('DOMContentLoaded', () => {
      loadSavedLogo();
      updateCategoryCounts();
      renderStories();
      renderPlaces();
      updateFavBadge();
    });

    // بەشی لۆگۆ
    function handleLogoUpload(event) {
      const file = event.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
          const base64Logo = e.target.result;
          document.getElementById('appLogo').src = base64Logo;
          localStorage.setItem('user_custom_logo', base64Logo);
          alert('لۆگۆکەت بە سەرکەوتوویی جێگیر کرا!');
        };
        reader.readAsDataURL(file);
      }
    }

    function loadSavedLogo() {
      const savedLogo = localStorage.getItem('user_custom_logo');
      if (savedLogo) {
        document.getElementById('appLogo').src = savedLogo;
      }
    }

    // ئەژمارکردنی شوێنەکان بۆ فلتەرەکان
    function updateCategoryCounts() {
      document.getElementById('count-all').innerText = placesData.length;
    }

    // پیشاندانی ستۆرییەکان لە سەرەوە
    function renderStories() {
      const container = document.getElementById('storiesContainer');
      const featured = placesData.filter(p => p.featured);
      container.innerHTML = featured.map(p => `
        <div onclick="openModal(${p.id})" class="flex flex-col items-center gap-1 cursor-pointer shrink-0 group">
          <div class="w-16 h-16 rounded-full p-[2.5px] bg-gradient-to-tr from-amber-500 via-rose-500 to-emerald-500 group-hover:scale-105 transition-transform">
            <img src="${p.image}" class="w-full h-full rounded-full object-cover border-2 border-white">
          </div>
          <span class="text-[10px] font-bold text-slate-700 w-16 truncate text-center">${p.title}</span>
        </div>
      `).join('');
    }

    // پیشاندانی کارتی شوێنەکان
    function renderPlaces() {
      const grid = document.getElementById('placesGrid');
      const noResults = document.getElementById('noResults');

      let filtered = placesData.filter(place => {
        const matchesCategory = (currentCategory === 'all') || (place.category === currentCategory);
        const matchesSearch = place.title.includes(searchQuery) || place.desc.includes(searchQuery) || place.address.includes(searchQuery);
        return matchesCategory && matchesSearch;
      });

      if (filtered.length === 0) {
        grid.innerHTML = '';
        noResults.classList.remove('hidden');
        return;
      }

      noResults.classList.add('hidden');
      grid.innerHTML = filtered.map(p => {
        const isFav = favorites.includes(p.id);
        return `
          <div class="bg-white rounded-3xl overflow-hidden border border-slate-200/80 shadow-sm hover:shadow-md transition">
            <div class="relative h-48 cursor-pointer" onclick="openModal(${p.id})">
              <img src="${p.image}" alt="${p.title}" class="w-full h-full object-cover">
              <div class="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent"></div>
              
              <span class="absolute top-3 right-3 bg-white/90 backdrop-blur-md text-slate-800 text-[11px] font-bold px-2.5 py-1 rounded-full shadow">
                ${p.categoryName}
              </span>

              <button onclick="event.stopPropagation(); toggleFavorite(${p.id})" 
                      class="absolute top-3 left-3 w-9 h-9 rounded-full bg-white/90 backdrop-blur-md flex items-center justify-center text-slate-400 hover:text-rose-500 transition shadow">
                <i class="fa-solid fa-heart ${isFav ? 'text-rose-500' : ''}"></i>
              </button>

              <div class="absolute bottom-3 right-3 left-3 text-white">
                <div class="flex items-center gap-1.5 text-amber-400 text-xs font-bold mb-0.5">
                  <i class="fa-solid fa-star"></i>
                  <span>${p.rating}</span>
                </div>
                <h3 class="font-extrabold text-lg leading-snug drop-shadow">${p.title}</h3>
              </div>
            </div>

            <div class="p-3.5 flex items-center justify-between text-xs text-slate-500">
              <span class="flex items-center gap-1 text-slate-600 truncate max-w-[200px]">
                <i class="fa-solid fa-location-dot text-emerald-600 text-sm"></i>
                ${p.address}
              </span>
              <button onclick="openModal(${p.id})" class="text-emerald-700 font-bold bg-emerald-50 px-3 py-1.5 rounded-xl hover:bg-emerald-100 transition">
                وردەکاری
              </button>
            </div>
          </div>
        `;
      }).join('');
    }

    // فلتەری پۆلێنەکان
    function filterCategory(cat) {
      currentCategory = cat;
      document.querySelectorAll('.cat-pill').forEach(btn => {
        btn.classList.remove('active', 'bg-emerald-600', 'text-white');
        btn.classList.add('bg-slate-100', 'text-slate-600');
      });
      event.currentTarget.classList.add('active', 'bg-emerald-600', 'text-white');
      event.currentTarget.classList.remove('bg-slate-100', 'text-slate-600');
      renderPlaces();
    }

    // گەڕان
    function handleSearch() {
      const input = document.getElementById('searchInput');
      searchQuery = input.value.trim();
      document.getElementById('clearSearchBtn').classList.toggle('hidden', searchQuery === '');
      renderPlaces();
    }

    function clearSearch() {
      document.getElementById('searchInput').value = '';
      searchQuery = '';
      document.getElementById('clearSearchBtn').classList.add('hidden');
      renderPlaces();
    }

    // مۆداڵی وردەکاری
    function openModal(id) {
      const place = placesData.find(p => p.id === id);
      if (!place) return;

      currentPlaceForAudio = place;
      document.getElementById('modalImg').src = place.image;
      document.getElementById('modalTitle').innerText = place.title;
      document.getElementById('modalCategoryBadge').innerText = place.categoryName;
      document.getElementById('modalLocationName').innerText = place.address;
      document.getElementById('modalDesc').innerText = place.desc;
      
      const navBtn = document.getElementById('modalNavBtn');
      navBtn.href = `https://www.google.com/maps/dir/?api=1&destination=${place.lat},${place.lng}`;

      const favBtn = document.getElementById('modalFavBtn');
      const isFav = favorites.includes(place.id);
      favBtn.innerHTML = `<i class="fa-solid fa-heart ${isFav ? 'text-rose-500' : 'text-slate-300'}"></i>`;
      favBtn.onclick = () => {
        toggleFavorite(place.id);
        const updatedFav = favorites.includes(place.id);
        favBtn.innerHTML = `<i class="fa-solid fa-heart ${updatedFav ? 'text-rose-500' : 'text-slate-300'}"></i>`;
      };

      // ئامادەکردنی دەنگ
      stopSpeech();
      document.getElementById('audioStatus').innerText = "ئامادەیە";

      document.getElementById('detailsModal').classList.remove('hidden');
    }

    function closeModal() {
      stopSpeech();
      document.getElementById('detailsModal').classList.add('hidden');
    }

    // دڵخوازەکان (Favorites)
    function toggleFavorite(id) {
      if (favorites.includes(id)) {
        favorites = favorites.filter(item => item !== id);
      } else {
        favorites.push(id);
      }
      localStorage.setItem('kirkuk_favorites', JSON.stringify(favorites));
      updateFavBadge();
      renderPlaces();
      renderFavoritesList();
    }

    function updateFavBadge() {
      const badge = document.getElementById('navFavBadge');
      if (favorites.length > 0) {
        badge.innerText = favorites.length;
        badge.classList.remove('hidden');
      } else {
        badge.classList.add('hidden');
      }
    }

    function renderFavoritesList() {
      const list = document.getElementById('favoritesList');
      const empty = document.getElementById('emptyFavorites');
      const count = document.getElementById('favCount');
      
      const favPlaces = placesData.filter(p => favorites.includes(p.id));
      count.innerText = `${favPlaces.length} شوێن`;

      if (favPlaces.length === 0) {
        list.innerHTML = '';
        empty.classList.remove('hidden');
        return;
      }

      empty.classList.add('hidden');
      list.innerHTML = favPlaces.map(p => `
        <div class="flex gap-3 bg-white p-3 rounded-2xl border border-slate-200 shadow-sm items-center">
          <img src="${p.image}" class="w-20 h-20 rounded-xl object-cover">
          <div class="flex-1">
            <h4 class="font-bold text-sm text-slate-900">${p.title}</h4>
            <p class="text-xs text-slate-500 line-clamp-1 mt-0.5">${p.address}</p>
            <div class="flex items-center gap-2 mt-2">
              <button onclick="openModal(${p.id})" class="text-[11px] bg-emerald-50 text-emerald-700 font-bold px-3 py-1 rounded-lg">بینیین</button>
              <button onclick="toggleFavorite(${p.id})" class="text-[11px] text-rose-500 hover:underline">سڕینەوە</button>
            </div>
          </div>
        </div>
      `).join('');
    }

    // بەشی ڕێبەری دەنگی (Speech Synthesis)
    let isSpeaking = false;
    function toggleAudioGuide() {
      if (!currentPlaceForAudio) return;

      if (isSpeaking) {
        stopSpeech();
      } else {
        startSpeech(currentPlaceForAudio.title + ". " + currentPlaceForAudio.desc);
      }
    }

    function startSpeech(text) {
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'ar-IQ'; // نزیکترین فۆنەتیک بۆ دەنگە کوردییەکە
        utterance.rate = 0.9;
        
        utterance.onstart = () => {
          isSpeaking = true;
          document.getElementById('audioStatus').innerText = "پەخش دەکرێت...";
          document.getElementById('audioIcon').classList.replace('fa-volume-high', 'fa-pause');
        };
        utterance.onend = () => {
          stopSpeech();
        };
        utterance.onerror = () => {
          stopSpeech();
        };
        window.speechSynthesis.speak(utterance);
      } else {
        alert("وێبگەڕەکەت پشتگیری خوێندنەوەی دەنگ ناکات");
      }
    }

    function stopSpeech() {
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
      }
      isSpeaking = false;
      const status = document.getElementById('audioStatus');
      const icon = document.getElementById('audioIcon');
      if (status) status.innerText = "ئامادەیە";
      if (icon) icon.classList.replace('fa-pause', 'fa-volume-high');
    }

    // بەشی نەخشەی Leaflet.js
    function initMap() {
      if (leafletMap) return;

      leafletMap = L.map('leafletMap', {
        zoomControl: false
      }).setView([35.4688, 44.3920], 12);

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap'
      }).addTo(leafletMap);

      markersLayer = L.layerGroup().addTo(leafletMap);

      placesData.forEach(p => {
        const marker = L.circleMarker([p.lat, p.lng], {
          radius: 8,
          fillColor: '#10b981',
          color: '#ffffff',
          weight: 2,
          opacity: 1,
          fillOpacity: 0.9
        }).addTo(markersLayer);

        marker.on('click', () => {
          showMapFloatingCard(p);
        });
      });
    }

    function showMapFloatingCard(place) {
      const card = document.getElementById('mapFloatingCard');
      document.getElementById('mapCardImg').src = place.image;
      document.getElementById('mapCardTitle').innerText = place.title;
      document.getElementById('mapCardDesc').innerText = place.desc;
      
      const navBtn = document.getElementById('mapCardNavBtn');
      navBtn.onclick = () => window.open(`https://www.google.com/maps/dir/?api=1&destination=${place.lat},${place.lng}`, '_blank');
      
      const detailsBtn = document.getElementById('mapCardDetailsBtn');
      detailsBtn.onclick = () => openModal(place.id);

      card.classList.remove('hidden');
    }

    function closeMapCard() {
      document.getElementById('mapFloatingCard').classList.add('hidden');
    }

    // گۆڕینی تابەکان لە مێنیوی خوارەوە
    function switchTab(tabId) {
      const views = ['places', 'map', 'favorites', 'about'];
      views.forEach(v => {
        document.getElementById(`view-${v}`).classList.add('hidden');
        const navBtn = document.getElementById(`nav-${v}`);
        navBtn.classList.remove('text-emerald-600');
        navBtn.classList.add('text-slate-400');
      });

      document.getElementById(`view-${tabId}`).classList.remove('hidden');
      const activeNav = document.getElementById(`nav-${tabId}`);
      activeNav.classList.add('text-emerald-600');
      activeNav.classList.remove('text-slate-400');

      if (tabId === 'map') {
        setTimeout(() => {
          initMap();
          leafletMap.invalidateSize();
        }, 150);
      } else if (tabId === 'favorites') {
        renderFavoritesList();
      }
    }
  </script>
</body>
</html>
