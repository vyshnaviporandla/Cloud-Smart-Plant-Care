import os
import firebase_admin
from firebase_admin import credentials, firestore


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SERVICE_ACCOUNT_PATH = os.path.join(
    BASE_DIR,
    "backend",
    "firebase-service-account.json"
)


if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
    firebase_admin.initialize_app(cred)


db = firestore.client()


def test_firestore():
    doc_ref = db.collection("cloud_test").document("test_document")

    doc_ref.set({
        "message": "Cloud Smart Plant Care connected successfully",
        "status": "connected"
    })

    document = doc_ref.get()

    if document.exists:
        print("Firestore connection successful!")
        print(document.to_dict())
    else:
        print("Firestore connection failed.")


if __name__ == "__main__":
    test_firestore()