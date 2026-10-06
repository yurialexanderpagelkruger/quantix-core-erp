LANGUAGES = {
    "en": {
        "app_name": "Quantix Core",
        "dashboard": "Dashboard",
        "clientes": "Clients",
        "stock": "Stock",
        "pedidos": "Orders",
        "usuarios": "Users",
        "reportes": "Reports",
        "logout": "Logout",
        "panel_control": "Control Panel",
        "total_clientes": "Clients",
        "total_productos": "Products",
        "total_pedidos": "Orders",
        "pedidos_pendientes": "Pending Orders",
        "valor_stock": "Total Stock Value",
        "bajo_stock": "Products below minimum stock",
        "sin_alertas": "No stock alerts.",
        "ultimos_pedidos": "Latest orders",
        "cliente": "Client",
        "fecha": "Date",
        "estado": "Status",
        "total": "Total",
        "sin_pedidos": "No orders registered.",
        "codigo": "Code",
        "producto": "Product",
        "minimo": "Minimum",
        "login_title": "Sign in",
        "username": "Username",
        "password": "Password",
        "sign_in": "Sign in",
        "invalid_credentials": "Invalid credentials.",
        "dark_mode": "Dark mode",
        "light_mode": "Light mode",
        "language": "Language",
    },
    "es": {
        "app_name": "Quantix Core",
        "dashboard": "Panel",
        "clientes": "Clientes",
        "stock": "Stock",
        "pedidos": "Pedidos",
        "usuarios": "Usuarios",
        "reportes": "Reportes",
        "logout": "Salir",
        "panel_control": "Panel de Control",
        "total_clientes": "Clientes",
        "total_productos": "Productos",
        "total_pedidos": "Pedidos",
        "pedidos_pendientes": "Pedidos Pendientes",
        "valor_stock": "Valor total del Stock",
        "bajo_stock": "Productos bajo stock mínimo",
        "sin_alertas": "Sin alertas de stock.",
        "ultimos_pedidos": "Últimos pedidos",
        "cliente": "Cliente",
        "fecha": "Fecha",
        "estado": "Estado",
        "total": "Total",
        "sin_pedidos": "Sin pedidos registrados.",
        "codigo": "Código",
        "producto": "Producto",
        "minimo": "Mínimo",
        "login_title": "Ingresar",
        "username": "Usuario",
        "password": "Contraseña",
        "sign_in": "Ingresar",
        "invalid_credentials": "Credenciales inválidas.",
        "dark_mode": "Modo oscuro",
        "light_mode": "Modo claro",
        "language": "Idioma",
    },
    "pt": {
        "app_name": "Quantix Core",
        "dashboard": "Painel",
        "clientes": "Clientes",
        "stock": "Estoque",
        "pedidos": "Pedidos",
        "usuarios": "Usuários",
        "reportes": "Relatórios",
        "logout": "Sair",
        "panel_control": "Painel de Controle",
        "total_clientes": "Clientes",
        "total_productos": "Produtos",
        "total_pedidos": "Pedidos",
        "pedidos_pendientes": "Pedidos Pendentes",
        "valor_stock": "Valor total do Estoque",
        "bajo_stock": "Produtos abaixo do estoque mínimo",
        "sin_alertas": "Sem alertas de estoque.",
        "ultimos_pedidos": "Últimos pedidos",
        "cliente": "Cliente",
        "fecha": "Data",
        "estado": "Status",
        "total": "Total",
        "sin_pedidos": "Nenhum pedido registrado.",
        "codigo": "Código",
        "producto": "Produto",
        "minimo": "Mínimo",
        "login_title": "Entrar",
        "username": "Usuário",
        "password": "Senha",
        "sign_in": "Entrar",
        "invalid_credentials": "Credenciais inválidas.",
        "dark_mode": "Modo escuro",
        "light_mode": "Modo claro",
        "language": "Idioma",
    },
}


def detect_language(accept_language_header):
    if not accept_language_header:
        return "en"

    langs = []
    for part in accept_language_header.split(","):
        part = part.strip()
        if ";" in part:
            code, q = part.split(";", 1)
            try:
                q_val = float(q.split("=")[1])
            except Exception:
                q_val = 0.0
            langs.append((code.strip().lower(), q_val))
        else:
            langs.append((part.lower(), 1.0))

    langs.sort(key=lambda x: x[1], reverse=True)

    for code, _ in langs:
        if code.startswith("es"):
            return "es"
        if code.startswith("pt"):
            return "pt"
        if code.startswith("en"):
            return "en"

    return "en"
