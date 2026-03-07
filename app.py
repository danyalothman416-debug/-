import 'package:flutter/material.dart';

void main() {
  runApp(const MaterialApp(
    home: DermanyZirak(),
    debugShowCheckedModeBanner: false,
  ));
}

class DermanyZirak extends StatelessWidget {
  const DermanyZirak({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF1A1A1A),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: const Icon(Icons.grid_view_rounded, color: Colors.white),
        actions: const [
           Padding(
            padding: EdgeInsets.all(12.0),
            child: Text(
              'دەرمانی زیرەک',
              style: TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold),
            ),
          ),
        ],
      ),
      body: Directionality(
        textDirection: TextDirection.rtl, // بۆ ئەوەی ڕێکخستنەکان لە ڕاستەوە بن
        child: SingleChildScrollView(
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // بەشی سڵایدەر
                Container(
                  width: double.infinity,
                  height: 180,
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [Color(0xFFE4A470), Color(0xFFC67D4B)],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
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
                const SizedBox(height: 25),
                const Text(
                  'سەرەکی',
                  style: TextStyle(color: Colors.white70, fontSize: 18),
                ),
                const SizedBox(height: 15),

                // تۆڕی کارتەکان - Grid
                GridView.count(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  crossAxisCount: 3,
                  mainAxisSpacing: 12,
                  crossAxisSpacing: 12,
                  childAspectRatio: 0.85,
                  children: [
                    _buildItem('دەرمانەکان', Icons.medical_services, Colors.pinkAccent),
                    _buildItem('بیرم بخەرەوە !', Icons.notifications_active, Colors.orangeAccent, isNew: true),
                    _buildItem('تاقیگە', Icons.biotech, Colors.lightBlueAccent),
                    _buildItem('پشکنینەکان', Icons.science, Colors.blue),
                    _buildItem('ڤیتامینەکان', Icons.local_drink, Colors.orange),
                    _buildItem('نەخۆشییەکان', Icons.coronavirus, Colors.redAccent),
                    _buildItem('بابەتەکان', Icons.person, Colors.red, isNew: true),
                    _buildItem('فرۆشگای ئۆنلاین', Icons.store, Colors.cyan),
                    _buildItem('دەرمانە نوێیەکان', Icons.medication, Colors.teal, isNew: true),
                  ],
                ),

                const SizedBox(height: 30),
                
                // تێکستە دوورودرێژەکەی خوارەوە بەبێ دەستکاری
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: const Color(0xFF252525),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Text(
                    'لە ئەپلیکەیشنی دەرمانی زیرەکدا ٩٧٠ دەرمانی تێدایە کە بێ بەرامبەر بەردەستە بۆ سەرجەم بەکارهێنەران و بە چالاککردنی بەرنامەکە ٤٩٩ دەرمانی نوێ زیاد دەبێت بۆ ئەپلیکەیشنەکە کە ڕۆژانە بەردەوام دەرمانی نوێی بۆ زیاد دەکرێت جگە لەوەی دوای چالاککردنی بەرنامەکە سەرجەم ڕیکلامەکانیش دەسڕێنەوە',
                    textAlign: TextAlign.center,
                    style: TextStyle(color: Colors.white, fontSize: 13, height: 1.8),
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

  Widget _buildItem(String title, IconData icon, Color color, {bool isNew = false}) {
    return Stack(
      children: [
        Container(
          width: double.infinity,
          decoration: BoxDecoration(
            color: const Color(0xFF252525),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icon, size: 35, color: color),
              const SizedBox(height: 10),
              Text(
                title,
                textAlign: TextAlign.center,
                style: const TextStyle(color: Colors.white, fontSize: 11),
              ),
            ],
          ),
        ),
        if (isNew)
          Positioned(
            top: 8,
            right: 8, // چونکە RTL مان بەکارهێناوە، دەکەوێتە لای ڕاست
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 2),
              decoration: BoxDecoration(
                color: Colors.red,
                borderRadius: BorderRadius.circular(4),
              ),
              child: const Text(
                'نوێ',
                style: TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold),
              ),
            ),
          ),
      ],
    );
  }
}
