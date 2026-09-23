<!DOCTYPE html>
<html lang="ku" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ڕێبەری کەرکووک | Kirkuk Guide</title>
  <style>
    :root {
      --bg: #f8fafc;
      --card-bg: #ffffff;
      --primary: #0284c7;
      --primary-light: #e0f2fe;
      --text-main: #0f172a;
      --text-muted: #64748b;
      --border: #e2e8f0;
      --tag-bg: #f1f5f9;
      --radius: 14px;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    body {
      background-color: var(--bg);
      color: var(--text-main);
      padding-bottom: 50px;
    }

    header {
      background: var(--card-bg);
      border-bottom: 1px solid var(--border);
      padding: 24px 20px;
      text-align: center;
      position: sticky;
      top: 0;
      z-index: 100;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
    }

    .header-title {
      font-size: 26px;
      font-weight: 800;
      color: var(--primary);
      margin-bottom: 6px;
    }

    .header-sub {
      font-size: 14px;
      color: var(--text-muted);
      margin-bottom: 18px;
    }

    .search-box {
      max-width: 500px;
      margin: 0 auto;
      position: relative;
    }

    .search-input {
      width: 100%;
      padding: 14px 20px;
      font-size: 16px;
      border: 1.5px solid var(--border);
      border-radius: 50px;
      outline: none;
      background: var(--bg);
      transition: all 0.2s ease;
    }

    .search-input:focus {
      border-color: var(--primary);
      background: #fff;
      box-shadow: 0 0 0 4px var(--primary-light);
    }

    .categories {
      display: flex;
      justify-content: center;
      gap: 8px;
      flex-wrap: wrap;
      margin: 20px auto 10px;
      max-width: 700px;
      padding: 0 15px;
    }

    .cat-btn {
      background: var(--card-bg);
      border: 1px solid var(--border);
      padding: 8px 18px;
      border-radius: 30px;
      font-size: 14px;
      cursor: pointer;
      color: var(--text-muted);
      font-weight: 600;
      transition: all 0.2s;
    }

    .cat-btn.active, .cat-btn:hover {
      background: var(--primary);
      color: #fff;
      border-color: var(--primary);
    }

    .container {
      max-width: 1100px;
      margin: 25px auto;
      padding: 0 16px;
    }

    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 18px;
    }

    .card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 18px;
      transition: transform 0.15s ease, box-shadow 0.15s ease;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }

    .card:hover {
      transform: translateY(-3px);
      box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05);
    }

    .card-top {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 10px;
    }

    .card-title {
      font-size: 18px;
      font-weight: 700;
      color: var(--text-main);
    }

    .badge {
      font-size: 12px;
      padding: 4px 10px;
      border-radius: 20px;
      font-weight: 600;
    }

    .badge-area { background: #fef3c7; color: #b45309; }
    .badge-historic { background: #e0e7ff; color: #4338ca; }
    .badge-fun { background: #dcfce7; color: #15803d; }
    .badge-market { background: #fce7f3; color: #be185d; }

    .card-desc {
      font-size: 14px;
      color: var(--text-muted);
      line-height: 1.6;
      margin-bottom: 14px;
    }

    .card-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-top: 1px solid var(--border);
      padding-top: 10px;
      font-size: 12px;
      color: var(--text-muted);
    }

    .empty-state {
      text-align: center;
      padding: 50px 20px;
      color: var(--text-muted);
      grid-column: 1 / -1;
      font-size: 16px;
    }
  </style>
</head>
<body>

  <header>
    <div class="header-title">🏛️ ڕێبەری شاری کەرکووک</div>
    <div class="header-sub">گەڕان بەناو گەڕەکەکان، شوێنە مێژووییەکان و سەیرانگاکاندا</div>
    
    <div class="search-box">
      <input type="text" id="searchInput" class="search-input" placeholder="ناوی گەڕەک یان شوێنێک بنووسە...">
    </div>

    <div class="categories">
      <button class="cat-btn active" onclick="filterCategory('all')">هەمووی</button>
      <button class="cat-btn" onclick="filterCategory('گەڕەک')">گەڕەکەکان</button>
      <button class="cat-btn" onclick="filterCategory('مێژوویی')">شوێنە مێژووییەکان</button>
      <button class="cat-btn" onclick="filterCategory('پارک و گەشت')">پارک و شوێنی خۆش</button>
      <button class="cat-btn" onclick="filterCategory('مۆڵ و بازاڕ')">مۆڵ و بازاڕ</button>
    </div>
  </header>

  <main class="container">
    <div class="grid" id="placesGrid"></div>
  </main>

  <script>
    const data = [
      // گەڕەکەکان
      { name: "ڕەحیماوا", type: "گەڕەک", badgeClass: "badge-area", desc: "گەڕەکێکی گەورە و بەناوبانگی کەرکووکە؛ بە بازاڕە قەرەباڵغەکەی، کەرەستەی خۆراکی و ژیانی شەوانە ناسراوە.", loc: "باکووری کەرکووک" },
      { name: "شۆرجە", type: "گەڕەک", badgeClass: "badge-area", desc: "گەڕەکێکی دێرین و زیندوو لە سەنتەری شار؛ بازاڕێکی چالاک و فرەجۆری تێدایە.", loc: "ناوەندی شار" },
      { name: "ئیسکان", type: "گەڕەک", badgeClass: "badge-area", desc: "گەڕەکێکی ئارام و ڕێکخراو لە نزیک کۆلێژ و سەنتەری شار، کۆڵانی فراوان و ژینگەیەکی خێزانی هەیە.", loc: "ناوەندی کەرکووک" },
      { name: "ئەڵماس", type: "گەڕەک", badgeClass: "badge-area", desc: "گەڕەکێکی هاوچەرخ و مۆدێرن؛ پڕە لە نۆرینگە، دەرمانخانە، کافێ و خواردنگەی بەناوبانگ.", loc: "ناوەندی شار" },
      { name: "ئیمام قاسم", type: "گەڕەک", badgeClass: "badge-area", desc: "گەڕەکێکی کۆن و مێژوویی کەرکووک کە پێگەیەکی کەلەپووری تایبەتی لە دڵی شارەکەدا هەیە.", loc: "ناوەند و ڕۆژهەڵات" },
      { name: "شۆراو", type: "گەڕەک", badgeClass: "badge-area", desc: "گەڕەکێکی فراوان لە نزیک دەروازەی سەرەکی شار بەرەو هەولێر، بە باڵەخانە و خانووی نوێ ناسراوە.", loc: "باکووری شار" },
      { name: "پەنجا عەلی", type: "گەڕەک", badgeClass: "badge-area", desc: "گەڕەکێکی گەورەی نیشتەجێبوون لە ڕۆژهەڵاتی شار بە ڕووبەرێکی فراوان و خەڵکێکی زۆرەوە.", loc: "ڕۆژهەڵاتی شار" },
      { name: "تسعین", type: "گەڕەک", badgeClass: "badge-area", desc: "گەڕەکێکی ناسراو و دێرین لە سەرەتای ڕێگای بەغدا، کەشێکی هێمن و نیشتەجێبوونی تەواوی هەیە.", loc: "باشووری شار" },
      { name: "قادسیە", type: "گەڕەک", badgeClass: "badge-area", desc: "گەڕەکێکی گەورە و هاوچەرخ لە کەرکووک کە بە چەندین بەش و بازاڕی ناوخۆیی دابەش بووە.", loc: "باشووری ڕۆژهەڵات" },
      { name: "عەرەفە", type: "گەڕەک", badgeClass: "badge-area", desc: "گەڕەکێکی مێژوویی سەر بە کۆمپانیای نەوت؛ بە دیزاینی کلاسیکی ئینگلیزی و باخچەکانی ناسراوە.", loc: "باکووری ڕۆژئاوا" },
      { name: "موسەڵڵا", type: "گەڕەک", badgeClass: "badge-area", desc: "گەڕەکێکی مێژوویی کەلەپووری کۆن بە کۆڵان و تاقی تەقلیدییەوە.", loc: "ناوەندی کەرکووک" },
      { name: "ڕێگای بەغدا", type: "گەڕەک", badgeClass: "badge-area", desc: "شەقام و ناوچەیەکی سەرەکی بازرگانی پڕ لە مۆڵ، پێشانگای سەیارە و ڕێستۆرانت.", loc: "باشووری کەرکووک" },

      // شوێنە مێژوویی و شوێنەوارەکان
      { name: "قەڵای کەرکووک", type: "مێژوویی", badgeClass: "badge-historic", desc: "دێرینترین و دیارترین هێمای شارەکە؛ بەسەر تەواوی شاردا دەڕوانێت و مێژووەکەی بۆ هەزاران ساڵ دەگەڕێتەوە.", loc: "دڵی سەنتەری شار" },
      { name: "بازاڕی قەیسەری کۆن", type: "مێژوویی", badgeClass: "badge-historic", desc: "بازاڕێکی کەلەپووری دێرین بە تاقی بەردین و دوکانی زێڕینگەری و کەرەستەی میللییەوە.", loc: "خوار قەڵا" },
      { name: "پردی بەردین (خاسە)", type: "مێژوویی", badgeClass: "badge-historic", desc: "پردە مێژووییەکەی سەر ڕووباری خاسە کە بەشە دێرینەکانی شاری کەرکووک بەیەکەوە دەبەستێتەوە.", loc: "سەر ڕووباری خاسە" },

      // پارک و شوێنی خۆش
      { name: "باخچەی گشتی (پارکی شار)", type: "پارک و گەشت", badgeClass: "badge-fun", desc: "گەورەترین باخچەی مێژوویی شار بۆ پشوودان، پیاسەکردن و یاری منداڵان لە ناوەندێکی سەوزدا.", loc: "ناوەندی شار" },
      { name: "کۆڕنیشی خاسە", type: "پارک و گەشت", badgeClass: "badge-fun", desc: "شەقامێکی درێژ بە درێژایی ڕووباری خاسە کە ئێواران خەڵک بۆ پیاسەکردن و کافێکان ڕووی تێدەکەن.", loc: "لەنێوان هەردوو دیوی شار" },
      { name: "شاری یاری کەرکووک (سەندباد)", type: "پارک و گەشت", badgeClass: "badge-fun", desc: "شوێنێکی خۆش و گونجاو بۆ خێزان و منداڵان بە چەندین یاریی سەرنجڕاکێشەوە.", loc: "ڕێگای بەغدا" },

      // مۆڵ و بازاڕ
      { name: "کەرکووک مۆڵ (Kirkuk Mall)", type: "مۆڵ و بازاڕ", badgeClass: "badge-market", desc: "ناوەندێکی بازاڕکردنی مۆدێرن بە براندە نێودەوڵەتییەکان، خواردنگەی خێرا و سینەما.", loc: "ڕێگای بەغدا" },
      { name: "تاوەر مۆڵ (Tower Mall)", type: "مۆڵ و بازاڕ", badgeClass: "badge-market", desc: "مۆڵێکی گەورە و سەردەمییانە لە شارەکە بۆ جلوبەرگ، کافێ و کات بەسەربردن.", loc: "گەڕەکی ئیسکان" }
    ];

    let currentCategory = 'all';

    function renderPlaces(filterText = '') {
      const grid = document.getElementById('placesGrid');
      grid.innerHTML = '';

      const filtered = data.filter(item => {
        const matchesCategory = currentCategory === 'all' || item.type === currentCategory;
        const matchesSearch = item.name.includes(filterText) || item.desc.includes(filterText) || item.loc.includes(filterText);
        return matchesCategory && matchesSearch;
      });

      if (filtered.length === 0) {
        grid.innerHTML = `<div class="empty-state">هیچ شوێنێک یان گەڕەکێک بەم ناوە نەدۆزرایەوە! 🔍</div>`;
        return;
      }

      filtered.forEach(item => {
        const card = document.createElement('div');
        card.className = 'card';
        card.innerHTML = `
          <div>
            <div class="card-top">
              <span class="card-title">${item.name}</span>
              <span class="badge ${item.badgeClass}">${item.type}</span>
            </div>
            <p class="card-desc">${item.desc}</p>
          </div>
          <div class="card-footer">
            <span>📍 ${item.loc}</span>
          </div>
        `;
        grid.appendChild(card);
      });
    }

    function filterCategory(cat) {
      currentCategory = cat;
      document.querySelectorAll('.cat-btn').forEach(btn => {
        btn.classList.toggle('active', btn.innerText.includes(cat) || (cat === 'all' && btn.innerText === 'هەمووی'));
      });
      renderPlaces(document.getElementById('searchInput').value.trim());
    }

    document.getElementById('searchInput').addEventListener('input', (e) => {
      renderPlaces(e.target.value.trim());
    });

    // کارپێکردنی یەکەمجار
    renderPlaces();
  </script>
</body>
</html>
