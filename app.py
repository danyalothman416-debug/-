import 'package:flutter/material.dart';

void main() {
  runApp(const MaterialApp(
    debugShowCheckedModeBanner: false,
    home: DermanyZirak(),
  ));
}

class DermanyZirak extends StatelessWidget {
  const DermanyZirak({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF1A1A1A),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: const Icon(Icons.grid_view_rounded, color: Colors.white),
        title: const Text('دەرمانی زیرەک', style: TextStyle(color: Colors.white)),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(15.0),
          child: Column(
            children: [
              // بەشی سلایدەر (ڕەنگە پرتەقاڵییەکە)
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(colors: [Color(0xFFE6A064), Color(0xFFC07B43)]),
                  borderRadius: BorderRadius.circular(15),
                ),
                child: const Text(
                  'لەڕێی ئەپی فرۆشگاکەم\nدەتوانیت فرۆشگاکەت بکەیت بە لینکێک\nکلیک بکە و داونڵۆدی بکە',
                  textAlign: TextAlign.center,
                  style: TextStyle(color: Colors.white, fontSize: 16),
                ),
              ),
              const SizedBox(height: 20),
              
              // ناونیشانی سەرەکی
              const Align(
                alignment: Alignment.centerRight,
                child: Text('سەرەکی', style: TextStyle(color: Colors.white70, fontSize: 18)),
              ),
              const SizedBox(height: 10),

              // بەشی کارتەکان (٩ دانە وەک وێنەکە)
              GridView.count(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                crossAxisCount: 3,
                mainAxisSpacing: 10,
                crossAxisSpacing: 10,
                children: [
                  _buildCard('دەرمانەکان', Icons.medical_services, Colors.pink),
                  _buildCard('بیرم بخەرەوە !', Icons.alarm, Colors.orange, hasNew: true),
                  _buildCard('تاقیگە', Icons.biotech, Colors.blue),
                  _buildCard('پشکنینەکان', Icons.science, Colors.blueAccent),
                  _buildCard('ڤیتامینەکان', Icons.local_drink, Colors.orange),
                  _buildCard('نەخۆشییەکان', Icons.coronavirus, Colors.red),
                  _buildCard('بابەتەکان', Icons.person, Colors.redAccent, hasNew: true),
                  _buildCard('فرۆشگای ئۆنلاین', Icons.shopping_bag, Colors.cyan),
                  _buildCard('دەرمانە نوێیەکان', Icons.medication, Colors.teal, hasNew: true),
                ],
              ),
              
              const SizedBox(height: 20),

              // تێکستە دوورودرێژەکەی خوارەوە
              Container(
                padding: const EdgeInsets.all(15),
                decoration: BoxDecoration(color: const Color(0xFF252525), borderRadius: BorderRadius.circular(12)),
                child: const Text(
                  'لە ئەپلیکەیشنی دەرمانی زیرەکدا ٩٧٠ دەرمانی تێدایە کە بێ بەرامبەر بەردەستە بۆ سەرجەم بەکارهێنەران و بە چالاککردنی بەرنامەکە ٤٩٩ دەرمانی نوێ زیاد دەبێت بۆ ئەپلیکەیشنەکە کە ڕۆژانە بەردەوام دەرمانی نوێی بۆ زیاد دەکرێت جگە لەوەی دوای چالاککردنی بەرنامەکە سەرجەم ڕیکلامەکانیش دەسڕێنەوە',
                  textAlign: TextAlign.center,
                  textDirection: TextDirection.rtl,
                  style: TextStyle(color: Colors.white, fontSize: 13, height: 1.5),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // ویجێتی دروستکردنی کارتەکان بە شێوەیەکی سادە
  Widget _buildCard(String title, IconData icon, Color color, {bool hasNew = false}) {
    return Stack(
      children: [
        Container(
          width: double.infinity,
          decoration: BoxDecoration(color: const Color(0xFF252525), borderRadius: BorderRadius.circular(12)),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icon, size: 35, color: color),
              const SizedBox(height: 5),
              Text(title, textAlign: TextAlign.center, style: const TextStyle(color: Colors.white, fontSize: 11)),
            ],
          ),
        ),
        if (hasNew)
          Positioned(
            top: 5,
            left: 5,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 2),
              decoration: BoxDecoration(color: Colors.red, borderRadius: BorderRadius.circular(4)),
              child: const Text('نوێ', style: TextStyle(color: Colors.white, fontSize: 8)),
            ),
          ),
      ],
    );
  }
}
