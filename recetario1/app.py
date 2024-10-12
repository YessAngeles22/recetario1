# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, url_for
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app, storage
import os
from config import Config

app = Flask(__name__)

# Inicializar Firebase
cred = credentials.Certificate(Config.FIREBASE_CONFIG)
initialize_app(cred, {
    'storageBucket': os.environ.get('FIREBASE_STORAGE_BUCKET', 'gs://recetario-4bd31.appspot.com/blob')
})

db = firestore.client()
bucket = storage.bucket()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        address = request.form['address']
        image = request.files.get('image')

        # Guardar datos en Firestore
        user_ref = db.collection('users').document()
        user_data = {
            'name': name,
            'phone': phone,
            'address': address
        }
        user_ref.set(user_data)

        # Guardar imagen en Storage
        if image:
            blob = bucket.blob(f"profile_images/{user_ref.id}/{image.filename}")
            try:
                blob.upload_from_file(image, content_type=image.content_type)
                image_url = blob.public_url
                user_ref.update({'image_url': image_url})
                print(f"Imagen de perfil subida correctamente: {image_url}")
            except Exception as e:
                print(f"Error al subir la imagen: {e}")

        return redirect(url_for('profile'))

    return render_template('profile.html')

@app.route('/agregar_receta', methods=['POST'])
def agregar_receta():
    # Obtener datos del formulario
    nombre = request.form['nombre']
    ingredientes = request.form['ingredientes']
    cantidades = request.form['cantidades']
    modo = request.form['modo']
    photo = request.files.get('photo')

    receta_data = {
        'nombre': nombre,
        'ingredientes': ingredientes,
        'cantidades': cantidades,
        'modo': modo
    }

    if photo:
        # Crear un blob en el bucket para la imagen
        blob = bucket.blob(f"recetas/{photo.filename}")
        
        # Subir el archivo al bucket
        try:
            blob.upload_from_file(photo, content_type=photo.content_type)
            image_url = blob.public_url
            print(f"Imagen subida correctamente: {image_url}")
            receta_data['imagen_url'] = image_url  # Agregar la URL de la imagen

        except Exception as e:
            print(f"Error al subir la imagen: {e}")

    # Guardar la receta en Firestore
    db.collection('recetas').add(receta_data)

    return redirect('/recetas')  # Redirigir a la página de recetas

@app.route('/recetas')
def mostrar_recetas():
    # Recuperar recetas de Firestore
    recetas_ref = db.collection('recetas')
    recetas = recetas_ref.stream()
    
    # Convertir las recetas a una lista de diccionarios
    lista_recetas = []
    for receta in recetas:
        receta_dict = receta.to_dict()
        receta_dict['id'] = receta.id  # Agregar el ID de la receta
        lista_recetas.append(receta_dict)
    
    return render_template('recetas.html', recetas=lista_recetas)

if __name__ == '__main__':
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT, debug=True)
