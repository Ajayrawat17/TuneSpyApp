# 🎵 TuneSpy – Music Recognition App like Shazam

> **TuneSpy** is a Flutter-based mobile application that identifies songs playing in the background. It works just like **Shazam**, using real-time audio fingerprinting. The app uses a custom Django backend with MongoDB Atlas and is deployed on AWS Cloud.

---

## 📱 Platform

- 📦 Android (Flutter)
- Backend: Django (Python)
- Database: MongoDB Atlas (Cloud)
- Hosting: AWS EC2 / Cloud

---

## 📚 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Installation & Setup](#installation--setup)
- [Usage Guide](#usage-guide)
- [Screenshots](#screenshots)
- [Folder Structure](#folder-structure)
- [Author](#author)
- [License](#license)
- [Recruiter Note](#recruiter-note)

---

## ✅ Features

- 🎧 Real-time song detection using microphone input
- 🔍 Audio fingerprinting and matching (custom backend logic)
- 🌐 REST API integration with Django backend
- ☁️ MongoDB Atlas for cloud-based song data storage
- 📜 History screen to view previously identified songs
- 📱 Modern UI built with Flutter

---

## 🧑‍💻 Tech Stack

### 🔹 Frontend:
- Flutter
- Dart

### 🔹 Backend:
- Django
- Django REST Framework
- Librosa (for audio fingerprinting)

### 🔹 Database:
- MongoDB Atlas

### 🔹 Hosting & DevOps:
- AWS EC2
- GitHub for version control

---

## 🏗️ Architecture

```plaintext
[Flutter App]
   |
   | (Audio Recording via Mic)
   v
[Django REST API]
   |
   | (Fingerprinting using Librosa)
   v
[MongoDB Atlas]
   |
   | (Find Closest Match)
   v
[Return Song Info to App]

⚙️ Installation & Setup
🔹 Flutter App Setup
bash
Copy
Edit
cd tunespyfrontend
flutter pub get
flutter run
📱 Make sure to use an Android device or emulator

🔹 Django Backend Setup
bash
Copy
Edit
cd TuneSpyBackend
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows

pip install -r requirements.txt
python manage.py runserver
🔹 MongoDB Setup
Use MongoDB Atlas

Create a cluster and connect your Django backend

Update your MongoDB URI in settings.py

▶️ Usage Guide
Open the app on your Android device

Tap "Listen" to identify the currently playing music

App records audio and sends it to backend

Backend processes, fingerprints, and matches the song

Output (song title, artist, etc.) is shown in the app

History of previously recognized songs is saved locally

📁 Folder Structure
bash
Copy
Edit
TuneSpy/
├── tunespyfrontend/       # Flutter mobile app
│   ├── lib/
│   ├── android/
│   └── pubspec.yaml
│
├── TuneSpyBackend/        # Django + REST API backend
│   ├── tunespy_api/
│   └── manage.py
│
├── .idea/                 # IDE config
└── README.md

👨‍💻 Author
Ajay Rawat
🎓 B.Tech CSE – Graphic Era Hill University
📧 ajayrawat11146@gmail.com
🌐 GitHub: Ajayrawat17

📄 License
This project is licensed under the MIT License.
