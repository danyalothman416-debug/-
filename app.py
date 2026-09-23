<!DOCTYPE html>
<html lang="ku" dir="rtl" class="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ڕێبەری کەرکووک | Kirkuk Guide</title>
  <!-- ستایلی مۆدێرنی Tailwind CSS و ئایکۆنەکان -->
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
  <!-- فۆنتی کوردی و عەرەبی مۆدێرن -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;600;700;800;900&display=swap" rel="stylesheet">

  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          fontFamily: {
            sans: ['Vazirmatn', 'Segoe UI', 'Tahoma', 'sans-serif'],
          },
          colors: {
            brand: {
              50: '#f0f9ff',
              100: '#e0f2fe',
              500: '#0ea5e9',
              600: '#0284c7',
              700: '#0369a1',
            }
          }
        }
      }
    }
  </script>
  <style>
    body { font-family: 'Vazirmatn', sans-serif; }
    .hide-scrollbar::-webkit-scrollbar { display: none; }
    .hide-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
  </style>
</head>
<body class="bg-slate-50 text-slate-800 dark:bg-slate-950 dark:text-slate-100 min-h-screen transition-colors duration-300">

  <!-- سەرپەڕە و ناڤبار (Navigation Bar) -->
  <header class="sticky top-0 z-40 bg-white/90 dark:bg-slate-900/90 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 transition-colors">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-20">
        
        <!-- لۆگۆ -->
        <div class="flex items-center gap-3 cursor-pointer" onclick="switchTab('home')">
          <div class="w-12 h-12 rounded-2xl bg-gradient-to-tr from-brand-600 to-amber-500 flex items-center justify-center text-white text-2xl shadow-lg shadow-brand-500/20">
            <i class="fa-solid fa-monument"></i>
          </div>
          <div>
            <h1 class="text-2xl font-black tracking-tight text-slate-900 dark:text-white flex items-center gap-2">
              ڕێبەری کەرکووک
              <span class="text-xs bg-brand-100 text-brand-700 dark:bg-brand-900/40 dark:text-brand-300 px-2 py-0.5 rounded-full font-bold">پڕۆ</span>
            </h1>
            <p class="text-xs text-slate-500 dark:text-slate-400 font-medium">دەروازەی تەواوی شار و گەڕەکەکان</p>
          </div>
        </div>

        <!-- گەڕانی ناوەندی سەرپەڕە -->
        <div class="hidden md:flex flex-1 max-w-md mx-8">
          <div class="relative w-full">
            <input type="text" id="globalSearch" oninput="handleSearch(this.value)" placeholder="گەڕان بۆ هەر شوێنێک، گەڕەکێک یان ڕێستۆرانتێک..." class="w-full bg-slate-100 dark:bg-slate-800/80 text-sm rounded-full pl-4 pr-11 py-2.5 outline-none border border-transparent focus:border-brand-500 focus:bg-white dark:focus:bg-slate-900 transition-all">
            <i class="fa-solid fa-magnifying-glass absolute right-4 top-3 text-slate-400"></i>
          </div>
        </div>

        <!-- دوگمە کردارەکان (Dark mode, Favorites, Admin) -->
        <div class="flex items-center gap-2">
          <!-- دڵخوازەکان -->
          <button onclick="switchTab('favorites')" class="relative p-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:text-red-500 transition-colors" title="دڵخوازەکانم">
            <i class="fa-solid fa-heart"></i>
            <span id="favCount" class="absolute -top-1 -right-1 bg-red-500 text-white text-[10px] font-bold w-4 h-4 rounded-full flex items-center justify-center">0</span>
          </button>

          <!-- دۆخی تاریک و ڕووناک -->
          <button onclick="toggleDarkMode()" class="p-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:text-amber-500 transition-colors" title="گۆڕینی ڕەنگ">
            <i id="themeIcon" class="fa-solid fa-moon"></i>
          </button>

          <!-- ئەدمین پانێڵ -->
          <button onclick="openAdminModal()" class="flex items-center gap-2 bg-brand-600 hover:bg-brand-700 text-white px-4 py-2 rounded-xl text-sm font-bold shadow-md shadow-brand-500/20 transition-all">
            <i class="fa-solid fa-gear"></i>
            <span class="hidden sm:inline">بەڕێوەبردن (Admin)</span>
          </button>
        </div>

      </div>
    </div>

    <!-- مێنیوی پۆلە سەرەکییەکان (Horizontal Scroll Bar) -->
    <div class="border-t border-slate-100 dark:border-slate-800/80 bg-white/50 dark:bg-slate-900/50">
      <div class="max-w-7xl mx-auto px-4 overflow-x-auto hide-scrollbar py-2.5 flex items-center gap-2">
        <button onclick="switchTab('home')" class="nav-tab active-tab px-4 py-1.5 rounded-full text-sm font-bold whitespace-nowrap transition-all flex items-center gap-2" data-tab="home">
          <i class="fa-solid fa-house"></i> سەرەتا
        </button>
        <button onclick="switchTab('neighborhoods')" class="nav-tab px-4 py-1.5 rounded-full text-sm font-bold whitespace-nowrap text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-all flex items-center gap-2" data-tab="neighborhoods">
          <i class="fa-solid fa-map-location-dot"></i> گەڕەکەکان
        </button>
        <button onclick="switchTab('fun')" class="nav-tab px-4 py-1.5 rounded-full text-sm font-bold whitespace-nowrap text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-all flex items-center gap-2" data-tab="fun">
          <i class="fa-solid fa-tree"></i> شوێنە خۆشەکان
        </button>
        <button onclick="switchTab('historic')" class="nav-tab px-4 py-1.5 rounded-full text-sm font-bold whitespace-nowrap text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-all flex items-center gap-2" data-tab="historic">
          <i class="fa-solid fa-landmark"></i> مێژوویی و قەڵا
        </button>
        <button onclick="switchTab('food')" class="nav-tab px-4 py-1.5 rounded-full text-sm font-bold whitespace-nowrap text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-all flex items-center gap-2" data-tab="food">
          <i class="fa-solid fa-utensils"></i> خواردن و ڕێستۆرانت
        </button>
        <button onclick="switchTab('market')" class="nav-tab px-4 py-1.5 rounded-full text-sm font-bold whitespace-nowrap text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-all flex items-center gap-2" data-tab="market">
          <i class="fa-solid fa-bag-shopping"></i> بازاڕ و مۆڵ
        </button>
        <button onclick="switchTab('services')" class="nav-tab px-4 py-1.5 rounded-full text-sm font-bold whitespace-nowrap text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-all flex items-center gap-2" data-tab="services">
          <i class="fa-solid fa-kit-medical"></i> خزمەتگوزاری و فریاکەوتن
        </button>
        <button onclick="switchTab('events')" class="nav-tab px-4 py-1.5 rounded-full text-sm font-bold whitespace-nowrap text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-all flex items-center gap-2" data-tab="events">
          <i class="fa-solid fa-calendar-star"></i> ڕووداوەکان
        </button>
      </div>
    </div>
  </header>

  <!-- ناوەڕۆکی سەرەکی (Main Container) -->
  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

    <!-- بەشی هێرۆ (Hero Banner) - تایبەت بە پەڕەی سەرەتا -->
    <div id="heroSection" class="relative rounded-3xl overflow-hidden mb-12 shadow-2xl bg-slate-900 border border-slate-800">
      <img src="https://images.unsplash.com/photo-1541872703-74c5e44368f9?auto=format&fit=crop&w=1400&q=80" alt="قەڵای کەرکووک" class="w-full h-80 object-cover opacity-40">
      <div class="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/50 to-transparent flex flex-col justify-end p-6 sm:p-10">
        <span class="inline-flex items-center gap-2 bg-amber-500/20 text-amber-300 border border-amber-500/30 text-xs font-bold px-3 py-1 rounded-full mb-3 w-fit">
          <i class="fa-solid fa-fire"></i> پایتەختی کلتوور و پێکەوەژیان
        </span>
        <h2 class="text-3xl sm:text-5xl font-black text-white mb-2 leading-tight">بەخێربێن بۆ شاری کەرکووک</h2>
        <p class="text-slate-300 text-sm sm:text-base max-w-2xl font-light mb-6">دەستپێکی گەشتەکەت بەناو دێرینترین گەڕەکەکان، خۆشترین کافێ و ڕێستۆرانتەکان، و پڕشکۆترین شوێنەوارەکانی شارەکەدا.</p>
        
        <!-- ئاماری خێرا -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-4 border-t border-white/10 text-white">
          <div>
            <div class="text-xl sm:text-2xl font-black text-brand-400">١٥+</div>
            <div class="text-xs text-slate-400">گەڕەکی سەرەکی</div>
          </div>
          <div>
            <div class="text-xl sm:text-2xl font-black text-amber-400">٥٠٠٠+ ساڵ</div>
            <div class="text-xs text-slate-400">مێژووی قەڵا</div>
          </div>
          <div>
            <div class="text-xl sm:text-2xl font-black text-emerald-400">٢٤/٧</div>
            <div class="text-xs text-slate-400">فریاگوزاری و خزمەت</div>
          </div>
          <div>
            <div class="text-xl sm:text-2xl font-black text-purple-400">١٠٠٪</div>
            <div class="text-xs text-slate-400">بە زمانی کوردی</div>
          </div>
        </div>
      </div>
    </div>

    <!-- ناونیشانی بەشی هەڵبژێردراو -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h3 id="sectionTitle" class="text-2xl font-black text-slate-900 dark:text-white flex items-center gap-2">
          <span>🌟 شوێنە پڕبینراوەکان</span>
        </h3>
        <p id="sectionDesc" class="text-sm text-slate-500 dark:text-slate-400 mt-1">تەواوی شوێنە دەستنیشانکراوەکانی کەرکووک بە زانیاری ورد</p>
      </div>
    </div>

    <!-- تۆڕی کاردەکان (Cards Grid) -->
    <div id="cardsGrid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <!-- کاردەکان لە ڕێگەی جاڤاسکریپتەوە دروست دەکرێن -->
    </div>

    <!-- باری بەتاڵ (Empty State) -->
    <div id="emptyState" class="hidden text-center py-20">
      <div class="w-20 h-20 mx-auto rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-3xl text-slate-400 mb-4">
        <i class="fa-solid fa-magnifying-glass"></i>
      </div>
      <h4 class="text-lg font-bold text-slate-800 dark:text-slate-200">هیچ ئەنجامێک نەدۆزرایەوە!</h4>
      <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">وشەیەکی تر یان پۆلێنێکی جیاواز تاقی بکەرەوە.</p>
    </div>

  </main>

  <!-- مۆداڵی زیادکردنی شوێن لەلایەن ئەدمینەوە (Admin Modal) -->
  <div id="adminModal" class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm hidden flex items-center justify-center p-4">
    <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6 sm:p-8 shadow-2xl">
      <div class="flex items-center justify-between pb-4 border-b border-slate-100 dark:border-slate-800 mb-6">
        <h3 class="text-xl font-black text-slate-900 dark:text-white flex items-center gap-2">
          <i class="fa-solid fa-sliders text-brand-600"></i> داشبۆردی بەڕێوەبەر (Admin)
        </h3>
        <button onclick="closeAdminModal()" class="text-slate-400 hover:text-slate-600 dark:hover:text-white text-xl">
          <i class="fa-solid fa-xmark"></i>
        </button>
      </div>

      <form id="placeForm" onsubmit="handleFormSubmit(event)" class="space-y-4">
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-bold text-slate-600 dark:text-slate-300 mb-1">ناوی شوێن / گەڕەک</label>
            <input type="text" id="formName" required placeholder="بۆ نموونە: قەڵای کەرکووک" class="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-brand-500">
          </div>
          <div>
            <label class="block text-xs font-bold text-slate-600 dark:text-slate-300 mb-1">پۆلێن (Category)</label>
            <select id="formCategory" class="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-brand-500">
              <option value="neighborhoods">گەڕەک</option>
              <option value="historic">مێژوویی</option>
              <option value="fun">پارک و سەیران</option>
              <option value="food">خواردن و ڕێستۆرانت</option>
              <option value="market">بازاڕ و مۆڵ</option>
              <option value="services">فریاگوزاری و خزمەت</option>
              <option value="events">ڕووداو و چالاکی</option>
            </select>
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-bold text-slate-600 dark:text-slate-300 mb-1">ناونیشان</label>
            <input type="text" id="formAddress" required placeholder="بۆ نموونە: سەنتەری شار" class="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-brand-500">
          </div>
          <div>
            <label class="block text-xs font-bold text-slate-600 dark:text-slate-300 mb-1">پلە / ڕەیتینگ (١ بۆ ٥)</label>
            <input type="number" step="0.1" min="1" max="5" id="formRating" value="4.8" class="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-brand-500">
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-bold text-slate-600 dark:text-slate-300 mb-1">ژمارەی پەیوەندی (ئارەزوومەندانە)</label>
            <input type="text" id="formPhone" placeholder="0770xxxxxxx" class="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-brand-500">
          </div>
          <div>
            <label class="block text-xs font-bold text-slate-600 dark:text-slate-300 mb-1">لینکی وێنە (Image URL)</label>
            <input type="url" id="formImage" placeholder="https://example.com/image.jpg" class="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-brand-500">
          </div>
        </div>

        <div>
          <label class="block text-xs font-bold text-slate-600 dark:text-slate-300 mb-1">دەربارەی شوێنەکە</label>
          <textarea id="formDesc" rows="3" required placeholder="کورتەیەک لەسەر مێژوو یان خزمەتگوزارییەکانی ئەم شوێنە..." class="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl p-4 text-sm outline-none focus:border-brand-500"></textarea>
        </div>

        <div class="flex items-center justify-end gap-3 pt-4 border-t border-slate-100 dark:border-slate-800">
          <button type="button" onclick="closeAdminModal()" class="px-5 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 text-sm font-bold text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800">داخستن</button>
          <button type="submit" class="px-6 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white text-sm font-bold shadow-md shadow-brand-500/20">زیادکردنی شوێنەکە</button>
        </div>
      </form>
    </div>
  </div>

  <!-- بنپەڕە (Footer) -->
  <footer class="border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 mt-20 py-8 text-center text-sm text-slate-500 dark:text-slate-400">
    <p>کەرکووک ڕێبەر © هەموو مافەکان پارێزراون بۆ دانیال</p>
    <p class="text-xs mt-1 text-slate-400">دروستکراوە بە خۆشەویستییەوە بۆ پایتەختی کلتووری کوردستان</p>
  </footer>

  <!-- جاڤاسکریپتی سەرەکی بەرنامەکە -->
  <script>
    // داتای سەرەتایی (Initial Data)
    const defaultData = [
      {
        id: 1,
        name: "قەڵای کەرکووک",
        category: "historic",
        rating: 4.9,
        image: "https://images.unsplash.com/photo-1541872703-74c5e44368f9?auto=format&fit=crop&w=800&q=80",
        desc: "کۆنترین هێمای مێژوویی شارەکە کە تەمەنی بۆ زیاتر لە پێنج هەزار ساڵ لەمەوبەر دەگەڕێتەوە و دەڕوانێت بەسەر تەواوی شارەکەدا.",
        address: "سەنتەری شاری کەرکووک",
        phone: "",
        map: "https://maps.google.com/?q=Kirkuk+Citadel"
      },
      {
        id: 2,
        name: "گەڕەکی ڕەحیماوا",
        category: "neighborhoods",
        rating: 4.8,
        image: "https://images.unsplash.com/photo-1519501025264-65ba15a82390?auto=format&fit=crop&w=800&q=80",
        desc: "یەکێک لە گەورەترین و زیندووترین گەڕەکەکانی شار، بە بازاڕە قەرەباڵغەکەی و خواردنە میللییە بەتامەکانی ناسراوە.",
        address: "باکووری شاری کەرکووک",
        phone: "",
        map: "https://maps.google.com/?q=Rahimawa+Kirkuk"
      },
      {
        id: 3,
        name: "گەڕەکی شۆرجە",
        category: "neighborhoods",
        rating: 4.7,
        image: "https://images.unsplash.com/photo-1477959858617-67f30bc75b82?auto=format&fit=crop&w=800&q=80",
        desc: "گەڕەکێکی دێرین و بازرگانیی کەرکووک کە پێگەیەکی جوگرافی و مێژوویی تایبەتی لە شارەکەدا هەیە.",
        address: "ناوەندی کەرکووک",
        phone: "",
        map: "https://maps.google.com/?q=Shorja+Kirkuk"
      },
      {
        id: 4,
        name: "گەڕەکی ئەڵماس",
        category: "neighborhoods",
        rating: 4.8,
        image: "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=800&q=80",
        desc: "ناوچەیەکی مۆدێرن کە بە دەرمانخانە، نۆرینگە، کافێ هاوچەرخەکان و ناوەندی کڕینی مۆبایل بەناوبانگە.",
        address: "ناوەندی شار",
        phone: "",
        map: "https://maps.google.com/?q=Almas+Kirkuk"
      },
      {
        id: 5,
        name: "پارکی گشتی (باخچەی شار)",
        category: "fun",
        rating: 4.6,
        image: "https://images.unsplash.com/photo-1519331379826-f10be5486c6f?auto=format&fit=crop&w=800&q=80",
        desc: "گەورەترین شوێنی سەوزایی لە دڵی کەرکووک بۆ پشوودان، پیاسەی ئێواران و کات بەسەربردنی خێزانەکان.",
        address: "شەقامی سەرەکی شار",
        phone: "",
        map: "https://maps.google.com/?q=Kirkuk+Public+Park"
      },
      {
        id: 6,
        name: "کۆڕنیشی خاسە",
        category: "fun",
        rating: 4.5,
        image: "https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?auto=format&fit=crop&w=800&q=80",
        desc: "شەقامێکی جوان بە درێژایی ڕووباری خاسە پڕ لە کافێ و شوێنی پیاسەکردن لە کاتەکانی ئێوارە و شەواندا.",
        address: "کەناری ڕووباری خاسە",
        phone: "",
        map: "https://maps.google.com/?q=Khasa+River+Kirkuk"
      },
      {
        id: 7,
        name: "بازاڕی قەیسەری کۆن",
        category: "historic",
        rating: 4.9,
        image: "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=800&q=80",
        desc: "بازاڕێکی کەلەپووری مێژوویی سەرپۆشراو بە تاقی بەردین کە مێژووەکەی دەگەڕێتەوە بۆ سەردەمی عوسمانییەکان.",
        address: "بەرامبەر قەڵای کەرکووک",
        phone: "",
        map: "https://maps.google.com/?q=Qaisariya+Bazaar+Kirkuk"
      },
      {
        id: 8,
        name: "چێشتخانەی کەبابی خاسە",
        category: "food",
        rating: 4.9,
        image: "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?auto=format&fit=crop&w=800&q=80",
        desc: "بەناوبانگترین کەبابی کەرکووک بە گۆشتی تازە و لەسەر خەڵووز لەگەڵ ترشیات و نانی گەرم پێشکەش دەکرێت.",
        address: "شەقامی قەڵا",
        phone: "07701234567",
        map: "https://maps.google.com/?q=Kirkuk+Kebab"
      },
      {
        id: 9,
        name: "کەرکووک مۆڵ (Kirkuk Mall)",
        category: "market",
        rating: 4.7,
        image: "https://images.unsplash.com/photo-1567449303078-57ad995bd301?auto=format&fit=crop&w=800&q=80",
        desc: "ناوەندێکی بازاڕکردنی پێشکەوتوو بە براندە جیهانییەکان، سینەمای نوێ، شوێنی یاری منداڵان و چێشتخانەکان.",
        address: "شەقامی ڕێگای بەغدا",
        phone: "07709876543",
        map: "https://maps.google.com/?q=Kirkuk+Mall"
      },
      {
        id: 10,
        name: "نەخۆشخانەی ئازادی فێرکاری",
        category: "services",
        rating: 4.5,
        image: "https://images.unsplash.com/photo-1587351021759-3e566b6af7cc?auto=format&fit=crop&w=800&q=80",
        desc: "گەورەترین ناوەندی پزیشکی و نەخۆشخانەی فریاکەوتنی گشتی لە کەرکووک بە خزمەتگوزاری ٢٤ کاتژمێری.",
        address: "گەڕەکی ئازادی",
        phone: "122",
        map: "https://maps.google.com/?q=Azadi+Hospital+Kirkuk"
      },
      {
        id: 11,
        name: "فیستیڤاڵی کلتووری نەورۆز لە قەڵا",
        category: "events",
        rating: 5.0,
        image: "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=800&q=80",
        desc: "بۆنەیەکی جەماوەری بە ئامادەبوونی هەزاران هاوڵاتی بە هەڵکردنی ئاگری نەورۆز و مۆسیقای فۆلکلۆری.",
        address: "سەر تەپۆڵکەی قەڵا",
        phone: "",
        map: "https://maps.google.com/?q=Kirkuk+Citadel"
      }
    ];

    // بارکردنی داتا لە localStorage
    let places = JSON.parse(localStorage.getItem('kirkuk_places')) || defaultData;
    let favorites = JSON.parse(localStorage.getItem('kirkuk_favs')) || [];
    let currentTab = 'home';
    let searchQuery = '';

    // دۆخی تاریک
    function toggleDarkMode() {
      const html = document.documentElement;
      const icon = document.getElementById('themeIcon');
      if (html.classList.contains('dark')) {
        html.classList.remove('dark');
        icon.classList.replace('fa-sun', 'fa-moon');
        localStorage.setItem('theme', 'light');
      } else {
        html.classList.add('dark');
        icon.classList.replace('fa-moon', 'fa-sun');
        localStorage.setItem('theme', 'dark');
      }
    }
    if (localStorage.getItem('theme') === 'dark') toggleDarkMode();

    // گۆڕینی بەشەکان (Tab Switching)
    function switchTab(tabId) {
      currentTab = tabId;
      document.querySelectorAll('.nav-tab').forEach(b => {
        b.classList.remove('bg-brand-600', 'text-white', 'shadow-md');
        b.classList.add('text-slate-600', 'dark:text-slate-400');
        if (b.dataset.tab === tabId) {
          b.classList.add('bg-brand-600', 'text-white', 'shadow-md');
          b.classList.remove('text-slate-600', 'dark:text-slate-400');
        }
      });

      const hero = document.getElementById('heroSection');
      const title = document.getElementById('sectionTitle');
      const desc = document.getElementById('sectionDesc');

      if (tabId === 'home') {
        hero.classList.remove('hidden');
        title.innerHTML = `<span>🌟 شوێنە پڕبینراوەکان</span>`;
        desc.innerText = "تەواوی شوێنە دەستنیشانکراوەکانی کەرکووک بە زانیاری ورد";
      } else {
        hero.classList.add('hidden');
        const titles = {
          neighborhoods: ["🗺️ گەڕەکەکانی کەرکووک", "ناساندنی هەموو گەڕەکە سەرەکی و دێرینەکان"],
          historic: ["🏛️ شوێنەوار و مێژوو", "قەڵا، پرد و بازاڕە کۆنەکانی شار"],
          fun: ["📍 پارک و شوێنی سەیران", "خۆشترین شوێنەکانی پشوودان و کافێکان"],
          food: ["🍽️ خواردن و ڕێستۆرانت", "کەباب، خواردنگەی خێرا و چێشتخانە بەناوبانگەکان"],
          market: ["🏪 بازاڕ و مۆڵەکان", "ناوەندەکانی کڕین، جلوبەرگ و ئەلیکترۆنیات"],
          services: ["🚑 خزمەتگوزاری و فریاکەوتن", "نەخۆشخانەکان، ژمارەی پۆلیس و فریاکەوتن"],
          events: ["📅 ڕووداو و فیستیڤاڵەکان", "بۆنە کلتوورییەکان و چالاکییەکانی شار"],
          favorites: ["❤️ دڵخوازەکانم", "ئەو شوێنانەی خۆت نیشانت کردوون"]
        };
        title.innerHTML = `<span>${titles[tabId][0]}</span>`;
        desc.innerText = titles[tabId][1];
      }
      renderCards();
    }

    // گەڕان
    function handleSearch(val) {
      searchQuery = val.trim().toLowerCase();
      renderCards();
    }

    // دڵخوازەکان (Favorites Toggle)
    function toggleFav(id, e) {
      e.stopPropagation();
      if (favorites.includes(id)) {
        favorites = favorites.filter(fId => fId !== id);
      } else {
        favorites.push(id);
      }
      localStorage.setItem('kirkuk_favs', JSON.stringify(favorites));
      updateFavBadge();
      renderCards();
    }

    function updateFavBadge() {
      document.getElementById('favCount').innerText = favorites.length;
    }

    // پیشاندانی کاردەکان
    function renderCards() {
      const grid = document.getElementById('cardsGrid');
      const empty = document.getElementById('emptyState');
      grid.innerHTML = '';

      let list = places;

      if (currentTab === 'favorites') {
        list = list.filter(item => favorites.includes(item.id));
      } else if (currentTab !== 'home') {
        list = list.filter(item => item.category === currentTab);
      }

      if (searchQuery) {
        list = list.filter(item => 
          item.name.toLowerCase().includes(searchQuery) ||
          item.desc.toLowerCase().includes(searchQuery) ||
          item.address.toLowerCase().includes(searchQuery)
        );
      }

      if (list.length === 0) {
        empty.classList.remove('hidden');
      } else {
        empty.classList.add('hidden');
        list.forEach(item => {
          const isFav = favorites.includes(item.id);
          const card = document.createElement('div');
          card.className = "bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 flex flex-col justify-between group";
          
          card.innerHTML = `
            <div>
              <div class="relative h-48 overflow-hidden bg-slate-100 dark:bg-slate-800">
                <img src="${item.image || 'https://images.unsplash.com/photo-1541872703-74c5e44368f9?auto=format&fit=crop&w=800&q=80'}" alt="${item.name}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500">
                <button onclick="toggleFav(${item.id}, event)" class="absolute top-3 left-3 w-9 h-9 rounded-full bg-white/80 dark:bg-slate-900/80 backdrop-blur-md flex items-center justify-center text-sm ${isFav ? 'text-red-500' : 'text-slate-400 hover:text-red-500'} transition-colors">
                  <i class="fa-solid fa-heart"></i>
                </button>
                <div class="absolute bottom-3 right-3 bg-black/60 backdrop-blur-md text-amber-300 text-xs font-bold px-2.5 py-1 rounded-full flex items-center gap-1">
                  <i class="fa-solid fa-star text-[10px]"></i> ${item.rating}
                </div>
              </div>
              <div class="p-5">
                <h4 class="text-lg font-black text-slate-900 dark:text-white mb-1">${item.name}</h4>
                <p class="text-xs text-brand-600 dark:text-brand-400 font-bold mb-3 flex items-center gap-1">
                  <i class="fa-solid fa-location-dot"></i> ${item.address}
                </p>
                <p class="text-xs leading-relaxed text-slate-500 dark:text-slate-400 line-clamp-3">${item.desc}</p>
              </div>
            </div>
            
            <div class="p-5 pt-0 border-t border-slate-100 dark:border-slate-800/60 mt-4 flex items-center justify-between gap-2">
              <a href="${item.map || 'https://maps.google.com/?q=' + encodeURIComponent(item.name + ' Kirkuk')}" target="_blank" class="flex-1 text-center bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 text-xs font-bold py-2.5 rounded-xl transition-colors flex items-center justify-center gap-1.5">
                <i class="fa-solid fa-map"></i> نەخشە
              </a>
              ${item.phone ? `
                <a href="tel:${item.phone}" class="p-2.5 bg-emerald-50 hover:bg-emerald-100 text-emerald-600 dark:bg-emerald-950/40 dark:text-emerald-400 rounded-xl text-xs font-bold transition-colors" title="پەیوەندی">
                  <i class="fa-solid fa-phone"></i>
                </a>
              ` : ''}
              <button onclick="deletePlace(${item.id})" class="p-2.5 text-slate-400 hover:text-red-500 rounded-xl text-xs transition-colors" title="سڕینەوەی ئەم شوێنە">
                <i class="fa-solid fa-trash-can"></i>
              </button>
            </div>
          `;
          grid.appendChild(card);
        });
      }
    }

    // کردارەکانی ئەدمین (Admin Functions)
    function openAdminModal() {
      document.getElementById('adminModal').classList.remove('hidden');
    }
    function closeAdminModal() {
      document.getElementById('adminModal').classList.add('hidden');
    }

    function handleFormSubmit(e) {
      e.preventDefault();
      const newPlace = {
        id: Date.now(),
        name: document.getElementById('formName').value,
        category: document.getElementById('formCategory').value,
        address: document.getElementById('formAddress').value,
        rating: parseFloat(document.getElementById('formRating').value) || 4.8,
        phone: document.getElementById('formPhone').value,
        image: document.getElementById('formImage').value || 'https://images.unsplash.com/photo-1541872703-74c5e44368f9?auto=format&fit=crop&w=800&q=80',
        desc: document.getElementById('formDesc').value,
        map: `https://maps.google.com/?q=${encodeURIComponent(document.getElementById('formName').value + ' Kirkuk')}`
      };

      places.unshift(newPlace);
      localStorage.setItem('kirkuk_places', JSON.stringify(places));
      closeAdminModal();
      document.getElementById('placeForm').reset();
      renderCards();
      alert("شوێنەکە بە سەرکەوتوویی لە کەرکووک زیادکرا! 🎉");
    }

    function deletePlace(id) {
      if (confirm("ئایا دڵنیایت دەتەوێت ئەم شوێنە بسڕیتەوە؟")) {
        places = places.filter(p => p.id !== id);
        localStorage.setItem('kirkuk_places', JSON.stringify(places));
        renderCards();
      }
    }

    // دەستپێکردن
    updateFavBadge();
    renderCards();
  </script>
</body>
</html>
