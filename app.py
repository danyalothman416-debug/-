import 'package:flutter/material.dart';

void main() {
  runApp(const Poli12App());
}

class Poli12App extends StatelessWidget {
  const Poli12App({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'پۆلی ١٢',
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
      ),
      home: const HomeScreen(),
    );
  }
}

// مۆدێلی پرسیار
class Question {
  final String questionText;
  final List<String> options;
  final int correctAnswerIndex;

  Question({
    required this.questionText,
    required this.options,
    required this.correctAnswerIndex,
  });
}

// لاپەڕەی سەرەکی
class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  final List<Map<String, dynamic>> subjects = const [
    {'title': 'بیرکاری', 'icon': Icons.calculate, 'color': Colors.blue},
    {'title': 'فیزیا', 'icon': Icons.bolt, 'color': Colors.amber},
    {'title': 'کیمیا', 'icon': Icons.science, 'color': Colors.green},
    {'title': 'زیندەزانی', 'icon': Icons.biotech, 'color': Colors.teal},
    {'title': 'کوردی', 'icon': Icons.menu_book, 'color': Colors.deepOrange},
    {'title': 'ئینگلیزی', 'icon': Icons.language, 'color': Colors.purple},
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('پۆلی ١٢ - تاقیکردنەوەی وزاری', style: TextStyle(fontWeight: FontWeight.bold)),
        centerTitle: true,
        backgroundColor: Colors.deepPurple.shade100,
      ),
      body: Directionality(
        textDirection: TextDirection.rtl,
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'وانەیەک هەڵبژێرە بۆ تاقیکردنەوە:',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 16),
              Expanded(
                child: GridView.builder(
                  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 2,
                    crossAxisSpacing: 12,
                    mainAxisSpacing: 12,
                    childAspectRatio: 1.1,
                  ),
                  itemCount: subjects.length,
                  itemBuilder: (context, index) {
                    final subject = subjects[index];
                    return InkWell(
                      onTap: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) => QuizScreen(subjectTitle: subject['title']),
                          ),
                        );
                      },
                      borderRadius: BorderRadius.circular(16),
                      child: Card(
                        elevation: 2,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                        color: (subject['color'] as Color).withOpacity(0.12),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(subject['icon'], size: 48, color: subject['color']),
                            const SizedBox(height: 10),
                            Text(
                              subject['title'],
                              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// لاپەڕەی تاقیکردنەوە
class QuizScreen extends StatefulWidget {
  final String subjectTitle;
  const QuizScreen({super.key, required this.subjectTitle});

  @override
  State<QuizScreen> createState() => _QuizScreenState();
}

class _QuizScreenState extends State<QuizScreen> {
  int currentIndex = 0;
  int score = 0;

  final List<Question> questions = [
    Question(
      questionText: 'ئەنجامی دەربڕینی (2x + 4 = 10) بریتییە لە چەند؟',
      options: ['x = 2', 'x = 3', 'x = 4', 'x = 5'],
      correctAnswerIndex: 1,
    ),
    Question(
      questionText: 'تەواوکاری ∫ 2x dx بریتییە لە چەند؟',
      options: ['x² + c', '2x² + c', 'x + c', '2 + c'],
      correctAnswerIndex: 0,
    ),
    Question(
      questionText: 'یەکەی پێوانەی هێز لە سیستەمی نێودەوڵەتیدا چییە؟',
      options: ['جول', 'نیوتن', 'وات', 'پاسکال'],
      correctAnswerIndex: 1,
    ),
  ];

  void answerQuestion(int index) {
    if (index == questions[currentIndex].correctAnswerIndex) {
      score++;
    }

    if (currentIndex < questions.length - 1) {
      setState(() {
        currentIndex++;
      });
    } else {
      showDialog(
        barrierDismissible: false,
        context: context,
        builder: (context) => Directionality(
          textDirection: TextDirection.rtl,
          child: AlertDialog(
            title: const Text('ئەنجام'),
            content: Text('نمرەکەت: $score لە ${questions.length}'),
            actions: [
              TextButton(
                onPressed: () {
                  Navigator.pop(context);
                  Navigator.pop(context);
                },
                child: const Text('تەواو'),
              ),
            ],
          ),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final q = questions[currentIndex];

    return Scaffold(
      appBar: AppBar(title: Text('تاقیکردنەوەی ${widget.subjectTitle}'), centerTitle: true),
      body: Directionality(
        textDirection: TextDirection.rtl,
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text('پرسیاری ${currentIndex + 1} لە ${questions.length}', style: const TextStyle(color: Colors.grey)),
              const SizedBox(height: 12),
              Text(q.questionText, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              const SizedBox(height: 24),
              ...List.generate(
                q.options.length,
                (i) => Padding(
                  padding: const EdgeInsets.only(bottom: 12.0),
                  child: ElevatedButton(
                    style: ElevatedButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 14)),
                    onPressed: () => answerQuestion(i),
                    child: Text(q.options[i], style: const TextStyle(fontSize: 16)),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
