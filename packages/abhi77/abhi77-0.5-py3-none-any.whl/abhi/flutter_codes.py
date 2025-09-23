def get_code(topic=None):
    codes = {
        "login_page": """
import 'package:flutter/material.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      debugShowCheckedModeBanner: false,
      home: LoginPage(),
    );
  }
}

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final TextEditingController _usernameController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();

  void _login() {
    String username = _usernameController.text.trim();
    String password = _passwordController.text.trim();

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Login Details'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('Username: $username'),
            Text('Password: $password'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  void _reset() {
    _usernameController.clear();
    _passwordController.clear();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Login Page')),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Username
            TextField(
              controller: _usernameController,
              decoration: const InputDecoration(
                labelText: 'Username',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 20),

            // Password
            TextField(
              controller: _passwordController,
              obscureText: true,
              decoration: const InputDecoration(
                labelText: 'Password',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 20),

            // Buttons
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                ElevatedButton(
                  onPressed: _login,
                  child: const Text('Login'),
                ),
                ElevatedButton(
                  onPressed: _reset,
                  child: const Text('Reset'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
""",

        "color_grid": """
import 'package:flutter/material.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false, // removes the debug banner
      home: const MyHomePage(title: 'Flutter Demo Home Page'),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key, required this.title});
  final String title;

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  Widget buildBox(Color color) {
    return ColoredBox(
      color: color,
      child: const SizedBox(width: 50, height: 50),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
        appBar: AppBar(title: Text(widget.title)),
        body: Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    buildBox(Colors.red),
                    buildBox(Colors.green),
                    buildBox(Colors.blue),
                    buildBox(Colors.orange),
                  ],
                ),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    buildBox(Colors.green),
                    buildBox(Colors.pink),
                    buildBox(Colors.black),
                    buildBox(Colors.red),
                  ],
                ),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    buildBox(Colors.red),
                    buildBox(Colors.green),
                    buildBox(Colors.blue),
                    buildBox(Colors.orange),
                  ],
                ),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    buildBox(Colors.pink),
                    buildBox(Colors.yellow),
                    buildBox(Colors.blue),
                    buildBox(Colors.red),
                  ],
                ),
              ],
            ),
            ),
        );
    }
}

""",

        "php_addition_api": """
http://localhost/addition_api.php
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

void main() => runApp(const MyApp());

class MyApp extends StatelessWidget {
  const MyApp({super.key});
  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      debugShowCheckedModeBanner: false,
      home: AdditionPage(),
    );
  }
}

class AdditionPage extends StatefulWidget {
  const AdditionPage({super.key});
  @override
  _AdditionPageState createState() => _AdditionPageState();
}

class _AdditionPageState extends State<AdditionPage> {
  final TextEditingController _num1Controller = TextEditingController();
  final TextEditingController _num2Controller = TextEditingController();
  String _result = '';
  bool _loading = false;

  @override
  void dispose() {
    _num1Controller.dispose();
    _num2Controller.dispose();
    super.dispose();
  }

  Future<void> _addNumbers() async {
    final num1 = _num1Controller.text.trim();
    final num2 = _num2Controller.text.trim();

    if (num1.isEmpty || num2.isEmpty) {
      setState(() => _result = 'Enter both numbers!');
      return;
    }

    final a = double.tryParse(num1);
    final b = double.tryParse(num2);
    if (a == null || b == null) {
      setState(() => _result = 'Please enter valid numbers');
      return;
    }

    setState(() {
      _loading = true;
      _result = '';
    });

    // For web use 'localhost'. For Android emulator use '10.0.2.2'. Adjust as needed.
    final uri = Uri.http('localhost', '/abhi/api.php', {
      'num1': num1,
      'num2': num2,
    });

    try {
      final response = await http.get(uri).timeout(const Duration(seconds: 10));
      if (response.statusCode == 200) {
        setState(() => _result = 'Result: ${response.body}');
      } else {
        setState(() => _result = 'Error: ${response.statusCode}');
      }
    } catch (e) {
      setState(() => _result = 'Network error: $e');
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Add Two Numbers')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            TextField(
              controller: _num1Controller,
              keyboardType: TextInputType.numberWithOptions(decimal: true),
              decoration: const InputDecoration(labelText: 'Number 1'),
            ),
            const SizedBox(height: 10),
            TextField(
              controller: _num2Controller,
              keyboardType: TextInputType.numberWithOptions(decimal: true),
              decoration: const InputDecoration(labelText: 'Number 2'),
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: _loading ? null : _addNumbers,
              child: _loading
                  ? const CircularProgressIndicator.adaptive()
                  : const Text('Add'),
            ),
            const SizedBox(height: 20),
            Text(
              _result,
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
          ],
        ),
      ),
    );
  }
}







PHP



<?php
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Headers: *");
header("Access-Control-Allow-Methods: GET, POST, OPTIONS");
 
if (isset($_GET['num1']) && isset($_GET['num2'])) {
    $num1 = (int) $_GET['num1'];
    $num2 = (int) $_GET['num2'];
    echo $num1 * $num2;
} else {
    echo "Missing numbers";
}
?>

""",

        "navigator_main": """
import 'package:flutter/material.dart';

void main() {
  runApp(const MyApp());
}

// Main App
class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Route Demo',
      initialRoute: '/',
      routes: {
        '/': (context) => const HomePage(),
        '/second': (context) => const SecondPage(),
        '/third': (context) => const ThirdPage(),
      },
    );
  }
}

// Page 1 - Home
class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Home Page')),
      body: Center(
        child: ElevatedButton(
          onPressed: () {
            Navigator.pushNamed(context, '/second');
          },
          child: const Text('Go to Second Page'),
        ),
      ),
    );
  }
}

// Page 2 - Second
class SecondPage extends StatelessWidget {
  const SecondPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Second Page')),
      body: Center(
        child: ElevatedButton(
          onPressed: () {
            Navigator.pushNamed(context, '/third');
          },
          child: const Text('Go to Third Page'),
        ),
      ),
    );
  }
}

// Page 3 - Third
class ThirdPage extends StatelessWidget {
  const ThirdPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Third Page')),
      body: Center(
        child: ElevatedButton(
          onPressed: () {
            Navigator.popUntil(context, ModalRoute.withName('/'));
          },
          child: const Text('Go Back to Home Page'),
        ),
      ),
    );
  }
}

""",

        "named_route_navigation": """
#lib/main
import 'package:flutter/material.dart';
import 'page_one.dart';
import 'page_two.dart';
import 'page_three.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Multi Page Routing',
      initialRoute: '/',
      routes: {
        '/': (context) => const PageOne(),
        '/two': (context) => const PageTwo(),
        '/three': (context) => const PageThree(),
      },
    );
  }
}

#page_one.dart
import 'package:flutter/material.dart';

class PageOne extends StatelessWidget {
  const PageOne({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Page One")),
      body: Center(
        child: ElevatedButton(
          onPressed: () {
            Navigator.pushNamed(context, '/two');
          },
          child: const Text("Go to Page Two"),
        ),
      ),
    );
  }
}

#page_two.dart
import 'package:flutter/material.dart';

class PageTwo extends StatelessWidget {
  const PageTwo({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Page Two")),
      body: Center(
        child: ElevatedButton(
          onPressed: () {
            Navigator.pushNamed(context, '/three');
          },
          child: const Text("Go to Page Three"),
        ),
      ),
    );
  }
}

#page_three.dart
import 'package:flutter/material.dart';

class PageThree extends StatelessWidget {
  const PageThree({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Page Three")),
      body: Center(
        child: ElevatedButton(
          onPressed: () {
            Navigator.popUntil(context, ModalRoute.withName('/'));
          },
          child: const Text("Go Back to Page One"),
        ),
      ),
    );
  }
}

""",
"Provider": """
#Main 
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'counter_provider.dart';

class AddTwoNumbersPage extends StatefulWidget {
  const AddTwoNumbersPage({super.key});

  @override
  State<AddTwoNumbersPage> createState() => _AddTwoNumbersPageState();
}

class _AddTwoNumbersPageState extends State<AddTwoNumbersPage> {
  final TextEditingController _num1Controller = TextEditingController();
  final TextEditingController _num2Controller = TextEditingController();

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<SumProvider>();
    return Scaffold(
      appBar: AppBar(title: const Text("Add Two Numbers")),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            TextField(
              controller: _num1Controller,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(
                labelText: "Enter first number",
                border: OutlineInputBorder(),
              ),
              onChanged: (value){
                final parsed = int.tryParse(value)??0;
                context.read<SumProvider>().setnum1(parsed);
              }
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _num2Controller,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(
                labelText: "Enter second number",
                border: OutlineInputBorder(),
              ),
              onChanged: (value){
                final parsed = int.tryParse(value)??0;
                context.read<SumProvider>().setnum2(parsed);
              }
            ),
            const SizedBox(height: 16),
            Text(
              "Result: ${provider.sum}",
              style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
          ],
        ),
     ),
    );
  }
}

#2
import 'package:provider/provider.dart';
import 'package:flutter/foundation.dart';

class SumProvider with ChangeNotifier{
  int num1 = 0;
  int num2 = 0;

  int get sum => num1 + num2;

  void setnum1(int num){
    num1 = num;
    notifyListeners();
  }

  void setnum2(int num){
    num2 = num;
    notifyListeners();
 }
}

#2
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'counter_provider.dart';
import 'first_page.dart';

void main() {
  runApp(
    ChangeNotifierProvider(
      create: (_) => SumProvider(),
      child: const MyApp(),
    ),
  );
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      home: const AddTwoNumbersPage(),
  );
 }
}


"""

    
    }

    if topic is None:
        return "Please specify a topic. Use abhi.topics() to see available topics."

    topic = topic.lower()
    return codes.get(topic, f"No content found for topic: {topic}")
