from flask import Flask, request, jsonify, render_template_string
import random
import os
from datetime import datetime

app = Flask(__name__)

image_paths = {
    "Beginner": {
        "10": {
            "Physics": "C:/Users/DELL/Downloads/AI CAPSTONE PROJECT/Class-10/Beginner/Physics",
            "Chemistry": "C:/Users/DELL/Downloads/AI CAPSTONE PROJECT/Class-10/Beginner/Chemistry",
            "Maths": "C:/Users/DELL/Downloads/AI CAPSTONE PROJECT/Class-10/Beginner/Maths",
            "Biology": "C:/Users/DELL/Downloads/AI CAPSTONE PROJECT/Class-10/Beginner/Biology",
            "English": "C:/Users/DELL/Downloads/AI CAPSTONE PROJECT/Class-10/Beginner/English"
        },
        "11": {
            "Physics": "C:/Users/DELL/Downloads/AI CAPSTONE PROJECT/Class-11/Beginner/Physics",
            "Chemistry": "C:/Users/DELL/Downloads/AI CAPSTONE PROJECT/Class-11/Beginner/Chemistry",
            "Maths": "C:/Users/DELL/Downloads/AI CAPSTONE PROJECT/Class-11/Beginner/Maths",
            "Biology": "C:/Users/DELL/Downloads/AI CAPSTONE PROJECT/Class-11/Beginner/Biology",
            "English": "C:/Users/DELL/Downloads/AI CAPSTONE PROJECT/Class-11/Beginner/English"
        },
        "12": {
            "Physics": "C:/Users/DELL/Downloads/AI CAPSTONE PROJECT/Class-12/Beginner/Physics",
            "Chemistry": "C:/Users/DELL/Downloads/AI CAPSTONE PROJECT/Class-12/Beginner/Chemistry",
            "Maths": "C:/Users/DELL/Downloads/AI CAPSTONE PROJECT/Class-12/Beginner/Maths",
            "Biology": "C:/Users/DELL/Downloads/AI CAPSTONE PROJECT/Class-12/Beginner/Biology",
            "English": "C:/Users/DELL/Downloads/AI CAPSTONE PROJECT/Class-12/Beginner/English"
        }
    }
}

MENU_TEXT = """
Hi! I am EduBot 🤖 Here's what I can help you with:

1. Tell me your class (e.g., "class 10").
2. Mention your subject (e.g., "math", "science").
3. Specify difficulty (Beginner, Intermediate, Advanced) — optional.

Example queries:
- "Give me an easy math question for class 10"
- "I want a hard science problem"
- "Help" or "menu" to see this message again.
"""

def load_images(class_level, subject, difficulty):
    base_path = image_paths[difficulty][class_level][subject]
    try:
        images = [f for f in os.listdir(base_path) if f.endswith(('.png', '.jpg', '.jpeg'))]
        if images:
            return os.path.join(base_path, random.choice(images))
    except FileNotFoundError:
        return None

def get_difficulty(user_input):
    user_input = user_input.lower()
    if any(word in user_input for word in ["beginner", "easy", "simple", "basic"]):
        return "Beginner"
    elif any(word in user_input for word in ["intermediate", "medium", "normal"]):
        return "Intermediate"
    elif any(word in user_input for word in ["advanced", "hard", "difficult", "challenging"]):
        return "Advanced"
    return "Beginner"

def get_question(student_class, subject, difficulty):
    class_level = student_class.split()[-1]
    image_path = load_images(class_level, subject, difficulty)
    return image_path if image_path else "Sorry, I don't have questions for your request yet."

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message", "").lower()

    if any(word in user_msg for word in ["help", "menu", "options"]):
        return jsonify({"reply": MENU_TEXT})

    if "class 10" in user_msg:
        student_class = "Class 10"
    elif "class 11" in user_msg:
        student_class = "Class 11"
    elif "class 12" in user_msg:
        student_class = "Class 12"
    else:
        student_class = "Unknown class"

    if "math" in user_msg or "mathematics" in user_msg:
        subject = "Maths"
    elif "science" in user_msg:
        subject = "Biology"
    elif "physics" in user_msg:
        subject = "Physics"
    elif "chemistry" in user_msg:
        subject = "Chemistry"
    else:
        subject = "General"

    difficulty = get_difficulty(user_msg)
    question_image_path = get_question(student_class, subject, difficulty)

    if question_image_path and os.path.exists(question_image_path):
        question_image_html = f'<img src="file:///{question_image_path}" alt="Question Image" style="max-width: 100%; height: auto;">'
    else:
        question_image_html = "Sorry, I couldn't find an image for your request."

    reply = f"Here's a {difficulty} question for {student_class} {subject}:\n{question_image_html}"
    return jsonify({"reply": reply})

@app.route("/")
def index():
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>EduBot 🤖 | AI Learning Assistant</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body class="bg-gray-100 min-h-screen">
  <div class="container mx-auto max-w-4xl p-4">
    <header class="bg-white rounded-t-xl shadow-md p-6 flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-blue-600">EduBot <span class="text-blue-400">🤖</span></h1>
        <p class="text-gray-600">Your AI-powered learning assistant</p>
      </div>
      <div class="flex items-center space-x-2">
        <span class="relative flex h-3 w-3">
          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
          <span class="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
        </span>
        <span class="text-sm text-gray-500">Online</span>
      </div>
    </header>

    <div class="chat-container bg-white rounded-b-xl shadow-md overflow-hidden flex flex-col" style="height: 70vh;">
      <div id="chatArea" class="flex-1 p-6 overflow-y-auto">
        <div class="flex mb-4">
          <div class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center mr-3">
            <i class="fas fa-robot text-blue-600"></i>
          </div>
          <div class="max-w-xl">
            <div class="bg-blue-50 text-blue-900 p-4 rounded-lg rounded-tl-none">
              <p>Hi there! 👋 I'm EduBot, your AI learning assistant.</p>
              <p class="mt-2">I can help you with questions for Class 10, 11, and 12 in various subjects.</p>
            </div>
            <div class="text-xs text-gray-500 ml-2 mt-1">{{ now }}</div>
          </div>
        </div>
        <div class="flex flex-wrap gap-2 mt-6">
          <button onclick="sendSuggestion('Help')" class="suggestion-chip bg-gray-100 hover:bg-gray-200 text-gray-800 px-4 py-2 rounded-full text-sm font-medium transition-all">
            Show Help
          </button>
        </div>
      </div>

      <div class="border-t border-gray-200 p-4 bg-gray-50">
        <div class="flex items-center gap-2">
          <input id="userInput" type="text" placeholder="Ask me anything about Class 10 subjects..." 
                 class="flex-1 border border-gray-300 rounded-full py-3 px-6 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent">
          <button onclick="sendMessage()" class="bg-blue-600 hover:bg-blue-700 text-white p-3 rounded-full w-12 h-12 flex items-center justify-center transition-all">
            <i class="fas fa-paper-plane"></i>
          </button>
        </div>
        <div class="text-xs text-gray-500 mt-2 text-center">
          Example: "Give me a medium difficulty math question"
        </div>
      </div>
    </div>

    <!-- Colored Info Boxes Section -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
      <div class="bg-blue-100 p-4 rounded-lg shadow-md">
        <h4 class="font-bold text-lg text-blue-800">24/7 Availability</h4>
        <p class="text-gray-700">EduBot is available anytime to assist you with your learning needs.</p>
      </div>
      <div class="bg-green-100 p-4 rounded-lg shadow-md">
        <h4 class="font-bold text-lg text-green-800">Personalized Learning</h4>
        <p class="text-gray-700">Get questions tailored to your class and difficulty level.</p>
      </div>
      <div class="bg-yellow-100 p-4 rounded-lg shadow-md">
        <h4 class="font-bold text-lg text-yellow-800">Difficulty Levels Include</h4>
        <p class="text-gray-700">Beginner, Intermediate, Advanced and Competitive Exams for classes 10 to 12!</p>
      </div>
    </div>
  </div>

  <script>
    const chatArea = document.getElementById('chatArea');
    const userInput = document.getElementById('userInput');

    function appendMessage(sender, text, isBot = false) {
      const messageDiv = document.createElement('div');
      messageDiv.className = `flex mb-4 ${isBot ? '' : 'justify-end'}`;
      const messageContent = `
        ${!isBot ? `
          <div class="max-w-xl order-1">
            <div class="bg-blue-600 text-white p-4 rounded-lg rounded-tr-none">
              <p>${text}</p>
            </div>
            <div class="text-xs text-gray-500 mr-2 mt-1 text-right">${formatTime()}</div>
          </div>
          <div class="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center ml-3 order-2">
            <i class="fas fa-user text-white"></i>
          </div>
        ` : `
          <div class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center mr-3">
            <i class="fas fa-robot text-blue-600"></i>
          </div>
          <div class="max-w-xl">
            <div class="bg-blue-50 text-blue-900 p-4 rounded-lg rounded-tl-none">
              <p>${text}</p>
            </div>
            <div class="text-xs text-gray-500 ml-2 mt-1">${formatTime()}</div>
          </div>
        `}
      `;
      messageDiv.innerHTML = messageContent;
      chatArea.appendChild(messageDiv);
      chatArea.scrollTop = chatArea.scrollHeight;
    }

    function sendSuggestion(text) {
      userInput.value = text;
      sendMessage();
    }

    async function sendMessage() {
      const message = userInput.value.trim();
      if (!message) return;
      appendMessage('You', message, false);
      userInput.value = '';
      try {
        const response = await fetch('/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message })
        });
        const data = await response.json();
        appendMessage('EduBot', data.reply, true);
      } catch (err) {
        appendMessage('EduBot', 'Error: Could not connect to the server.', true);
      }
    }

    function formatTime() {
      const now = new Date();
      let hours = now.getHours();
      let minutes = now.getMinutes();
      const ampm = hours >= 12 ? 'pm' : 'am';
      hours = hours % 12;
      hours = hours ? hours : 12;
      minutes = minutes < 10 ? '0' + minutes : minutes;
      return `${hours}:${minutes} ${ampm}`;
    }

    userInput.addEventListener('keydown', function(event) {
      if (event.key === 'Enter') {
        sendMessage();
      }
    });
  </script>
</body>
</html>
''', now=datetime.now().strftime("%I:%M %p"))

if __name__ == "__main__":
    app.run(debug=True)
