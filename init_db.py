from database import init_database, get_connection
from werkzeug.security import generate_password_hash

init_database()

conn = get_connection()
cur = conn.cursor()

usuarios = [
    ("admin", generate_password_hash("admin123"), "Administrador General", "admin"),
    ("operador", generate_password_hash("operador123"), "Operador de Depósito", "operador"),
    ("consulta", generate_password_hash("consulta123"), "Usuario de Consulta", "consulta"),
]

for u in usuarios:
    cur.execute(
        "INSERT OR IGNORE INTO usuarios (username, password_hash, nombre, rol) VALUES (?, ?, ?, ?)",
        u
    )

productos = [
    ("P001", "Notebook Lenovo IdeaPad 3", "Informática", 850000, 12, 5),
    ("P002", "Mouse Logitech M170", "Periféricos", 12000, 45, 10),
    ("P003", "Teclado Redragon K552", "Periféricos", 65000, 8, 5),
    ("P004", "Monitor Samsung 24\"", "Informática", 320000, 6, 3),
    ("P005", "Auriculares HyperX Cloud", "Audio", 95000, 20, 8),
]

for p in productos:
    cur.execute(
        "INSERT OR IGNORE INTO productos (codigo, nombre, categoria, precio, stock, stock_minimo) VALUES (?, ?, ?, ?, ?, ?)",
        p
    )

clientes = [
    ("Distribuidora del Norte S.A.", "30-71234567-9", "ventas@delnorte.com", "1145551234", "Av. Rivadavia 1234, CABA"),
    ("TecnoShop SRL", "30-70987654-3", "contacto@tecnoshop.com", "1155559876", "Calle Florida 567, CABA"),
    ("Comercial Andina S.A.", "30-70111222-4", "info@andina.com", "1166664321", "Av. Córdoba 890, CABA"),
]

for c in clientes:
    cur.execute(
        "INSERT OR IGNORE INTO clientes (razon_social, cuit, email, telefono, direccion) VALUES (?, ?, ?, ?, ?)",
        c
    )

conn.commit()
conn.close()

print("Base de datos inicializada correctamente.")
print("Usuarios: admin/admin123 | operador/operador123 | consulta/consulta123")
