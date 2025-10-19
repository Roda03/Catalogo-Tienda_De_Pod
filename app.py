from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'dcloud_secret_key_2024'

# Configuración
ADMIN_PASSWORD = "admin123"

# SQLite temporal
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Verificar si el usuario es mayor de edad
def es_mayor_de_edad():
    return session.get('mayor_de_edad', False)

# Inicializar base de datos
def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Crear tabla de sugerencias
    c.execute('''CREATE TABLE IF NOT EXISTS sugerencias_sabores
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  sabor TEXT NOT NULL,
                  fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Crear tabla de productos
    c.execute('''CREATE TABLE IF NOT EXISTS productos
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  nombre TEXT NOT NULL,
                  sabor TEXT NOT NULL,
                  precio INTEGER NOT NULL,
                  imagen TEXT NOT NULL,
                  stock INTEGER DEFAULT 1)''')
    
    # Verificar si hay productos, si no, insertar los predeterminados
    c.execute("SELECT COUNT(*) FROM productos")
    count = c.fetchone()[0]
    
    if count == 0:
        productos_iniciales = [
            ("Miami Mint", "Menta refrescante de Miami", 70000, "miami-mint.jpg", 3),
            ("Monster Drink", "Energética y revitalizante", 70000, "monster-drink.jpg", 2),
            ("Menthol", "Mentol clásico y refrescante", 70000, "menthol.jpg", 2),
            ("Blue Dragon Razz", "Dragon azul con frambuesa", 70000, "blue-dragon-razz.jpg", 2),
            ("Dragon Fruit", "Fruta del dragón tropical", 70000, "dragon-fruit.jpg", 2),
            ("Blackberry Ice", "Mora negra con hielo", 70000, "blackberry-ice.jpg", 1),
            ("Blueberry Mint", "Arándano con menta", 70000, "blueberry-mint.jpg", 2),
            ("Love 66", "Mezcla especial Love 66", 70000, "love-66.jpg", 2),
            ("Mint Waterberry", "Menta con frutos del bosque acuosos", 70000, "mint-waterberry.jpg", 2),
            ("Blueberry Strawberry", "Mezcla de arándano y fresa", 70000, "blueberry-strawberry.jpg", 1),
            ("Pink Lemonade", "Limonada rosa refrescante", 70000, "pink-lemonade.jpg", 1)
        ]
        
        c.executemany('''INSERT INTO productos (nombre, sabor, precio, imagen, stock) 
                         VALUES (?, ?, ?, ?, ?)''', productos_iniciales)
    
    conn.commit()
    conn.close()
    print("✅ Base de datos SQLite inicializada correctamente")

# Cargar productos desde SQLite
def cargar_productos():
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM productos ORDER BY id")
        productos = c.fetchall()
        conn.close()
        
        # Convertir a lista de diccionarios
        productos_list = []
        for producto in productos:
            productos_list.append(dict(producto))
        return productos_list
    except Exception as e:
        print(f"Error cargando productos: {e}")
        return []

# Guardar sugerencia de sabor
def guardar_sugerencia_sabor(sabor):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("INSERT INTO sugerencias_sabores (sabor) VALUES (?)", (sabor,))
        conn.commit()
        conn.close()
        print(f"✅ Sugerencia guardada: {sabor}")
        return True
    except Exception as e:
        print(f"❌ Error guardando sugerencia: {e}")
        return False

# Obtener sugerencias
def obtener_sugerencias_sabores():
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT id, sabor, fecha_creacion FROM sugerencias_sabores ORDER BY id DESC")
        sugerencias = c.fetchall()
        conn.close()
        
        # Convertir a lista de tuplas
        sugerencias_list = []
        for sugerencia in sugerencias:
            sugerencias_list.append(tuple(sugerencia))
        return sugerencias_list
    except Exception as e:
        print(f"Error obteniendo sugerencias: {e}")
        return []

# Actualizar stock
def actualizar_stock(producto_id, nuevo_stock):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("UPDATE productos SET stock = ? WHERE id = ?", (nuevo_stock, producto_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error actualizando stock: {e}")
        return False

# Ruta para diagnóstico de base de datos
@app.route('/debug-db')
def debug_db():
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        # Verificar tablas
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tablas = c.fetchall()
        
        # Verificar sugerencias
        c.execute("SELECT COUNT(*) FROM sugerencias_sabores")
        count_sugerencias = c.fetchone()[0]
        
        # Verificar productos
        c.execute("SELECT COUNT(*) FROM productos")
        count_productos = c.fetchone()[0]
        
        conn.close()
        
        return f"""
        <h1>Debug Base de Datos SQLite</h1>
        <p><strong>Tablas existentes:</strong> {[tabla[0] for tabla in tablas]}</p>
        <p><strong>Sugerencias en la tabla:</strong> {count_sugerencias}</p>
        <p><strong>Productos en la tabla:</strong> {count_productos}</p>
        <p style="color: green;">✅ Conexión SQLite exitosa</p>
        """
    except Exception as e:
        return f"<h1>Error: {str(e)}</h1>"

# Ruta principal - verificación de edad
@app.route('/', methods=['GET', 'POST'])
def edad_gate():
    if request.method == 'POST':
        opcion = request.form.get('edad')
        if opcion == 'si':
            session['mayor_de_edad'] = True
            session.permanent = True
            return redirect(url_for('index'))
        else:
            return redirect(url_for('acceso_denegado'))
    
    if es_mayor_de_edad():
        return redirect(url_for('index'))
    return render_template('edad_gate.html')

# Página de acceso denegado
@app.route('/acceso_denegado')
def acceso_denegado():
    return render_template('acceso_denegado.html')

# Catálogo principal
@app.route('/catalogo')
def index():
    if not es_mayor_de_edad():
        return redirect(url_for('edad_gate'))
    
    productos = cargar_productos()
    return render_template('index.html', productos=productos)

# Ruta para sugerir sabores
@app.route('/sugerir', methods=['POST'])
def sugerir():
    if not es_mayor_de_edad():
        return redirect(url_for('edad_gate'))
    
    sabor = request.form.get('sabor', '').strip()
    if sabor:
        if guardar_sugerencia_sabor(sabor):
            # Éxito
            return redirect(url_for('index'))
        else:
            # Error pero redirige igual para no interrumpir la experiencia
            print("Error al guardar sugerencia, pero continuando...")
            return redirect(url_for('index'))
    return redirect(url_for('index'))

# Panel de administración
@app.route('/admin')
def admin():
    password = request.args.get('pass', '')
    
    if password != ADMIN_PASSWORD:
        return "<h1>Acceso denegado</h1><p>Contraseña incorrecta o no proporcionada.</p>"
    
    sugerencias = obtener_sugerencias_sabores()
    productos = cargar_productos()
    return render_template('admin.html', sugerencias=sugerencias, productos=productos)

# Actualizar stock
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

# Ruta para agregar nuevos productos
@app.route('/agregar_producto', methods=['POST'])
def agregar_producto():
    password = request.args.get('pass', '')
    
    if password != ADMIN_PASSWORD:
        return jsonify({'error': 'Acceso denegado'}), 403
    
    try:
        nombre = request.form.get('nombre')
        sabor = request.form.get('sabor')
        precio = int(request.form.get('precio'))
        imagen = request.form.get('imagen')
        stock = int(request.form.get('stock', 1))
        
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('''INSERT INTO productos (nombre, sabor, precio, imagen, stock) 
                     VALUES (?, ?, ?, ?, ?)''', 
                 (nombre, sabor, precio, imagen, stock))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Producto agregado correctamente'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Ruta para salir (resetear verificación)
@app.route('/salir')
def salir():
    session.pop('mayor_de_edad', None)
    return redirect(url_for('edad_gate'))

# Inicializar la base de datos al inicio
with app.app_context():
    init_db()

if __name__ == '__main__':
    app.run(debug=True)