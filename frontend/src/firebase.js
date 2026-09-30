import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyA3zKIbQ54TRI5Mqecy9vEd6gRwhf0B-Oc",
  authDomain: "cloud-smart-plant-care-a5583.firebaseapp.com",
  projectId: "cloud-smart-plant-care-a5583",
  storageBucket: "cloud-smart-plant-care-a5583.firebasestorage.app",
  messagingSenderId: "770050884616",
  appId: "1:770050884616:web:064b2b049015953d18fdbd"
};

const app = initializeApp(firebaseConfig);

export const auth = getAuth(app);

export default app;
