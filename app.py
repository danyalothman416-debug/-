import 'package:flutter/material.dart';

void main() => runApp(const MaterialApp(home: DermanyZirak(), debugShowCheckedModeBanner: false));

class DermanyZirak extends StatelessWidget {
  const DermanyZirak({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF1E1E1E),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: const Icon(Icons.grid_view_rounded, color: Colors.white),
        title: const Text('دەرمانی زیرەک', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              // بەشی سڵایدەرەکە (وەک وێنەکە)
              Container(
                height: 160,
                decoration: BoxDecoration(
                  gradient: const LinearGradient(colors: [Color(0xFFE4A470), Color(0xFFC67D4B)]),
                  borderRadius: BorderRadius.circular(15),
                ),
                child: const Center(
                  child: Text(
                    'لەڕێی ئەپی فرۆشگاکەم\nدەتوانیت فرۆشگاکەت بکەیت بە لینکێک\nکلیک بکە و داونڵۆدی بکە',
                    textAlign: TextAlign.center,
                    style: TextStyle(color: Colors.white, fontSize: 16, height: 1.5),
                  ),
                ),
              ),
              const SizedBox(height: 20),
              const Text('سەرەکی', style: TextStyle(color: Colors.white, fontSize: 18)),
              const SizedBox(height: 15),

              // لێرە هەموو ٩ خانەکە وەک خۆی دادەنێم
              GridView.count(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                crossAxisCount: 3,
                mainAxisSpacing: 10,
                crossAxisSpacing: 10,
                childAspectRatio: 0.8,
                children: [
                  _item('دەرمانەکان', Icons.medication, Colors.pinkAccent),
                  _item('بیرم بخەرەوە !', Icons.notifications_active, Colors.orangeAccent, isNew: true),
                  _item('تاقیگە', Icons.biotech, Colors.lightBlueAccent),
                  _item('پشکنینەکان', Icons.science, Colors.blue),
                  _item('ڤیتامینەکان', Icons.liquor, Colors.orange), // ئایکۆنی شەربەت/ڤیتامین
                  _item('نەخۆشییەکان', Icons.coronavirus, Colors.red),
                  _item('بابەتەکان', Icons.person, Colors.red, isNew: true),
                  _item('فرۆشگای ئۆنلاین', Icons.medical_services, Colors.cyan),
                  _item('دەرمانە نوێیەکان', Icons.pills, Colors.teal, isNew: true),
                ],
              ),

              const SizedBox(height: 20),
              // تێکستە دوورودرێژەکەی خوارەوە بەبێ دەستکاری
              Container(
                padding: const EdgeInsets.all(15),
                decoration: BoxDecoration(color: const Color(0xFF2A2A2A), borderRadius: BorderRadius.circular(12)),
                child: const Text(
                  'لە ئەپلیکەیشنی دەرمانی زیرەکدا ٩٧٠ دەرمانی تێدایە کە بێ بەرامبەر بەردەستە بۆ سەرجەم بەکارهێنەران و بە چالاککردنی بەرنامەکە ٤٩٩ دەرمانی نوێ زیاد دەبێت بۆ ئەپلیکەیشنەکە کە ڕۆژانە بەردەوام دەرمانی نوێی بۆ زیاد دەکرێت جگە لەوەی دوای چالاککردنی بەرنامەکە سەرجەم ڕیکلامەکانیش دەسڕێنەوە',
                  textAlign: TextAlign.center,
                  textDirection: TextDirection.rtl,
                  style: TextStyle(color: Colors.white, fontSize: 14, height: 1.6),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _item(String title, IconData icon, Color color, {bool isNew = false}) {
    return Stack(
      children: [
        Container(
          decoration: BoxDecoration(color: const Color(0xFF2A2A2A), borderRadius: BorderRadius.circular(10)),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icon, size: 40, color: color),
              const SizedBox(height: 8),
              Text(title, style: const TextStyle(color: Colors.white, fontSize: 12), textAlign: TextAlign.center),
            ],
          ),
        ),
        if (isNew)
          Positioned(
            top: 5, left: 5,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 2),
              decoration: BoxDecoration(color: Colors.red, borderRadius: BorderRadius.circular(4)),
              child: const Text('نوێ', style: TextStyle(color: Colors.white, fontSize: 9)),
            ),
          ),
      ],
    );
  }
}
