from functools import wraps
from datetime import datetime, timedelta
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, jsonify, Response
)
from werkzeug.security import check_password_hash, generate_password_hash
from database import get_connection, init_database, registrar_auditoria

app = Flask(__name__)
app.secret_key = "quantix-core-secret-key-2026"

ROLES = {
    "admin": ["dashboard", "clientes", "stock", "pedidos", "usuarios", "reportes"],
    "operador": ["dashboard", "clientes", "stock", "pedidos", "reportes"],
    "consulta": ["dashboard", "clientes", "stock", "pedidos", "reportes"],
}

PERMISOS_ESCRITURA = {
    "admin": ["clientes", "stock", "pedidos", "usuarios"],
    "operador": ["clientes", "stock", "pedidos"],
    "consulta": [],
}


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


def require_perm(permiso):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            rol = session.get("rol")
            if permiso not in PERMISOS_ESCRITURA.get(rol, []):
                flash("No tenés permisos para realizar esta acción.", "danger")
                return redirect(url_for("dashboard"))
            return f(*args, **kwargs)
        return wrapper
    return decorator


@app.context_processor
def inject_user():
    return {
        "current_user": session.get("nombre"),
        "current_rol": session.get("rol"),
        "menu": ROLES.get(session.get("rol"), []),
    }


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        conn = get_connection()
        user = conn.execute(
            "SELECT * FROM usuarios WHERE username = ? AND activo = 1", (username,)
        ).fetchone()
        conn.close()
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["nombre"] = user["nombre"]
            session["rol"] = user["rol"]
            registrar_auditoria(user["id"], "LOGIN", f"Ingreso de {username}")
            return redirect(url_for("dashboard"))
        flash("Credenciales inválidas.", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    if "user_id" in session:
        registrar_auditoria(session["user_id"], "LOGOUT", f"Salida de {session.get('username')}")
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
@login_required
def dashboard():
    conn = get_connection()
    total_clientes = conn.execute("SELECT COUNT(*) c FROM clientes").fetchone()["c"]
    total_productos = conn.execute("SELECT COUNT(*) c FROM productos").fetchone()["c"]
    total_pedidos = conn.execute("SELECT COUNT(*) c FROM pedidos").fetchone()["c"]
    pedidos_pendientes = conn.execute(
        "SELECT COUNT(*) c FROM pedidos WHERE estado = 'pendiente'"
    ).fetchone()["c"]
    valor_stock = conn.execute(
        "SELECT COALESCE(SUM(precio * stock),0) v FROM productos"
    ).fetchone()["v"]
    bajo_stock = conn.execute(
        "SELECT * FROM productos WHERE stock <= stock_minimo ORDER BY stock ASC"
    ).fetchall()
    ultimos_pedidos = conn.execute("""
        SELECT p.id, c.razon_social, p.fecha, p.estado, p.total
        FROM pedidos p JOIN clientes c ON c.id = p.cliente_id
        ORDER BY p.id DESC LIMIT 5
    """).fetchall()
    conn.close()
    return render_template(
        "dashboard.html",
        total_clientes=total_clientes,
        total_productos=total_productos,
        total_pedidos=total_pedidos,
        pedidos_pendientes=pedidos_pendientes,
        valor_stock=valor_stock,
        bajo_stock=bajo_stock,
        ultimos_pedidos=ultimos_pedidos,
    )


@app.route("/clientes")
@login_required
def clientes():
    q = request.args.get("q", "").strip()
    conn = get_connection()
    if q:
        rows = conn.execute(
            "SELECT * FROM clientes WHERE razon_social LIKE ? OR cuit LIKE ? ORDER BY id DESC",
            (f"%{q}%", f"%{q}%")
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM clientes ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("clientes.html", clientes=rows, q=q)


@app.route("/clientes/nuevo", methods=["POST"])
@login_required
@require_perm("clientes")
def cliente_nuevo():
    data = request.form
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO clientes (razon_social, cuit, email, telefono, direccion) VALUES (?, ?, ?, ?, ?)",
            (data["razon_social"], data.get("cuit"), data.get("email"),
             data.get("telefono"), data.get("direccion"))
        )
        conn.commit()
        registrar_auditoria(session["user_id"], "CLIENTE_ALTA", data["razon_social"])
        flash("Cliente creado correctamente.", "success")
    except Exception as e:
        flash(f"Error: {e}", "danger")
    conn.close()
    return redirect(url_for("clientes"))


@app.route("/clientes/<int:cid>/editar", methods=["POST"])
@login_required
@require_perm("clientes")
def cliente_editar(cid):
    data = request.form
    conn = get_connection()
    conn.execute(
        "UPDATE clientes SET razon_social=?, cuit=?, email=?, telefono=?, direccion=? WHERE id=?",
        (data["razon_social"], data.get("cuit"), data.get("email"),
         data.get("telefono"), data.get("direccion"), cid)
    )
    conn.commit()
    conn.close()
    registrar_auditoria(session["user_id"], "CLIENTE_EDIT", f"ID {cid}")
    flash("Cliente actualizado.", "success")
    return redirect(url_for("clientes"))


@app.route("/clientes/<int:cid>/eliminar", methods=["POST"])
@login_required
@require_perm("clientes")
def cliente_eliminar(cid):
    conn = get_connection()
    try:
        conn.execute("DELETE FROM clientes WHERE id=?", (cid,))
        conn.commit()
        registrar_auditoria(session["user_id"], "CLIENTE_DEL", f"ID {cid}")
        flash("Cliente eliminado.", "success")
    except Exception:
        flash("No se puede eliminar: tiene pedidos asociados.", "danger")
    conn.close()
    return redirect(url_for("clientes"))


@app.route("/stock")
@login_required
def stock():
    q = request.args.get("q", "").strip()
    conn = get_connection()
    if q:
        rows = conn.execute(
            "SELECT * FROM productos WHERE nombre LIKE ? OR codigo LIKE ? ORDER BY id DESC",
            (f"%{q}%", f"%{q}%")
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM productos ORDER BY id DESC").fetchall()
    movs = conn.execute("""
        SELECT m.*, p.nombre producto, u.nombre usuario
        FROM movimientos_stock m
        JOIN productos p ON p.id = m.producto_id
        LEFT JOIN usuarios u ON u.id = m.usuario_id
        ORDER BY m.id DESC LIMIT 20
    """).fetchall()
    conn.close()
    return render_template("stock.html", productos=rows, movimientos=movs, q=q)


@app.route("/stock/nuevo", methods=["POST"])
@login_required
@require_perm("stock")
def stock_nuevo():
    data = request.form
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO productos (codigo, nombre, categoria, precio, stock, stock_minimo) VALUES (?, ?, ?, ?, ?, ?)",
            (data["codigo"], data["nombre"], data.get("categoria"),
             float(data.get("precio") or 0), int(data.get("stock") or 0),
             int(data.get("stock_minimo") or 0))
        )
        conn.commit()
        registrar_auditoria(session["user_id"], "PRODUCTO_ALTA", data["nombre"])
        flash("Producto creado.", "success")
    except Exception as e:
        flash(f"Error: {e}", "danger")
    conn.close()
    return redirect(url_for("stock"))


@app.route("/stock/<int:pid>/movimiento", methods=["POST"])
@login_required
@require_perm("stock")
def stock_movimiento(pid):
    tipo = request.form["tipo"]
    cantidad = int(request.form["cantidad"])
    motivo = request.form.get("motivo", "")
    conn = get_connection()
    prod = conn.execute("SELECT * FROM productos WHERE id=?", (pid,)).fetchone()
    if not prod:
        conn.close()
        flash("Producto inexistente.", "danger")
        return redirect(url_for("stock"))
    nuevo = prod["stock"]
    if tipo == "entrada":
        nuevo += cantidad
    elif tipo == "salida":
        if cantidad > prod["stock"]:
            conn.close()
            flash("Stock insuficiente.", "danger")
            return redirect(url_for("stock"))
        nuevo -= cantidad
    else:
        nuevo = cantidad
    conn.execute("UPDATE productos SET stock=? WHERE id=?", (nuevo, pid))
    conn.execute(
        "INSERT INTO movimientos_stock (producto_id, tipo, cantidad, motivo, usuario_id) VALUES (?, ?, ?, ?, ?)",
        (pid, tipo, cantidad, motivo, session["user_id"])
    )
    conn.commit()
    conn.close()
    registrar_auditoria(session["user_id"], "STOCK_MOV", f"{tipo} {cantidad} prod {pid}")
    flash("Movimiento registrado.", "success")
    return redirect(url_for("stock"))


@app.route("/pedidos")
@login_required
def pedidos():
    conn = get_connection()
    rows = conn.execute("""
        SELECT p.*, c.razon_social
        FROM pedidos p JOIN clientes c ON c.id = p.cliente_id
        ORDER BY p.id DESC
    """).fetchall()
    clientes = conn.execute("SELECT id, razon_social FROM clientes ORDER BY razon_social").fetchall()
    productos = conn.execute("SELECT id, codigo, nombre, precio, stock FROM productos ORDER BY nombre").fetchall()
    conn.close()
    return render_template("pedidos.html", pedidos=rows, clientes=clientes, productos=productos)


@app.route("/pedidos/nuevo", methods=["POST"])
@login_required
@require_perm("pedidos")
def pedido_nuevo():
    cliente_id = int(request.form["cliente_id"])
    producto_id = int(request.form["producto_id"])
    cantidad = int(request.form["cantidad"])
    conn = get_connection()
    prod = conn.execute("SELECT * FROM productos WHERE id=?", (producto_id,)).fetchone()
    if not prod or prod["stock"] < cantidad:
        conn.close()
        flash("Stock insuficiente para el pedido.", "danger")
        return redirect(url_for("pedidos"))
    total = prod["precio"] * cantidad
    cur = conn.execute(
        "INSERT INTO pedidos (cliente_id, estado, total, creado_por) VALUES (?, 'pendiente', ?, ?)",
        (cliente_id, total, session["user_id"])
    )
    pedido_id = cur.lastrowid
    conn.execute(
        "INSERT INTO pedido_detalle (pedido_id, producto_id, cantidad, precio_unitario) VALUES (?, ?, ?, ?)",
        (pedido_id, producto_id, cantidad, prod["precio"])
    )
    conn.execute("UPDATE productos SET stock = stock - ? WHERE id=?", (cantidad, producto_id))
    conn.execute(
        "INSERT INTO movimientos_stock (producto_id, tipo, cantidad, motivo, usuario_id) VALUES (?, 'salida', ?, ?, ?)",
        (producto_id, cantidad, f"Pedido #{pedido_id}", session["user_id"])
    )
    conn.commit()
    conn.close()
    registrar_auditoria(session["user_id"], "PEDIDO_NUEVO", f"Pedido {pedido_id}")
    flash("Pedido creado correctamente.", "success")
    return redirect(url_for("pedidos"))


@app.route("/pedidos/<int:pid>/estado", methods=["POST"])
@login_required
@require_perm("pedidos")
def pedido_estado(pid):
    estado = request.form["estado"]
    conn = get_connection()
    conn.execute("UPDATE pedidos SET estado=? WHERE id=?", (estado, pid))
    conn.commit()
    conn.close()
    registrar_auditoria(session["user_id"], "PEDIDO_ESTADO", f"Pedido {pid} -> {estado}")
    flash("Estado actualizado.", "success")
    return redirect(url_for("pedidos"))


@app.route("/pedidos/<int:pid>/detalle")
@login_required
def pedido_detalle(pid):
    conn = get_connection()
    pedido = conn.execute("""
        SELECT p.*, c.razon_social, c.cuit, u.nombre as vendedor
        FROM pedidos p
        JOIN clientes c ON c.id = p.cliente_id
        LEFT JOIN usuarios u ON u.id = p.creado_por
        WHERE p.id=?
    """, (pid,)).fetchone()
    items = conn.execute("""
        SELECT d.*, pr.nombre, pr.codigo
        FROM pedido_detalle d
        JOIN productos pr ON pr.id = d.producto_id
        WHERE d.pedido_id=?
    """, (pid,)).fetchall()
    conn.close()
    return jsonify({
        "pedido": dict(pedido) if pedido else None,
        "items": [dict(i) for i in items]
    })


@app.route("/usuarios")
@login_required
def usuarios():
    if session.get("rol") != "admin":
        flash("Acceso restringido.", "danger")
        return redirect(url_for("dashboard"))
    conn = get_connection()
    rows = conn.execute("SELECT * FROM usuarios ORDER BY id").fetchall()
    conn.close()
    return render_template("usuarios.html", usuarios=rows)


@app.route("/usuarios/nuevo", methods=["POST"])
@login_required
@require_perm("usuarios")
def usuario_nuevo():
    data = request.form
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO usuarios (username, password_hash, nombre, rol) VALUES (?, ?, ?, ?)",
            (data["username"], generate_password_hash(data["password"]),
             data["nombre"], data["rol"])
        )
        conn.commit()
        registrar_auditoria(session["user_id"], "USUARIO_ALTA", data["username"])
        flash("Usuario creado.", "success")
    except Exception as e:
        flash(f"Error: {e}", "danger")
    conn.close()
    return redirect(url_for("usuarios"))


@app.route("/usuarios/<int:uid>/toggle", methods=["POST"])
@login_required
@require_perm("usuarios")
def usuario_toggle(uid):
    conn = get_connection()
    conn.execute("UPDATE usuarios SET activo = CASE activo WHEN 1 THEN 0 ELSE 1 END WHERE id=?", (uid,))
    conn.commit()
    conn.close()
    registrar_auditoria(session["user_id"], "USUARIO_TOGGLE", f"ID {uid}")
    flash("Estado de usuario actualizado.", "success")
    return redirect(url_for("usuarios"))


@app.route("/reportes")
@login_required
def reportes():
    dias = int(request.args.get("dias", 30))
    desde = (datetime.now() - timedelta(days=dias)).strftime("%Y-%m-%d")
    conn = get_connection()
    ventas = conn.execute("""
        SELECT DATE(fecha) dia, COUNT(*) cantidad, SUM(total) total
        FROM pedidos
        WHERE fecha >= ? AND estado != 'cancelado'
        GROUP BY DATE(fecha)
        ORDER BY dia DESC
    """, (desde,)).fetchall()
    top_productos = conn.execute("""
        SELECT pr.nombre, SUM(d.cantidad) unidades, SUM(d.cantidad * d.precio_unitario) total
        FROM pedido_detalle d
        JOIN productos pr ON pr.id = d.producto_id
        JOIN pedidos p ON p.id = d.pedido_id
        WHERE p.fecha >= ?
        GROUP BY pr.id
        ORDER BY unidades DESC
        LIMIT 10
    """, (desde,)).fetchall()
    por_estado = conn.execute(
        "SELECT estado, COUNT(*) c, SUM(total) t FROM pedidos GROUP BY estado"
    ).fetchall()
    auditoria = conn.execute("""
        SELECT a.*, u.username
        FROM auditoria a
        LEFT JOIN usuarios u ON u.id = a.usuario_id
        ORDER BY a.id DESC LIMIT 30
    """).fetchall()
    conn.close()
    return render_template(
        "reportes.html",
        ventas=ventas,
        top_productos=top_productos,
        por_estado=por_estado,
        auditoria=auditoria,
        dias=dias,
    )


@app.route("/reportes/export.csv")
@login_required
def export_csv():
    conn = get_connection()
    rows = conn.execute("""
        SELECT p.id, c.razon_social, p.fecha, p.estado, p.total
        FROM pedidos p JOIN clientes c ON c.id = p.cliente_id
        ORDER BY p.id DESC
    """).fetchall()
    conn.close()
    def generar():
        yield "ID,Cliente,Fecha,Estado,Total\n"
        for r in rows:
            yield f"{r['id']},{r['razon_social']},{r['fecha']},{r['estado']},{r['total']}\n"
    return Response(
        generar(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=reporte_pedidos.csv"}
    )


if __name__ == "__main__":
    init_database()
    app.run(debug=True, host="0.0.0.0", port=5000)
