import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret_key'
    FIREBASE_CONFIG = os.environ.get('FIREBASE_CONFIG') or 'C:/receta/recetario-4bd31-firebase-adminsdk-wwcnu-5565f32cb1.json'
