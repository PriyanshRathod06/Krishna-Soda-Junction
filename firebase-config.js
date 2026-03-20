import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-app.js";
import { getFirestore } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-firestore.js";

const firebaseConfig = {
  apiKey:            "AIzaSyBEUhzb-WXWtUFjwmNXePX3IMSTFMs0Ie8",
  authDomain:        "krishna-soda-juction.firebaseapp.com",
  projectId:         "krishna-soda-juction",
  storageBucket:     "krishna-soda-juction.firebasestorage.app",
  messagingSenderId: "182906199546",
  appId:             "1:182906199546:web:808818dff2267bb2a19843"
};

const app = initializeApp(firebaseConfig);
export const db = getFirestore(app);
