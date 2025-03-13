### **FitCheck - AI-Based Outfit Recommendation App**

FitCheck is an AI-powered fashion assistant that helps users find the perfect outfit combinations.
Simply upload a clothing item, and the app will recommend five matching fashion items from a curated image database.

# Features: 

* AI-Powered Recommendations – Get fashion recommendations using deep learning.

* Fast & Efficient – Uses a pre-trained model to generate recommendations in real-time.

* Cross-Platform – Works on mobile via Expo Go and a local server.

# Installation & Setup:

1️⃣ Download the Dataset

Before running the app, download the required dataset:
cd src/dataset/data
python download_data.py

2️⃣ Install Required Dependencies

Backend (Flask Server)

Make sure you have Python installed. Then install the dependencies:
pip install -r requirements.txt

Frontend (React Native + Expo)

FitCheck's frontend is built with React Native. Install Node.js and then install dependencies:
cd src/frontend
npm install

Additionally, install Expo Go on your mobile device from the App Store / Google Play.

3️⃣ Configure Network Settings

In the file src/frontend/app/index.tsx, update two lines of code to replace the default IP address with your computer's local IP (make sure both your PC and mobile are connected to the same Wi-Fi).

4️⃣ Run the Application

Start the Backend Server:
cd src/backend
python flask_server.py

Launch the Mobile App

1. Open a new terminal:
cd src/frontend (if not already in the frontend directory)
npx expo start

2. Scan the QR code with Expo Go on your mobile device.

3. Enjoy personalized fashion recommendations! 🎉