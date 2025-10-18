import requests
import os

# Crear carpeta de imágenes
os.makedirs('static/images', exist_ok=True)

# Lista de imágenes a descargar
imagenes = {
    'miami-mint.jpg': 'https://images.unsplash.com/photo-1604908550668-82c5712dde53?w=300&h=200&fit=crop&auto=format',
    'monster-drink.jpg': 'https://images.unsplash.com/photo-1570193021132-f8e13b9b13d7?w=300&h=200&fit=crop&auto=format',
    'menthol.jpg': 'https://images.unsplash.com/photo-1572490122747-3968b75cc699?w=300&h=200&fit=crop&auto=format',
    'blue-dragon-razz.jpg': 'https://images.unsplash.com/photo-1560769684-55015cee73a8?w=300&h=200&fit=crop&auto=format',
    'dragon-fruit.jpg': 'https://images.unsplash.com/photo-1553279768-865429fa0078?w=300&h=200&fit=crop&auto=format',
    'blackberry-ice.jpg': 'https://images.unsplash.com/photo-1553279768-865429fa0078?w=300&h=200&fit=crop&auto=format',
    'blueberry-mint.jpg': 'https://images.unsplash.com/photo-1572490122747-3968b75cc699?w=300&h=200&fit=crop&auto=format',
    'love-66.jpg': 'https://images.unsplash.com/photo-1604908550668-82c5712dde53?w=300&h=200&fit=crop&auto=format',
    'mint-waterberry.jpg': 'https://images.unsplash.com/photo-1560769684-55015cee73a8?w=300&h=200&fit=crop&auto=format',
    'blueberry-strawberry.jpg': 'https://images.unsplash.com/photo-1570193021132-f8e13b9b13d7?w=300&h=200&fit=crop&auto=format',
    'pink-lemonade.jpg': 'https://images.unsplash.com/photo-1553279768-865429fa0078?w=300&h=200&fit=crop&auto=format'
}

def descargar_imagen(nombre, url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(f'static/images/{nombre}', 'wb') as f:
                f.write(response.content)
            print(f'✅ Descargada: {nombre}')
        else:
            print(f'❌ Error descargando {nombre}: {response.status_code}')
    except Exception as e:
        print(f'❌ Error con {nombre}: {e}')

# Descargar todas las imágenes
for nombre, url in imagenes.items():
    descargar_imagen(nombre, url)

print("🎉 ¡Descarga completada!")