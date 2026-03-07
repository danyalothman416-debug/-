import 'package:flutter/material.dart';

void main() {
  runApp(const DermanyZirakApp());
}

class DermanyZirakApp extends StatelessWidget {
  const DermanyZirakApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      home: Scaffold(
        backgroundColor: const Color(0xFF1A1A1A), // ڕەنگی باکگراوندی تاریک
        appBar: AppBar(
          backgroundColor: Colors.transparent,
          elevation: 0,
          leading: const Icon(Icons.grid_view_rounded, color: Colors.white, size: 30),
          title: const Text(
            'دەرمانی زیرەک',
            style: TextStyle(
              color: Colors.white,
              fontSize: 22,
              fontWeight: FontWeight.bold,
            ),
          ),
          centerTitle: false,
        ),
        body: SingleChildScrollView(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                // بەشی سلایدەر (ڕیکلامەکان)
                const SizedBox(height: 10),
                SizedBox(
                  height: 180,
                  child: ListView(
                    scrollDirection: Axis.horizontal,
                    reverse: true, // بۆ ئەوەی لە ڕاستەوە دەست پێ بکات
                    children: [
                      _buildSliderCard('لە ڕێی ئەپی فرۆشگاکەم\nدەتوانیت فرۆشگاکەت بکەیت بە لینکێک\nکلیک بکە و داونڵۆدی بکە'),
                      const SizedBox(width: 10),
                      _buildSliderCard('ڕیکلامی دووەم'),
                    ],
                  ),
                ),
                
                const SizedBox(height: 25),
                const Text(
                  'سەرەکی',
                  style: TextStyle(color: Colors.white70, fontSize: 18),
                ),
                const SizedBox(height: 15),

                // تۆڕی کارتەکان (Grid)
                GridView.count(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  crossAxisCount: 3,
                  mainAxisSpacing: 12,
                  crossAxisSpacing: 12,
                  childAspectRatio: 0.85,
                  children: [
                    _buildMenuCard('دەرمانەکان', Icons.medication, Colors.pinkAccent),
                    _buildMenuCard('بیرم بخەرەوە!', Icons.notifications_active, Colors.orangeAccent, isNew: true),
                    _buildMenuCard('تاقیگە', Icons.biotech, Colors.lightBlueAccent),
                    _buildMenuCard('پشکنینەکان', Icons.science, Colors.blue),
                    _buildMenuCard('ڤیتامینەکان', Icons.wine_bar, Colors.orange),
                    _buildMenuCard('نەخۆشییەکان', Icons.coronavirus, Colors.redAccent),
                    _buildMenuCard('بابەتەکان', Icons.person, Colors.red, isNew: true),
                    _buildMenuCard('فرۆشگای ئۆنلاین', Icons.medical_services, Colors.cyan),
                    _buildMenuCard('دەرمانە نوێیەکان', Icons.pill, Colors.teal, isNew: true),
                  ],
                ),

                const SizedBox(height: 30),
                
                // بەشی زانیاری خوارەوە
                Container(
                  padding: const EdgeInsets.all(15),
                  decoration: BoxDecoration(
                    color: const Color(0xFF252525),
                    borderRadius: BorderRadius.circular(15),
                  ),
                  child: const Text(
                    'لە ئەپلیکەیشنی دەرمانی زیرەکدا ٩٧٠ دەرمانی تێدایە کە بێ بەرامبەر بەردەستە بۆ سەرجەم بەکارهێنەران و بە چالاککردنی بەرنامەکە ٤٩٩ دەرمانی نوێ زیاد دەبێت بۆ ئەپلیکەیشنەکە کە ڕۆژانە بەردەوام دەرمانی نوێی بۆ زیاد دەکرێت جگە لەوەی دوای چالاککردنی بەرنامەکە سەرجەم ڕیکلامەکانیش دەسڕێنەوە',
                    textAlign: TextAlign.center,
                    style: TextStyle(color: Colors.white, height: 1.6, fontSize: 13),
                    textDirection: TextDirection.rtl,
                  ),
                ),
                const SizedBox(height: 20),
              ],
            ),
          ),
        ),
      ),
    );
  }

  // ویجێت بۆ دروستکردنی کارتەکانی مێنێو
  Widget _buildMenuCard(String title, IconData icon, Color iconColor, {bool isNew = false}) {
    return Stack(
      children: [
        Container(
          decoration: BoxDecoration(
            color: const Color(0xFF252525),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icon, size: 40, color: iconColor),
              const SizedBox(height: 10),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 4.0),
                child: Text(
                  title,
                  textAlign: TextAlign.center,
                  style: const TextStyle(color: Colors.white, fontSize: 13),
                ),
              ),
            ],
          ),
        ),
        if (isNew)
          Positioned(
            top: 8,
            left: 8,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
              decoration: BoxDecoration(color: Colors.red, borderRadius: BorderRadius.circular(5)),
              child: const Text('نوێ', style: TextStyle(color: Colors.white, fontSize: 10)),
            ),
          ),
      ],
    );
  }

  // ویجێت بۆ دروستکردنی سلایدەر
  Widget _buildSliderCard(String text) {
    return Container(
      width: 300,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFFE6A064), Color(0xFFC07B43)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Center(
        child: Text(
          text,
          textAlign: TextAlign.center,
          textDirection: TextDirection.rtl,
          style: const TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.bold),
        ),
      ),
    );
  }
}
