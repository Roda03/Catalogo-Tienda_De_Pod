from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import json
import sqlite3
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'dcloud_secret_key_2024'  # Clave para las sesiones

# Configuración
ADMIN_PASSWORD = "admin123"

# Verificar si el usuario es mayor de edad
def es_mayor_de_edad():
    return session.get('mayor_de_edad', False)

# Inicializar base de datos de sugerencias
def init_db():
    conn = sqlite3.connect('sugerencias.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sugerencias_sabores
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  sabor TEXT NOT NULL)''')
    conn.commit()
    conn.close()

# Cargar productos desde JSON
def cargar_productos():
    try:
        with open('productos.json', 'r', encoding='utf-8') as f:
            productos = json.load(f)
            for producto in productos:
                if 'stock' not in producto:
                    producto['stock'] = 1
            return productos
    except FileNotFoundError:
        return []

# Guardar sugerencia de sabor
def guardar_sugerencia_sabor(sabor):
    conn = sqlite3.connect('sugerencias.db')
    c = conn.cursor()
    c.execute("INSERT INTO sugerencias_sabores (sabor) VALUES (?)", (sabor,))
    conn.commit()
    conn.close()

# Obtener sugerencias
def obtener_sugerencias_sabores():
    conn = sqlite3.connect('sugerencias.db')
    c = conn.cursor()
    c.execute("SELECT * FROM sugerencias_sabores ORDER BY id DESC")
    sugerencias = c.fetchall()
    conn.close()
    return sugerencias

# Actualizar stock
def actualizar_stock(producto_id, nuevo_stock):
    try:
        with open('productos.json', 'r', encoding='utf-8') as f:
            productos = json.load(f)
        
        for producto in productos:
            if producto.get('id') == producto_id:
                producto['stock'] = nuevo_stock
                break
        
        with open('productos.json', 'w', encoding='utf-8') as f:
            json.dump(productos, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"Error actualizando stock: {e}")
        return False

# Ruta para verificación de edad
@app.route('/verificar_edad', methods=['POST'])
def verificar_edad():
    opcion = request.form.get('edad')
    if opcion == 'si':
        session['mayor_de_edad'] = True
        session.permanent = True
        return redirect(url_for('index'))
    else:
        return redirect(url_for('acceso_denegado'))

# Página de acceso denegado
@app.route('/acceso_denegado')
def acceso_denegado():
    return render_template('acceso_denegado.html')

# Página de verificación de edad
@app.route('/')
def edad_gate():
    if es_mayor_de_edad():
        return redirect(url_for('index'))
    return render_template('edad_gate.html')

# Catálogo principal (solo accesible si es mayor de edad)
@app.route('/catalogo')
def index():
    if not es_mayor_de_edad():
        return redirect(url_for('edad_gate'))
    
    productos = cargar_productos()
    return render_template('index.html', productos=productos)

@app.route('/sugerir', methods=['POST'])
def sugerir():
    if not es_mayor_de_edad():
        return redirect(url_for('edad_gate'))
    
    sabor = request.form.get('sabor', '').strip()
    if sabor:
        guardar_sugerencia_sabor(sabor)
    return redirect(url_for('index'))

@app.route('/admin')
def admin():
    password = request.args.get('pass', '')
    
    if password != ADMIN_PASSWORD:
        return "<h1>Acceso denegado</h1><p>Contraseña incorrecta o no proporcionada.</p>"
    
    sugerencias = obtener_sugerencias_sabores()
    productos = cargar_productos()
    return render_template('admin.html', sugerencias=sugerencias, productos=productos)

@app.route('/actualizar_stock', methods=['POST'])
def actualizar_stock_route():
    password = request.args.get('pass', '')
    
    if password != ADMIN_PASSWORD:
        return jsonify({'error': 'Acceso denegado'}), 403
    
    producto_id = request.form.get('producto_id')
    nuevo_stock = request.form.get('nuevo_stock')
    
    try:
        producto_id = int(producto_id)
        nuevo_stock = int(nuevo_stock)
        
        if actualizar_stock(producto_id, nuevo_stock):
            return jsonify({'success': True, 'message': 'Stock actualizado correctamente'})
        else:
            return jsonify({'error': 'Error al actualizar stock'}), 500
            
    except ValueError:
        return jsonify({'error': 'ID de producto o stock inválido'}), 400

# Ruta para salir (resetear verificación)
@app.route('/salir')
def salir():
    session.pop('mayor_de_edad', None)
    return redirect(url_for('edad_gate'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)