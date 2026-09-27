"""
=============================================================================
PROYECTO: Mini ERP - Muse Studio ("Tu mayorista online")
MÓDULO: app.py
=============================================================================
"""
import os
from flask import Flask, render_template_string, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from database import db
from models import User, Product, Purchase, Sale, Invoice, InvoiceItem
from config.icons_colors import Theme
from utils import generate_sku, toggle_product_status, delete_product, generate_invoice_number

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'muse_studio_secreta_2026')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///muse_studio_erp.db')

db.init_app(app)

# Filtro para formato de moeda con separador de miles
@app.template_filter('money')
def money_filter(value):
    if value is None:
        return '$ 0.00'
    try:
        return '$ {:,.2f}'.format(float(value))
    except:
        return '$ 0.00'

with app.app_context():
    print("🔨 Preparando banco de datos...")
    db.create_all()
    print("✅ Tablas creadas/verificadas con éxito!")
    if not User.query.filter_by(username='dev').first():
        db.session.add(User(username='dev', password=generate_password_hash('dev123'), role='dev'))
    if not User.query.filter_by(username='admin').first():
        db.session.add(User(username='admin', password=generate_password_hash('admin123'), role='admin'))
    db.session.commit()

TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Muse Studio - Mini ERP</title>
    <style>
        :root { --bg-dark: #121212; --gold: #D4AF37; --pink: #FF69B4; --light-pink: #FFF0F5; --danger: #ff6b6b; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f9f9f9; margin: 0; padding: 0; color: #333; }
        .header { background: var(--bg-dark); color: var(--gold); padding: 20px; text-align: center; border-bottom: 3px solid var(--pink); }
        .header h1 { margin: 0; font-size: 24px; }
        .header p { margin: 5px 0 0 0; color: var(--pink); font-size: 14px; }
        .container { max-width: 1000px; margin: 30px auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); }
        .btn { background: var(--gold); color: #000; padding: 10px 18px; border: none; border-radius: 5px; font-weight: bold; cursor: pointer; text-decoration: none; display: inline-block; }
        .btn-pink { background: var(--pink); color: white; }
        .btn-dark { background: var(--bg-dark); color: var(--gold); }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #e0e0e0; padding: 12px; text-align: left; }
        th { background-color: var(--light-pink); }
        .alert { padding: 12px; background: #d4edda; color: #155724; margin-bottom: 20px; border-radius: 5px; }
        form input, form select { padding: 10px; margin: 8px 0 15px 0; width: 100%; box-sizing: border-box; border: 1px solid #ccc; border-radius: 5px; }
        .nav-bar { background: #222; color: white; border-bottom: 2px solid var(--pink); }
        .nav-bar a { color: var(--gold); text-decoration: none; transition: all 0.3s ease; }
        .nav-bar a:hover { background: rgba(212, 175, 55, 0.2) !important; transform: translateY(-2px); }
        .kpi-container { display: flex; gap: 20px; margin-bottom: 25px; }
        .kpi-card { flex: 1; background: #fff5f8; border: 1px solid #ffccd5; padding: 20px; border-radius: 8px; text-align: center; }
        .kpi-card h3 { margin: 0; color: #666; font-size: 14px; }
        .kpi-card p { margin: 10px 0 0 0; font-size: 22px; font-weight: bold; color: var(--pink); }
        .quick-actions { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin-bottom: 25px; }
        .kpi-value { transition: filter 0.3s ease; }
        .kpi-value.hidden { filter: blur(8px); }
        .kpi-value.hidden::after { content: '••••'; position: absolute; left: 50%; transform: translateX(-50%); }
        button[onclick*="toggleValues"] { transition: all 0.3s ease; }
    </style>
</head>
<body>

<div class="header">
    <img src="{{ theme.LOGO.path }}" alt="{{ theme.LOGO.alt }}" style="max-width: 140px; max-height: 140px; margin-bottom: 10px;">
    <h1>{{ theme.BRAND.name }}</h1>
    <p>{{ theme.BRAND.tagline }} • {{ theme.BRAND.description }}</p>
</div>

{% if session.get('user') %}
<div class="nav-bar" style="display: flex; justify-content: space-between; align-items: center; padding: 15px 30px;">
    <div style="display: flex; align-items: center; gap: 10px;">
        <span style="font-size: 14px; color: #999;">Sesión activa:</span>
        <b style="color: var(--gold); font-size: 16px;">{{ session['user'] | upper }}</b>
        <span style="background: var(--pink); color: white; padding: 3px 8px; border-radius: 3px; font-size: 12px; font-weight: bold;">{{ session['role'] | upper }}</span>
    </div>

    <div style="display: flex; gap: 20px; align-items: center;">
        {% if session['role'] == 'dev' %}
            <a href="/dev" style="display: flex; align-items: center; gap: 8px; color: var(--gold); text-decoration: none; font-weight: bold; padding: 8px 15px; background: rgba(255,255,255,0.1); border-radius: 5px; transition: all 0.3s;">
                🏠 Inicio
            </a>
        {% elif session['role'] == 'admin' %}
            <a href="/admin" style="display: flex; align-items: center; gap: 8px; color: var(--gold); text-decoration: none; font-weight: bold; padding: 8px 15px; background: rgba(255,255,255,0.1); border-radius: 5px; transition: all 0.3s;">
                🏠 Inicio
            </a>
        {% endif %}

        <div style="height: 25px; width: 1px; background: rgba(255,255,255,0.2);"></div>

        <a href="/logout" style="display: flex; align-items: center; gap: 8px; color: #ff6b6b; text-decoration: none; font-weight: bold; padding: 8px 15px; background: rgba(255,107,107,0.1); border-radius: 5px; transition: all 0.3s; border: 1px solid rgba(255,107,107,0.3);">
            🚪 Salir
        </a>
    </div>
</div>
{% endif %}

<div class="container">
    {% with messages = get_flashed_messages() %}
      {% if messages %}
        <div class="alert">{{ messages[0] }}</div>
      {% endif %}
    {% endwith %}

    {% if request.endpoint == 'login' %}
        <h2>Iniciar Sesión - Muse Studio</h2>
        <form method="POST">
            <label>Usuario:</label>
            <input type="text" name="username" required>
            <label>Contraseña:</label>
            <input type="password" name="password" required>
            <button type="submit" class="btn">Entrar</button>
        </form>
        <p><small>• Dev: <b>dev</b> / dev123<br>• Admin: <b>admin</b> / admin123</small></p>

    {% elif session.get('role') == 'dev' %}
        <h2>Panel de Desarrollador - Gestión de Usuarios</h2>
        <form method="POST" action="/dev/create_user" style="background: #fafafa; padding: 20px; border-radius: 8px; border: 1px solid #eee;">
            <h3>Registrar Nuevo Usuario</h3>
            <label>Nombre de Usuario:</label>
            <input type="text" name="new_user" required>
            <label>Contraseña:</label>
            <input type="password" name="new_password" required>
            <label>Rol:</label>
            <select name="role">
                <option value="admin">Admin (ERP)</option>
                <option value="dev">Dev</option>
            </select>
            <button type="submit" class="btn btn-pink">Crear Usuario</button>
        </form>
        <table>
            <tr><th>ID</th><th>Usuario</th><th>Rol</th></tr>
            {% for u in users %}
            <tr><td>{{ u.id }}</td><td><b>{{ u.username }}</b></td><td>{{ u.role | upper }}</td></tr>
            {% endfor %}
        </table>

    {% elif session.get('role') == 'admin' and request.endpoint == 'admin_dashboard' %}
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px;">
            <h2 style="margin: 0;">{{ theme.OPERATIONS.historial }} Dashboard General - Muse Studio</h2>
            <button type="button" onclick="toggleValuesVisibility()" style="background: var(--bg-dark); color: var(--gold); border: 2px solid var(--gold); padding: 10px 15px; border-radius: 5px; cursor: pointer; font-size: 18px; font-weight: bold;">
                👁️ Mostrar
            </button>
        </div>

        <div class="kpi-container">
            <div class="kpi-card">
                <h3>📊 Productos Activos</h3>
                <p class="kpi-value">{{ total_products }}</p>
            </div>
            <div class="kpi-card">
                <h3>⚠️ Alertas Stock Bajo</h3>
                <p class="kpi-value" style="color: #e63946;">{{ low_stock_count }}</p>
            </div>
            <div class="kpi-card">
                <h3>💰 Valor Inventario</h3>
                <p class="kpi-value" style="color: var(--gold);">{{ total_inventory_value | money }}</p>
            </div>
        </div>

        <div style="margin-top: 35px; margin-bottom: 25px; border-top: 2px solid #e0e0e0; padding-top: 25px;">
            <h3 style="margin-bottom: 20px;">⚡ Accesos Rápidos (Flujo Operativo)</h3>
            <div class="quick-actions">
                <a href="/admin/sale" class="btn btn-pink" style="text-align: center; padding: 15px; font-size: 14px; font-weight: bold;">{{ theme.OPERATIONS.salida }}<br>1. Venta</a>
                <a href="/admin/catalog" class="btn btn-dark" style="text-align: center; padding: 15px; font-size: 14px; font-weight: bold;">{{ theme.OPERATIONS.historial }}<br>2. Catálogo</a>
                <a href="/admin/product/new" class="btn" style="text-align: center; padding: 15px; font-size: 14px; font-weight: bold; background: #4CAF50; color: white;">{{ theme.ACTIONS.guardar }}<br>3. Nuevo</a>
                <a href="/admin/purchase" class="btn btn-dark" style="text-align: center; padding: 15px; font-size: 14px; font-weight: bold;">{{ theme.OPERATIONS.entrada }}<br>4. Entrada</a>
                <a href="/admin/sales-history" class="btn" style="text-align: center; padding: 15px; font-size: 14px; font-weight: bold; background: #FF6B9D; color: white;">📊<br>5. Análisis</a>
                <a href="/admin/price-guide" class="btn" style="text-align: center; padding: 15px; font-size: 14px; font-weight: bold; background: #2196F3; color: white;">{{ theme.OPERATIONS.historial }}<br>6. Guía</a>
            </div>
        </div>

        <script>
            let valuesVisible = true;
            function toggleValuesVisibility() {
                const values = document.querySelectorAll('.kpi-value');
                const button = event.target;

                valuesVisible = !valuesVisible;

                values.forEach(v => {
                    if (valuesVisible) {
                        v.classList.remove('hidden');
                    } else {
                        v.classList.add('hidden');
                    }
                });

                button.textContent = valuesVisible ? '👁️ Mostrar' : '🙈 Ocultar';
                button.style.background = valuesVisible ? 'var(--bg-dark)' : '#f44336';
                button.style.borderColor = valuesVisible ? 'var(--gold)' : '#f44336';
            }
        </script>

        <h3 style="margin-top: 30px;">⚠️ Alertas de Stock Bajo o Crítico</h3>
        <table>
            <tr><th>{{ theme.INFORMATION.codigo }} Código</th><th>📦 Producto</th><th>{{ theme.INFORMATION.precio }} Categoría</th><th>{{ theme.INFORMATION.stock }} Stock</th><th>⚠️ Mínimo</th><th>💡 Acción</th></tr>
            {% for p in low_stock_products %}
            <tr>
                <td>{{ p.code }}</td>
                <td><b>{{ p.name }}</b></td>
                <td>{{ p.category }}</td>
                <td style="color: #e63946; font-weight: bold;">{{ p.stock }}</td>
                <td>{{ p.min_stock }}</td>
                <td><a href="/admin/purchase" class="btn" style="padding: 5px 10px; font-size: 12px;">📥 Reponer</a></td>
            </tr>
            {% else %}
            <tr><td colspan="6" style="text-align: center; color: green;">¡Todo el inventario está en niveles óptimos!</td></tr>
            {% endfor %}
        </table>

    {% elif request.endpoint == 'cash_flow' %}
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h2>{{ theme.OPERATIONS.historial }} Flujo de Caja (últimos 30 días)</h2>
            <a href="/admin" class="btn-dark btn" style="font-size: 13px;">← Volver al Dashboard</a>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-bottom: 30px;">
            <div style="background: #fff5f8; padding: 20px; border-radius: 8px; text-align: center; border-left: 4px solid #4CAF50;">
                <h3 style="margin: 0; color: #666; font-size: 14px;">💰 Total Ventas (Entrada)</h3>
                <p style="font-size: 24px; color: #4CAF50; font-weight: bold; margin: 10px 0;">$ {{ "%.2f"|format(total_sales) }}</p>
            </div>
            <div style="background: #fff5f8; padding: 20px; border-radius: 8px; text-align: center; border-left: 4px solid #f44336;">
                <h3 style="margin: 0; color: #666; font-size: 14px;">🛒 Total Compras (Salida)</h3>
                <p style="font-size: 24px; color: #f44336; font-weight: bold; margin: 10px 0;">$ {{ "%.2f"|format(total_purchases) }}</p>
            </div>
            <div style="background: {% if balance >= 0 %}#e8f5e9{% else %}#ffebee{% endif %}; padding: 20px; border-radius: 8px; text-align: center; border-left: 4px solid {% if balance >= 0 %}#4CAF50{% else %}#f44336{% endif %};">
                <h3 style="margin: 0; color: #666; font-size: 14px;">📊 Saldo Neto</h3>
                <p style="font-size: 24px; color: {% if balance >= 0 %}#4CAF50{% else %}#f44336{% endif %}; font-weight: bold; margin: 10px 0;">$ {{ "%.2f"|format(balance) }}</p>
            </div>
        </div>
        <h3>Movimientos por Fecha</h3>
        <table>
            <tr>
                <th>📅 Fecha</th>
                <th style="text-align: right; color: #4CAF50;">💰 Ventas ($)</th>
                <th style="text-align: right; color: #f44336;">🛒 Compras ($)</th>
                <th style="text-align: right;">📊 Saldo Día ($)</th>
            </tr>
            {% for fecha, datos in cash_flow_data %}
            <tr>
                <td>{{ fecha }}</td>
                <td style="text-align: right; color: #4CAF50; font-weight: bold;">{{ "%.2f"|format(datos.ventas) }}</td>
                <td style="text-align: right; color: #f44336; font-weight: bold;">{{ "%.2f"|format(datos.compras) }}</td>
                <td style="text-align: right; background: {% if (datos.ventas - datos.compras) >= 0 %}#e8f5e9{% else %}#ffebee{% endif %}; font-weight: bold;">{{ "%.2f"|format(datos.ventas - datos.compras) }}</td>
            </tr>
            {% endfor %}
        </table>

    {% elif request.endpoint == 'price_guide' %}
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h2>{{ theme.OPERATIONS.historial }} Guía de Precios y Ventas</h2>
            <a href="/admin" class="btn-dark btn" style="font-size: 13px;">← Volver al Dashboard</a>
        </div>
        <p style="color: #666; margin-bottom: 20px;">Histórico de ventas y precios promedio para cada producto (últimos 15 y 30 días)</p>
        <table>
            <tr>
                <th>{{ theme.INFORMATION.codigo }} SKU</th>
                <th>📦 Producto</th>
                <th>{{ theme.INFORMATION.costo }} Costo Prom.</th>
                <th>📊 Ventas 15d</th>
                <th>💰 Precio Prom. 15d</th>
                <th>📊 Ventas 30d</th>
                <th>💰 Precio Prom. 30d</th>
                <th>{{ theme.INFORMATION.stock }} Stock</th>
                <th>{{ theme.INFORMATION.estado }} Estado</th>
            </tr>
            {% for p in product_data %}
            <tr style="{% if p.status == 'inactivo' %}opacity: 0.6;{% endif %}">
                <td><code style="background: #f0f0f0; padding: 3px 6px; border-radius: 3px;">{{ p.code }}</code></td>
                <td><b>{{ p.name }}</b></td>
                <td>{{ p.avg_cost | money }}</td>
                <td style="text-align: center;">{{ p.qty_15 }} un</td>
                <td style="color: #2196F3; font-weight: bold;">{{ p.price_avg_15 | money }}</td>
                <td style="text-align: center;">{{ p.qty_30 }} un</td>
                <td style="color: #4CAF50; font-weight: bold;">{{ p.price_avg_30 | money }}</td>
                <td>{{ p.stock }}</td>
                <td>
                    {% if p.status == 'ativo' %}
                        <span style="color: #4CAF50;">{{ theme.INFORMATION.activo }}</span>
                    {% else %}
                        <span style="color: #f44336;">{{ theme.INFORMATION.inactivo }}</span>
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
        </table>

    {% elif request.endpoint == 'admin_catalog' %}
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h2>{{ theme.OPERATIONS.historial }} Catálogo de Productos</h2>
            <a href="/admin" class="btn-dark btn" style="font-size: 13px;">← Volver al Dashboard</a>
        </div>
        <div style="margin: 15px 0;">
            <a href="/admin/product/new" class="btn btn-pink">➕ Nuevo Producto</a>
        </div>
        <div style="margin-bottom: 15px;">
            <input type="text" id="filterInput" placeholder="🔍 Buscar en tabla..." style="padding: 10px; border: 1px solid #ccc; border-radius: 5px; width: 300px;">
        </div>
        <table id="dataTable">
            <tr>
                <th style="cursor: pointer; user-select: none;">{{ theme.INFORMATION.codigo }} SKU ↕️</th>
                <th style="cursor: pointer; user-select: none;">{{ theme.INFORMATION.nombre }} Nombre ↕️</th>
                <th style="cursor: pointer; user-select: none;">{{ theme.INFORMATION.precio }} Categoría ↕️</th>
                <th style="cursor: pointer; user-select: none;">{{ theme.INFORMATION.costo }} Costo Prom. ↕️</th>
                <th style="cursor: pointer; user-select: none;">💰 Média Salida ↕️</th>
                <th style="cursor: pointer; user-select: none;">{{ theme.INFORMATION.stock }} Stock ↕️</th>
                <th style="cursor: pointer; user-select: none;">{{ theme.INFORMATION.estado }} Estado ↕️</th>
                <th>⚙️ Acciones</th>
            </tr>
            {% for p in products %}
            <tr style="{% if p.status == 'inativo' %}opacity: 0.6;{% endif %}" data-sku="{{ p.code }}" data-nombre="{{ p.name }}" data-categoria="{{ p.category }}" data-costo="{{ p.avg_cost }}" data-salida="{{ p.avg_sale }}" data-stock="{{ p.stock }}" data-estado="{{ p.status }}">
                <td><code style="background: #f0f0f0; padding: 3px 6px; border-radius: 3px;">{{ p.code }}</code></td>
                <td><b>{{ p.name }}</b></td>
                <td>{{ p.category }}</td>
                <td style="color: #FF6B9D; font-weight: bold;">{{ p.avg_cost | money }}</td>
                <td style="color: #4CAF50; font-weight: bold;">{{ p.avg_sale | money }}</td>
                <td>{{ p.stock }} {% if p.stock <= p.min_stock %} ⚠️{% endif %}</td>
                <td>
                    {% if p.status == 'ativo' %}
                        <span style="color: #4CAF50; font-weight: bold;">{{ theme.INFORMATION.activo }} Activo</span>
                    {% else %}
                        <span style="color: #f44336; font-weight: bold;">{{ theme.INFORMATION.inactivo }} Inactivo</span>
                    {% endif %}
                </td>
                <td>
                    <a href="/admin/product/edit/{{ p.code }}" class="btn" style="background: #2196F3; color: white; padding: 5px 10px; font-size: 12px; margin: 2px;">
                        {{ theme.ACTIONS.editar }} Editar
                    </a>
                    <a href="/admin/product/toggle/{{ p.code }}" class="btn" style="background: #FFC107; padding: 5px 10px; font-size: 12px; margin: 2px;">
                        {% if p.status == 'ativo' %} {{ theme.ACTIONS.desactivar }} Desactivar {% else %} {{ theme.ACTIONS.activar }} Activar {% endif %}
                    </a>
                    <a href="/admin/product/delete/{{ p.code }}" class="btn" style="background: #f44336; color: white; padding: 5px 10px; font-size: 12px; margin: 2px;" onclick="return confirm('¿Seguro de eliminar?');">
                        {{ theme.ACTIONS.eliminar }} Eliminar
                    </a>
                </td>
            </tr>
            {% endfor %}
        </table>
        <script>
            const table = document.getElementById('dataTable');
            const filterInput = document.getElementById('filterInput');
            const headers = table.querySelectorAll('th:not(:last-child)');
            let sortOrder = {};

            // Inicializar sort order
            headers.forEach((h, i) => { sortOrder[i] = 'asc'; });

            // Evento de filtro
            filterInput.addEventListener('keyup', function() {
                const filter = this.value.toLowerCase();
                const rows = table.querySelectorAll('tr:not(:first-child)');
                rows.forEach(row => {
                    const text = row.textContent.toLowerCase();
                    row.style.display = text.includes(filter) ? '' : 'none';
                });
            });

            // Evento de ordenação nas colunas
            headers.forEach((header, index) => {
                header.addEventListener('click', function() {
                    const rows = Array.from(table.querySelectorAll('tr:not(:first-child)'));
                    const isAsc = sortOrder[index] === 'asc';

                    rows.sort((a, b) => {
                        const aVal = a.children[index].textContent.trim();
                        const bVal = b.children[index].textContent.trim();
                        const aNum = parseFloat(aVal.replace(/[^\\d.-]/g, '')) || aVal;
                        const bNum = parseFloat(bVal.replace(/[^\\d.-]/g, '')) || bVal;

                        if (typeof aNum === 'number' && typeof bNum === 'number') {
                            return isAsc ? aNum - bNum : bNum - aNum;
                        }
                        return isAsc ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
                    });

                    rows.forEach(row => table.appendChild(row));
                    sortOrder[index] = isAsc ? 'desc' : 'asc';

                    // Actualizar visual del header
                    headers.forEach((h, i) => {
                        h.style.background = i === index ? '#FFB6D9' : '';
                        h.style.fontWeight = i === index ? 'bold' : '';
                    });
                });
            });
        </script>

    {% elif request.endpoint == 'edit_product' %}
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h2>{{ theme.ACTIONS.editar }} Editar Producto</h2>
            <a href="/admin/catalog" class="btn-dark btn" style="font-size: 13px;">← Volver al Catálogo</a>
        </div>
        <form method="POST" style="max-width: 600px;">
            <label>{{ theme.INFORMATION.codigo }} SKU: <strong>{{ edit_product.code }}</strong></label>

            <label style="margin-top: 15px;">{{ theme.INFORMATION.nombre }} Nombre del Producto:</label>
            <input type="text" name="name" value="{{ edit_product.name }}" required style="padding: 10px; border: 1px solid #ccc; border-radius: 5px; width: 100%; box-sizing: border-box;">

            <label style="margin-top: 15px;">{{ theme.INFORMATION.precio }} Categoría:</label>
            <input type="text" name="category" value="{{ edit_product.category }}" required style="padding: 10px; border: 1px solid #ccc; border-radius: 5px; width: 100%; box-sizing: border-box;">

            <div style="display: flex; gap: 10px; margin-top: 20px;">
                <button type="submit" class="btn btn-pink" style="flex: 1;">{{ theme.ACTIONS.guardar }} Guardar Cambios</button>
                <a href="/admin/catalog" class="btn" style="background: #ccc; flex: 1; text-align: center; padding: 10px;">{{ theme.ACTIONS.cancelar }} Cancelar</a>
            </div>
            <p style="color: #666; margin-top: 20px; font-size: 12px;">✓ Todos los textos se convertirán a MAYÚSCULA automáticamente</p>
        </form>

    {% elif request.endpoint == 'admin_new_product' %}
        <h2>{{ theme.ACTIONS.guardar }} Catálogo de Productos</h2>
        <p style="color: #666; font-size: 14px;">{{ theme.INFORMATION.codigo }} SKU se genera automáticamente | {{ theme.INFORMATION.nombre }} Nombre | {{ theme.INFORMATION.precio }} Categoría</p>
        <form method="POST" style="max-width: 600px;">
            <label>{{ theme.INFORMATION.nombre }} Nombre del Producto:</label>
            <input type="text" name="name" placeholder="Ej: Labial Mate Velvet" required style="padding: 10px; border: 1px solid #ccc; border-radius: 5px; width: 100%; box-sizing: border-box;">

            <label style="margin-top: 15px;">{{ theme.INFORMATION.precio }} Categoría:</label>
            <input type="text" name="category" placeholder="Ej: Makeup / Beauty / Accessories" required style="padding: 10px; border: 1px solid #ccc; border-radius: 5px; width: 100%; box-sizing: border-box;">

            <div style="display: flex; gap: 10px; margin-top: 20px;">
                <button type="submit" class="btn btn-pink" style="flex: 1;">{{ theme.ACTIONS.guardar }} Guardar Producto</button>
                <a href="/admin" class="btn" style="background: #ccc; flex: 1; text-align: center; padding: 10px;">{{ theme.ACTIONS.cancelar }} Cancelar</a>
            </div>
            <p style="color: #666; margin-top: 20px; font-size: 12px;">✓ Todos los textos se convertirán a MAYÚSCULA automáticamente</p>
        </form>

    {% elif request.endpoint == 'admin_purchase' %}
        <h2>📥 Registrar Entrada de Compra (Reabastecimiento)</h2>
        <form method="POST">
            <label>Fecha:</label>
            <input type="date" name="date" required>
            <label>Buscar Producto (por SKU o Nombre):</label>
            <div style="position: relative; margin-bottom: 15px;">
                <input type="text" id="productSearch" placeholder="Ej: MS-000001 o Labial Mate" style="width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 5px; box-sizing: border-box;">
                <ul id="productList" style="position: absolute; top: 100%; left: 0; right: 0; background: white; border: 1px solid #ccc; border-top: none; border-radius: 0 0 5px 5px; max-height: 300px; overflow-y: auto; list-style: none; padding: 0; margin: 0; display: none; z-index: 1000;">
                </ul>
            </div>
            <input type="hidden" name="product_code" id="productCode" required>
            <div id="productInfo" style="background: #f0f0f0; padding: 15px; border-radius: 5px; margin-bottom: 15px; display: none;">
                <strong>Producto Seleccionado:</strong> <span id="selectedProduct"></span><br>
                <strong>Stock Actual:</strong> <span id="selectedStock"></span><br>
                <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #ccc;">
                    <strong>{{ theme.OPERATIONS.historial }} Historial de Compras:</strong><br>
                    <small style="color: #666;">
                        Compras anteriores: <span id="purchaseCount" style="color: #FF6B9D; font-weight: bold;">0</span><br>
                        Costo Promedio: $ <span id="avgCost" style="color: #4CAF50; font-weight: bold;">0.00</span><br>
                        Última Compra: $ <span id="lastCost" style="color: #2196F3; font-weight: bold;">0.00</span> (<span id="lastDate">-</span>)
                    </small>
                </div>
            </div>
            <label>Cantidad Comprada:</label>
            <input type="number" name="quantity" min="1" required>
            <label>Costo Unitario de Adquisición ($):</label>
            <div style="display: grid; grid-template-columns: 1fr auto; gap: 10px; margin-bottom: 15px;">
                <input type="number" step="0.01" name="unit_cost" id="unitCost" required style="padding: 10px; border: 1px solid #ccc; border-radius: 5px; box-sizing: border-box;">
                <select id="costSelector" style="padding: 10px; border: 1px solid #ccc; border-radius: 5px; background: white; cursor: pointer; font-size: 14px; min-width: 140px;">
                    <option value="manual">{{ theme.OPERATIONS.manual }} Manual</option>
                    <option value="avg">{{ theme.OPERATIONS.promedio }} Promedio</option>
                    <option value="last">{{ theme.OPERATIONS.ultima }} Última</option>
                </select>
            </div>
            <button type="submit" class="btn btn-pink">Registrar Entrada y Actualizar Stock</button>
            <a href="/admin" class="btn" style="background: #ccc; margin-left: 10px;">Cancelar</a>
        </form>
        <script>
            const productSearch = document.getElementById('productSearch');
            const productList = document.getElementById('productList');
            const productCode = document.getElementById('productCode');
            const productInfo = document.getElementById('productInfo');
            const selectedProduct = document.getElementById('selectedProduct');
            const selectedStock = document.getElementById('selectedStock');
            const products = {{ products_json | safe }};

            productSearch.addEventListener('input', function() {
                const searchValue = this.value.toLowerCase().trim();
                productList.innerHTML = '';

                if (searchValue.length === 0) {
                    productList.style.display = 'none';
                    return;
                }

                const filtered = products.filter(p =>
                    p.code.toLowerCase().includes(searchValue) ||
                    p.name.toLowerCase().includes(searchValue)
                );

                if (filtered.length === 0) {
                    productList.style.display = 'none';
                    return;
                }

                filtered.forEach(product => {
                    const li = document.createElement('li');
                    li.style.cssText = 'padding: 10px; border-bottom: 1px solid #eee; cursor: pointer; transition: background 0.2s;';
                    li.textContent = `${product.code} - ${product.name} (Stock: ${product.stock})`;
                    li.onmouseover = () => li.style.background = '#f0f0f0';
                    li.onmouseout = () => li.style.background = 'white';
                    li.onclick = () => selectProduct(product);
                    productList.appendChild(li);
                });

                productList.style.display = 'block';
            });

            function selectProduct(product) {
                productSearch.value = `${product.code} - ${product.name}`;
                productCode.value = product.code;
                selectedProduct.textContent = `${product.code} - ${product.name}`;
                selectedStock.textContent = product.stock;

                // Mostrar histórico de compras
                document.getElementById('purchaseCount').textContent = product.purchase_count;
                document.getElementById('avgCost').textContent = product.avg_cost.toFixed(2);
                document.getElementById('lastCost').textContent = product.last_cost.toFixed(2);
                document.getElementById('lastDate').textContent = product.last_date;

                // Auto-preencher com o custo promedio
                document.getElementById('unitCost').value = product.avg_cost.toFixed(2);

                productInfo.style.display = 'block';
                productList.style.display = 'none';
            }

            // Selector de custo
            document.getElementById('costSelector').addEventListener('change', function() {
                const selectedProduct = products.find(p => p.code === productCode.value);
                if (!selectedProduct) return;

                const unitCostInput = document.getElementById('unitCost');
                if (this.value === 'avg') {
                    unitCostInput.value = selectedProduct.avg_cost.toFixed(2);
                } else if (this.value === 'last') {
                    unitCostInput.value = selectedProduct.last_cost.toFixed(2);
                }
            });

            document.addEventListener('click', function(e) {
                if (e.target !== productSearch && e.target !== productList) {
                    productList.style.display = 'none';
                }
            });
        </script>

    {% elif request.endpoint == 'admin_sale' %}
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <h2 style="margin: 0;">🛍️ Punto de Venta (POS) - Muse Studio</h2>
            <a href="/admin" class="btn-dark btn" style="font-size: 13px;">← Volver al Dashboard</a>
        </div>

        <div style="display: block; margin-bottom: 220px;">
            <h3>📦 Catálogo de Productos</h3>
            <input type="text" id="searchInput" placeholder="🔍 Buscar SKU o nombre..." style="padding: 12px; border: 2px solid #ccc; border-radius: 5px; width: 100%; margin-bottom: 15px; box-sizing: border-box; font-size: 16px;">

            <div id="productsContainer" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 10px;">
                <!-- Los productos se cargan aquí con JavaScript -->
            </div>
        </div>

        <!-- CARRITO FLOTANTE PARA MOBILE -->
        <div style="position: fixed; bottom: 0; left: 0; right: 0; background: #fff5f8; border-top: 3px solid var(--pink); box-shadow: 0 -2px 10px rgba(0,0,0,0.15); z-index: 1000;">
            <div style="padding: 12px; max-width: 1000px; margin: 0 auto;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <div>
                        <h4 style="margin: 0; color: var(--pink); font-size: 16px; font-weight: bold;">🛒 Carrito</h4>
                        <small style="color: #666; font-size: 13px;">Items: <span id="cartCount" style="font-weight: bold; color: var(--pink);">0</span></small>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 12px; color: #999; margin-bottom: 2px;">Total</div>
                        <div id="cartTotal" style="font-size: 20px; font-weight: bold; color: #4CAF50;">$ 0.00</div>
                    </div>
                </div>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                    <button type="button" onclick="toggleCartModal()" class="btn" style="background: #FFC107; color: black; padding: 10px; font-size: 14px; font-weight: bold; border: none; border-radius: 5px; cursor: pointer;">
                        📋 Ver Carrito
                    </button>
                    <form method="POST" id="checkoutForm" style="margin: 0;">
                        <input type="hidden" name="date" value="{{ today }}">
                        <div id="formItems"></div>
                        <button type="submit" class="btn btn-pink" style="width: 100%; padding: 10px; font-size: 14px; font-weight: bold; border: none; border-radius: 5px; cursor: pointer;">
                            💳 Procesar
                        </button>
                    </form>
                </div>
            </div>
        </div>

        <!-- MODAL CARRITO DETALLADO -->
        <div id="cartModal" style="display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.6); z-index: 2000; padding: 0;">
            <div style="background: white; margin: 0; border-radius: 15px 15px 0 0; position: absolute; bottom: 0; left: 0; right: 0; max-height: 85vh; overflow-y: auto; box-shadow: 0 -5px 20px rgba(0,0,0,0.3);">
                <div style="background: var(--pink); color: white; padding: 15px; display: flex; justify-content: space-between; align-items: center; border-radius: 15px 15px 0 0; position: sticky; top: 0;">
                    <h3 style="margin: 0; font-size: 18px;">🛒 Detalles del Carrito</h3>
                    <button type="button" onclick="toggleCartModal()" style="background: transparent; border: none; color: white; font-size: 28px; cursor: pointer; padding: 0; width: 30px; height: 30px;">✕</button>
                </div>

                <div id="cartItemsModal" style="padding: 15px; min-height: 100px;">
                    <p style="text-align: center; color: #999; margin: 40px 0; font-size: 16px;">Carrito vacío</p>
                </div>

                <div style="background: #f0f0f0; padding: 15px; border-top: 1px solid #e0e0e0; position: sticky; bottom: 0;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 15px; font-size: 18px; font-weight: bold;">
                        <span>Total:</span>
                        <span id="cartTotalModal" style="color: #4CAF50;">$ 0.00</span>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                        <button type="button" onclick="toggleCartModal()" class="btn" style="background: #FFC107; color: black; padding: 12px; font-size: 14px; font-weight: bold; border: none; border-radius: 5px; cursor: pointer;">
                            ← Seguir Comprando
                        </button>
                        <button type="button" onclick="clearCart()" class="btn" style="background: #f44336; color: white; padding: 12px; font-size: 14px; font-weight: bold; border: none; border-radius: 5px; cursor: pointer;">
                            🗑️ Limpiar Todo
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <script>
            const productsData = {{ products_data | safe }};
            let cart = [];

            function toggleCartModal() {
                const modal = document.getElementById('cartModal');
                modal.style.display = modal.style.display === 'none' ? 'block' : 'none';
                updateCartModal();
            }

            function renderProducts() {
                const container = document.getElementById('productsContainer');
                const searchValue = document.getElementById('searchInput').value.toLowerCase();
                container.innerHTML = '';

                productsData.forEach(product => {
                    if (product.code.toLowerCase().includes(searchValue) ||
                        product.name.toLowerCase().includes(searchValue)) {

                        const isInactive = product.status !== 'ativo';
                        const cardHTML = `
                            <div style="background: white; border: 2px solid #ddd; border-radius: 8px; padding: 12px; cursor: pointer; transition: all 0.3s; text-align: center; ${isInactive ? 'opacity: 0.5; pointer-events: none;' : ''}">
                                <div style="font-weight: bold; color: #333; margin-bottom: 8px; font-size: 13px;">${product.code}</div>
                                <div style="font-size: 12px; color: #666; margin-bottom: 8px; line-height: 1.3; min-height: 32px; display: flex; align-items: center; justify-content: center;">${product.name}</div>
                                <div style="font-size: 11px; color: #999; margin-bottom: 8px; background: #f0f0f0; padding: 4px; border-radius: 3px;">Stock: <strong>${product.stock}</strong></div>
                                <div style="color: var(--pink); font-weight: bold; margin-bottom: 10px; font-size: 15px;">$ ${product.avg_price.toFixed(2)}</div>
                                ${product.stock > 0 ? `
                                    <button type="button" onclick="addToCart('${product.code}', '${product.name}', ${product.avg_price}, ${product.stock})" class="btn" style="width: 100%; padding: 8px; font-size: 13px; background: var(--pink); color: white; border: none; border-radius: 5px; font-weight: bold; cursor: pointer;">
                                        ➕ Agregar
                                    </button>
                                ` : `
                                    <div style="text-align: center; padding: 8px; color: #f44336; font-size: 12px; font-weight: bold; background: #ffebee; border-radius: 5px;">
                                        ❌ Sin Stock
                                    </div>
                                `}
                            </div>
                        `;
                        container.innerHTML += cardHTML;
                    }
                });
            }

            function addToCart(code, name, price, availableStock) {
                const existing = cart.find(item => item.code === code);
                if (existing) {
                    if (existing.quantity < availableStock) {
                        existing.quantity++;
                        updateCart();
                    } else {
                        alert('❌ Stock insuficiente');
                    }
                } else {
                    cart.push({ code, name, price, quantity: 1, stock: availableStock });
                    updateCart();
                }
            }

            function removeFromCart(code) {
                cart = cart.filter(item => item.code !== code);
                updateCart();
            }

            function updateQuantity(code, newQty) {
                const item = cart.find(i => i.code === code);
                if (item) {
                    if (newQty <= 0) {
                        removeFromCart(code);
                    } else if (newQty <= item.stock) {
                        item.quantity = newQty;
                        updateCart();
                    }
                }
            }

            function updateCart() {
                const formItemsDiv = document.getElementById('formItems');

                if (cart.length > 0) {
                    let formHTML = '';
                    cart.forEach((item, index) => {
                        formHTML += `
                            <input type="hidden" name="item_${index}_code" value="${item.code}">
                            <input type="hidden" name="item_${index}_quantity" value="${item.quantity}">
                            <input type="hidden" name="item_${index}_price" value="${item.price}">
                        `;
                    });
                    formItemsDiv.innerHTML = formHTML;
                } else {
                    formItemsDiv.innerHTML = '';
                }

                updateCartDisplay();
                updateCartModal();
            }

            function updateCartDisplay() {
                let total = 0;
                let itemCount = 0;
                cart.forEach(item => {
                    total += item.price * item.quantity;
                    itemCount += item.quantity;
                });

                document.getElementById('cartTotal').textContent = '$ ' + total.toFixed(2);
                document.getElementById('cartCount').textContent = itemCount;
            }

            function updateCartModal() {
                const cartItemsDiv = document.getElementById('cartItemsModal');
                const cartTotalModal = document.getElementById('cartTotalModal');

                if (cart.length === 0) {
                    cartItemsDiv.innerHTML = '<p style="text-align: center; color: #999; margin: 40px 0; font-size: 16px;">Carrito vacío</p>';
                    cartTotalModal.textContent = '$ 0.00';
                } else {
                    let html = '';
                    let total = 0;

                    cart.forEach(item => {
                        const subtotal = item.price * item.quantity;
                        total += subtotal;

                        html += `
                            <div style="background: #f9f9f9; padding: 12px; margin-bottom: 10px; border-radius: 8px; border-left: 4px solid var(--pink);">
                                <div style="font-weight: bold; font-size: 14px; margin-bottom: 8px; color: #333;">${item.code}</div>
                                <div style="font-size: 13px; color: #666; margin-bottom: 10px;">${item.name}</div>
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                                    <span style="font-size: 13px; color: #666;">$ ${item.price.toFixed(2)} × <input type="number" value="${item.quantity}" min="1" max="${item.stock}" onchange="updateQuantity('${item.code}', parseInt(this.value))" style="width: 40px; padding: 4px; text-align: center; border: 1px solid #ccc; border-radius: 3px; font-size: 13px;"></span>
                                </div>
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <strong style="color: #4CAF50; font-size: 14px;">$ ${subtotal.toFixed(2)}</strong>
                                    <button type="button" onclick="removeFromCart('${item.code}')" class="btn" style="padding: 5px 10px; font-size: 12px; background: #f44336; color: white; border: none; border-radius: 4px; cursor: pointer;">
                                        ✕ Quitar
                                    </button>
                                </div>
                            </div>
                        `;
                    });

                    cartItemsDiv.innerHTML = html;
                    cartTotalModal.textContent = '$ ' + total.toFixed(2);
                }
            }

            function clearCart() {
                if (confirm('¿Limpiar el carrito completamente?')) {
                    cart = [];
                    updateCart();
                }
            }

            // Evento de búsqueda
            document.getElementById('searchInput').addEventListener('input', renderProducts);

            // Cargar productos al abrir la página
            renderProducts();
        </script>

    {% elif request.endpoint == 'sales_history' %}
        <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"></script>

        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 10px;">
            <h2 style="margin: 0;">📊 Histórico de Ventas - Análisis de Ganancias</h2>
            <div style="display: flex; gap: 10px;">
                <button onclick="exportToExcel()" class="btn" style="background: #4CAF50; color: white; padding: 10px 15px; font-size: 13px;">
                    📥 Exportar a Excel
                </button>
                <a href="/admin" class="btn-dark btn" style="font-size: 13px;">← Volver</a>
            </div>
        </div>

        <!-- FILTROS -->
        <div style="background: #f9f9f9; padding: 15px; border-radius: 8px; margin-bottom: 20px; display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px;">
            <div>
                <label style="font-size: 12px; color: #666;">Desde:</label>
                <input type="date" id="dateFrom" style="width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box;">
            </div>
            <div>
                <label style="font-size: 12px; color: #666;">Hasta:</label>
                <input type="date" id="dateTo" style="width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box;">
            </div>
            <div style="display: flex; align-items: flex-end; gap: 8px;">
                <button onclick="applyDateFilter()" class="btn btn-pink" style="padding: 8px 15px; font-size: 12px; flex: 1;">Filtrar</button>
                <button onclick="resetDateFilter()" class="btn" style="padding: 8px 15px; font-size: 12px; background: #ccc; flex: 1;">Limpiar</button>
            </div>
        </div>

        <!-- ESTADÍSTICAS GENERALES -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 30px;">
            <div style="background: #e8f5e9; border-left: 4px solid #4CAF50; padding: 20px; border-radius: 8px;">
                <h4 style="margin: 0; color: #666; font-size: 13px;">💰 Ingresos Totales</h4>
                <p style="margin: 10px 0 0 0; font-size: 24px; font-weight: bold; color: #4CAF50;">{{ total_revenue | money }}</p>
            </div>
            <div style="background: #ffebee; border-left: 4px solid #f44336; padding: 20px; border-radius: 8px;">
                <h4 style="margin: 0; color: #666; font-size: 13px;">📦 Costo Total de Productos</h4>
                <p style="margin: 10px 0 0 0; font-size: 24px; font-weight: bold; color: #f44336;">{{ total_cost_all | money }}</p>
            </div>
            <div style="background: {% if total_profit >= 0 %}#e3f2fd{% else %}#ffebee{% endif %}; border-left: 4px solid {% if total_profit >= 0 %}#2196F3{% else %}#f44336{% endif %}; padding: 20px; border-radius: 8px;">
                <h4 style="margin: 0; color: #666; font-size: 13px;">💎 Ganancia Neta</h4>
                <p style="margin: 10px 0 0 0; font-size: 24px; font-weight: bold; color: {% if total_profit >= 0 %}#2196F3{% else %}#f44336{% endif %};">{{ total_profit | money }}</p>
            </div>
            <div style="background: #fff3e0; border-left: 4px solid #FF9800; padding: 20px; border-radius: 8px;">
                <h4 style="margin: 0; color: #666; font-size: 13px;">📈 Margen de Ganancia Promedio</h4>
                <p style="margin: 10px 0 0 0; font-size: 24px; font-weight: bold; color: #FF9800;">{{ "%.1f"|format(avg_profit_margin) }}%</p>
            </div>
        </div>

        <!-- GRÁFICOS DE TENDENCIAS -->
        <h3 style="margin-top: 40px;">📈 Gráficos de Tendencias</h3>

        <!-- BOTONES DE VISTA -->
        <div style="margin-bottom: 20px; display: flex; gap: 8px; flex-wrap: wrap; justify-content: center;">
            <button onclick="changeChartView('daily')" class="btn btn-pink" id="btnDaily" style="padding: 10px 15px; font-size: 13px; font-weight: bold;">📅 Diario</button>
            <button onclick="changeChartView('weekly')" class="btn" style="padding: 10px 15px; font-size: 13px; background: #2196F3; color: white;">📊 Semanal</button>
            <button onclick="changeChartView('monthly')" class="btn" style="padding: 10px 15px; font-size: 13px; background: #FF9800; color: white;">📈 Mensual</button>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 40px;">
            <div style="background: white; padding: 20px; border-radius: 8px; border: 1px solid #e0e0e0;">
                <h4 style="margin-top: 0;">💰 Ingresos vs Costos</h4>
                <canvas id="trendChart" height="80"></canvas>
            </div>
            <div style="background: white; padding: 20px; border-radius: 8px; border: 1px solid #e0e0e0;">
                <h4 style="margin-top: 0;">💎 Ganancia</h4>
                <canvas id="profitChart" height="80"></canvas>
            </div>
        </div>

        <!-- ANÁLISIS POR PRODUCTO -->
        <h3>🏆 Top Productos por Ganancia</h3>
        <div style="overflow-x: auto; margin-bottom: 40px;">
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="background-color: #fff5f8;">
                    <th style="padding: 12px; text-align: left; border: 1px solid #e0e0e0;">SKU</th>
                    <th style="padding: 12px; text-align: left; border: 1px solid #e0e0e0;">Producto</th>
                    <th style="padding: 12px; text-align: center; border: 1px solid #e0e0e0;">📦 Cantidad</th>
                    <th style="padding: 12px; text-align: center; border: 1px solid #e0e0e0;">🛒 Ventas</th>
                    <th style="padding: 12px; text-align: right; border: 1px solid #e0e0e0;">💰 Ingresos</th>
                    <th style="padding: 12px; text-align: right; border: 1px solid #e0e0e0;">📉 Costo</th>
                    <th style="padding: 12px; text-align: right; border: 1px solid #e0e0e0;">💎 Ganancia</th>
                    <th style="padding: 12px; text-align: center; border: 1px solid #e0e0e0;">📊 Margen %</th>
                </tr>
                {% for prod in product_list %}
                <tr style="border: 1px solid #e0e0e0;">
                    <td style="padding: 12px; border: 1px solid #e0e0e0; font-weight: bold; color: var(--pink);">{{ prod.code }}</td>
                    <td style="padding: 12px; border: 1px solid #e0e0e0;">{{ prod.name }}</td>
                    <td style="padding: 12px; border: 1px solid #e0e0e0; text-align: center;">{{ prod.quantity_sold }}</td>
                    <td style="padding: 12px; border: 1px solid #e0e0e0; text-align: center;">{{ prod.sales_count }}</td>
                    <td style="padding: 12px; border: 1px solid #e0e0e0; text-align: right; color: #4CAF50; font-weight: bold;">{{ prod.total_revenue | money }}</td>
                    <td style="padding: 12px; border: 1px solid #e0e0e0; text-align: right; color: #f44336;">{{ prod.total_cost | money }}</td>
                    <td style="padding: 12px; border: 1px solid #e0e0e0; text-align: right; font-weight: bold; color: {% if prod.profit >= 0 %}#2196F3{% else %}#f44336{% endif %};">{{ prod.profit | money }}</td>
                    <td style="padding: 12px; border: 1px solid #e0e0e0; text-align: center; background: {% if prod.profit_margin >= 30 %}#e8f5e9{% elif prod.profit_margin >= 15 %}#fff3e0{% else %}#ffebee{% endif %};">{{ "%.1f"|format(prod.profit_margin) }}%</td>
                </tr>
                {% else %}
                <tr>
                    <td colspan="8" style="padding: 20px; text-align: center; color: #999;">No hay productos vendidos</td>
                </tr>
                {% endfor %}
            </table>
        </div>

        <!-- TABLA DE HISTÓRICO -->
        <h3>📋 Detalle de Todas las Ventas</h3>
        <div style="margin-bottom: 15px;">
            <input type="text" id="filterSales" placeholder="🔍 Buscar por NF o fecha..." style="padding: 10px; border: 1px solid #ccc; border-radius: 5px; width: 100%; max-width: 400px; box-sizing: border-box;">
        </div>

        <div style="overflow-x: auto;">
            <table id="salesTable" style="width: 100%; border-collapse: collapse;">
                <tr style="background-color: #fff5f8; cursor: pointer; user-select: none;">
                    <th style="cursor: pointer; padding: 12px; text-align: left; border: 1px solid #e0e0e0;">📅 Fecha ↕️</th>
                    <th style="cursor: pointer; padding: 12px; text-align: left; border: 1px solid #e0e0e0;">🧾 NF/Invoice ↕️</th>
                    <th style="cursor: pointer; padding: 12px; text-align: center; border: 1px solid #e0e0e0;">📦 Items ↕️</th>
                    <th style="cursor: pointer; padding: 12px; text-align: right; border: 1px solid #e0e0e0;">💰 Ingresos ↕️</th>
                    <th style="cursor: pointer; padding: 12px; text-align: right; border: 1px solid #e0e0e0;">📉 Costo ↕️</th>
                    <th style="cursor: pointer; padding: 12px; text-align: right; border: 1px solid #e0e0e0;">💎 Ganancia ↕️</th>
                    <th style="cursor: pointer; padding: 12px; text-align: center; border: 1px solid #e0e0e0;">📊 Margen ↕️</th>
                </tr>
                {% for inv in invoice_details %}
                <tr data-date="{{ inv.date }}" data-invoice="{{ inv.invoice_number }}" data-ganancia="{{ inv.profit }}" style="border: 1px solid #e0e0e0;">
                    <td style="padding: 12px; border: 1px solid #e0e0e0;">{{ inv.date }}</td>
                    <td style="padding: 12px; border: 1px solid #e0e0e0; font-weight: bold; color: var(--pink);">{{ inv.invoice_number }}</td>
                    <td style="padding: 12px; border: 1px solid #e0e0e0; text-align: center;">{{ inv.item_count }}</td>
                    <td style="padding: 12px; border: 1px solid #e0e0e0; text-align: right; color: #4CAF50; font-weight: bold;">{{ inv.total_revenue | money }}</td>
                    <td style="padding: 12px; border: 1px solid #e0e0e0; text-align: right; color: #f44336;">{{ inv.total_cost | money }}</td>
                    <td style="padding: 12px; border: 1px solid #e0e0e0; text-align: right; font-weight: bold; color: {% if inv.profit >= 0 %}#2196F3{% else %}#f44336{% endif %};">{{ inv.profit | money }}</td>
                    <td style="padding: 12px; border: 1px solid #e0e0e0; text-align: center; background: {% if inv.profit_margin >= 30 %}#e8f5e9{% elif inv.profit_margin >= 15 %}#fff3e0{% else %}#ffebee{% endif %};">{{ "%.1f"|format(inv.profit_margin) }}%</td>
                </tr>
                {% else %}
                <tr>
                    <td colspan="7" style="padding: 20px; text-align: center; color: #999;">No hay ventas registradas aún</td>
                </tr>
                {% endfor %}
            </table>
        </div>

        <script>
            // Datos para gráficos por período
            const chartDataDaily = {{ chart_data | safe }};
            const chartDataWeekly = {{ chart_data_weekly | safe }};
            const chartDataMonthly = {{ chart_data_monthly | safe }};

            // Guardar datos originales
            const originalChartDataDaily = JSON.parse(JSON.stringify(chartDataDaily));
            const originalChartDataWeekly = JSON.parse(JSON.stringify(chartDataWeekly));
            const originalChartDataMonthly = JSON.parse(JSON.stringify(chartDataMonthly));

            let currentChartView = 'daily';
            let trendChartInstance = null;
            let profitChartInstance = null;
            let allRows = [];
            let dateFilterActive = false;
            let filterFromDate = null;
            let filterToDate = null;

            // Cambiar vista de gráficos
            function changeChartView(view) {
                currentChartView = view;

                // Actualizar botones activos
                document.querySelectorAll('button[onclick*="changeChartView"]').forEach(btn => {
                    btn.style.opacity = '0.7';
                    btn.style.background = '';
                });
                event.target.style.opacity = '1';
                event.target.style.background = 'var(--pink)';

                // Actualizar gráficos
                updateCharts();
            }

            // Filtrar datos por rango de fechas
            function filterDataByDateRange(data, fromDate, toDate) {
                if (!dateFilterActive) return data;

                return data.filter(d => {
                    const dataDate = d.date;
                    return dataDate >= fromDate && dataDate <= toDate;
                });
            }

            // Actualizar gráficos basado en vista actual
            function updateCharts() {
                let data = JSON.parse(JSON.stringify(originalChartDataDaily));
                let label = 'Diario';

                if (currentChartView === 'weekly') {
                    data = JSON.parse(JSON.stringify(originalChartDataWeekly));
                    label = 'Semanal';
                } else if (currentChartView === 'monthly') {
                    data = JSON.parse(JSON.stringify(originalChartDataMonthly));
                    label = 'Mensual';
                }

                // Aplicar filtro de fechas si está activo
                if (dateFilterActive && filterFromDate && filterToDate) {
                    data = filterDataByDateRange(data, filterFromDate, filterToDate);
                }

                const dates = data.map(d => d.date);
                const revenues = data.map(d => d.revenue);
                const costs = data.map(d => d.cost);
                const profits = data.map(d => d.profit);

                // Destruir gráficos anteriores
                if (trendChartInstance) trendChartInstance.destroy();
                if (profitChartInstance) profitChartInstance.destroy();

                // Gráfico de Ingresos vs Costos
                trendChartInstance = new Chart(document.getElementById('trendChart'), {
                    type: 'line',
                    data: {
                        labels: dates,
                        datasets: [
                            {
                                label: 'Ingresos',
                                data: revenues,
                                borderColor: '#4CAF50',
                                backgroundColor: 'rgba(76, 175, 80, 0.1)',
                                tension: 0.4,
                                fill: true,
                                borderWidth: 2
                            },
                            {
                                label: 'Costos',
                                data: costs,
                                borderColor: '#f44336',
                                backgroundColor: 'rgba(244, 67, 54, 0.1)',
                                tension: 0.4,
                                fill: true,
                                borderWidth: 2
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: { position: 'top' },
                            title: { display: true, text: `Vista: ${label}` }
                        },
                        scales: { y: { beginAtZero: true } }
                    }
                });

                // Gráfico de Ganancia
                profitChartInstance = new Chart(document.getElementById('profitChart'), {
                    type: 'bar',
                    data: {
                        labels: dates,
                        datasets: [{
                            label: `Ganancia ${label}`,
                            data: profits,
                            backgroundColor: profits.map(p => p >= 0 ? '#2196F3' : '#f44336'),
                            borderRadius: 5
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: { display: false },
                            title: { display: true, text: `Ganancia ${label}` }
                        },
                        scales: { y: { beginAtZero: true } }
                    }
                });
            }

            // Inicializar gráficos
            function initCharts() {
                updateCharts();
            }

            // Exportar a Excel
            function exportToExcel() {
                const table = document.getElementById('salesTable');
                const wb = XLSX.utils.table_to_book(table);
                XLSX.writeFile(wb, `Ventas_${new Date().toISOString().split('T')[0]}.xlsx`);
            }

            // Filtro por fechas
            function applyDateFilter() {
                const dateFrom = document.getElementById('dateFrom').value;
                const dateTo = document.getElementById('dateTo').value;

                if (!dateFrom || !dateTo) {
                    alert('Por favor selecciona ambas fechas');
                    return;
                }

                const [yFrom, mFrom, dFrom] = dateFrom.split('-');
                const [yTo, mTo, dTo] = dateTo.split('-');
                const filterFrom = `${dFrom}/${mFrom}/${yFrom}`;
                const filterTo = `${dTo}/${mTo}/${yTo}`;

                // Aplicar filtro a tabla
                allRows.forEach(row => {
                    const rowDate = row.dataset.date;
                    if (rowDate >= filterFrom && rowDate <= filterTo) {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
                    }
                });

                // Aplicar filtro a gráficos
                dateFilterActive = true;
                filterFromDate = filterFrom;
                filterToDate = filterTo;
                updateCharts();
            }

            function resetDateFilter() {
                document.getElementById('dateFrom').value = '';
                document.getElementById('dateTo').value = '';
                allRows.forEach(row => row.style.display = '');

                // Resetear gráficos
                dateFilterActive = false;
                filterFromDate = null;
                filterToDate = null;
                updateCharts();
            }

            // Ordenamiento de tabla
            const headers = document.querySelectorAll('th');
            const table = document.getElementById('salesTable');
            allRows = Array.from(table.querySelectorAll('tbody tr, tr[data-date]'));

            headers.forEach((header, index) => {
                header.addEventListener('click', () => {
                    const isAsc = header.classList.contains('asc');
                    headers.forEach(h => h.classList.remove('asc', 'desc'));

                    if (isAsc) {
                        header.classList.add('desc');
                    } else {
                        header.classList.add('asc');
                    }

                    allRows.sort((a, b) => {
                        const aVal = a.children[index].textContent.trim();
                        const bVal = b.children[index].textContent.trim();

                        const aNum = parseFloat(aVal.replace(/[^\d.-]/g, '')) || aVal;
                        const bNum = parseFloat(bVal.replace(/[^\d.-]/g, '')) || bVal;

                        if (isAsc) {
                            return bNum < aNum ? -1 : 1;
                        } else {
                            return aNum < bNum ? -1 : 1;
                        }
                    });

                    allRows.forEach(row => table.appendChild(row));
                });
            });

            // Filtro de búsqueda rápida
            document.getElementById('filterSales').addEventListener('input', (e) => {
                const searchValue = e.target.value.toLowerCase();
                allRows.forEach(row => {
                    const date = row.dataset.date || row.children[0].textContent;
                    const invoice = row.dataset.invoice || row.children[1].textContent;

                    if (date.includes(searchValue) || invoice.toLowerCase().includes(searchValue)) {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
                    }
                });
            });

            // Inicializar todo al cargar
            window.addEventListener('load', initCharts);
        </script>

    {% endif %}
</div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            session['user'] = user.username
            session['role'] = user.role
            return redirect(url_for('dev_panel' if user.role == 'dev' else 'admin_dashboard'))
        flash('Credenciales inválidas.')
    return render_template_string(TEMPLATE, theme=Theme)

@app.route('/dev')
def dev_panel():
    if session.get('role') != 'dev': return redirect(url_for('login'))
    return render_template_string(TEMPLATE, users=User.query.all(), theme=Theme)

@app.route('/dev/create_user', methods=['POST'])
def create_user():
    if session.get('role') != 'dev': return redirect(url_for('login'))
    new_username = request.form['new_user']
    new_password = request.form['new_password']
    role = request.form['role']
    
    if User.query.filter_by(username=new_username).first():
        flash('El nombre de usuario ya existe.')
        return redirect(url_for('dev_panel'))
    
    hashed_pw = generate_password_hash(new_password, method='pbkdf2:sha256')
    db.session.add(User(username=new_username, password=hashed_pw, role=role))
    db.session.commit()
    flash(f'Usuario "{new_username}" creado con éxito.')
    return redirect(url_for('dev_panel'))

@app.route('/admin')
def admin_dashboard():
    if session.get('role') != 'admin': return redirect(url_for('login'))
    
    products = Product.query.all()
    total_products = len(products)
    
    product_stocks = {}
    for p in products:
        total_purchases = db.session.query(db.func.sum(Purchase.quantity)).filter_by(product_code=p.code).scalar() or 0
        total_sales = db.session.query(db.func.sum(Sale.quantity)).filter_by(product_code=p.code).scalar() or 0
        product_stocks[p.code] = total_purchases - total_sales

    low_stock_products = []
    total_inventory_value = 0
    for p in products:
        current_stock = product_stocks.get(p.code, 0)
        p.stock = current_stock
        total_inventory_value += current_stock * p.cost_price
        if current_stock <= p.min_stock:
            low_stock_products.append(p)

    return render_template_string(TEMPLATE,
                                  total_products=total_products,
                                  low_stock_count=len(low_stock_products),
                                  total_inventory_value=total_inventory_value,
                                  low_stock_products=low_stock_products,
                                  theme=Theme)

@app.route('/admin/sales-history')
def sales_history():
    if session.get('role') != 'admin': return redirect(url_for('login'))
    from datetime import datetime
    import json

    # Obtener todas las facturas/ventas
    invoices = Invoice.query.all()
    invoice_details = []
    product_analysis = {}

    for invoice in invoices:
        items = InvoiceItem.query.filter_by(invoice_number=invoice.invoice_number).all()
        total_cost = 0

        for item in items:
            purchases = Purchase.query.filter_by(product_code=item.product_code).all()
            if purchases:
                total_cost_item = sum(p.quantity * p.unit_cost for p in purchases)
                total_qty = sum(p.quantity for p in purchases)
                unit_cost = total_cost_item / total_qty if total_qty > 0 else 0
                total_cost += unit_cost * item.quantity

            # Análisis por producto
            if item.product_code not in product_analysis:
                product = Product.query.filter_by(code=item.product_code).first()
                product_analysis[item.product_code] = {
                    'code': item.product_code,
                    'name': product.name if product else 'Producto Desconocido',
                    'quantity_sold': 0,
                    'total_revenue': 0,
                    'total_cost': 0,
                    'sales_count': 0
                }

            product_analysis[item.product_code]['quantity_sold'] += item.quantity
            product_analysis[item.product_code]['total_revenue'] += item.subtotal
            product_analysis[item.product_code]['sales_count'] += 1

            purchases = Purchase.query.filter_by(product_code=item.product_code).all()
            if purchases:
                total_cost_product = sum(p.quantity * p.unit_cost for p in purchases)
                total_qty = sum(p.quantity for p in purchases)
                unit_cost = total_cost_product / total_qty if total_qty > 0 else 0
                product_analysis[item.product_code]['total_cost'] += unit_cost * item.quantity

        profit = invoice.total_amount - total_cost
        profit_margin = (profit / invoice.total_amount * 100) if invoice.total_amount > 0 else 0

        invoice_details.append({
            'invoice_number': invoice.invoice_number,
            'date': invoice.date,
            'total_revenue': invoice.total_amount,
            'total_cost': round(total_cost, 2),
            'profit': round(profit, 2),
            'profit_margin': round(profit_margin, 2),
            'item_count': len(items)
        })

    # Calcular ganancias por producto
    for code in product_analysis:
        prod = product_analysis[code]
        prod['profit'] = prod['total_revenue'] - prod['total_cost']
        prod['profit_margin'] = (prod['profit'] / prod['total_revenue'] * 100) if prod['total_revenue'] > 0 else 0
        prod['avg_price'] = prod['total_revenue'] / prod['quantity_sold'] if prod['quantity_sold'] > 0 else 0

    # Ordenar productos por ganancia
    product_list = sorted(product_analysis.values(), key=lambda x: x['profit'], reverse=True)

    # Estadísticas generales
    total_revenue = sum(inv['total_revenue'] for inv in invoice_details)
    total_cost_all = sum(inv['total_cost'] for inv in invoice_details)
    total_profit = total_revenue - total_cost_all
    avg_profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0

    # Datos para gráficos - VISTA DIARIA (default)
    dates = sorted(set(inv['date'] for inv in invoice_details))
    chart_data_daily = []
    for date in dates:
        day_revenue = sum(inv['total_revenue'] for inv in invoice_details if inv['date'] == date)
        day_cost = sum(inv['total_cost'] for inv in invoice_details if inv['date'] == date)
        day_profit = day_revenue - day_cost
        chart_data_daily.append({'date': date, 'revenue': day_revenue, 'cost': day_cost, 'profit': day_profit})

    # VISTA SEMANAL
    chart_data_weekly = {}
    for inv in invoice_details:
        # Convertir fecha DD/MM/YYYY a datetime
        day, month, year = map(int, inv['date'].split('/'))
        date_obj = datetime(year, month, day)
        week_key = f"Sem {date_obj.strftime('%U/%Y')}"

        if week_key not in chart_data_weekly:
            chart_data_weekly[week_key] = {'revenue': 0, 'cost': 0}

        chart_data_weekly[week_key]['revenue'] += inv['total_revenue']
        chart_data_weekly[week_key]['cost'] += inv['total_cost']

    chart_data_weekly_list = []
    for week, data in sorted(chart_data_weekly.items()):
        chart_data_weekly_list.append({
            'date': week,
            'revenue': data['revenue'],
            'cost': data['cost'],
            'profit': data['revenue'] - data['cost']
        })

    # VISTA MENSUAL
    chart_data_monthly = {}
    for inv in invoice_details:
        day, month, year = map(int, inv['date'].split('/'))
        month_key = f"{month:02d}/{year}"

        if month_key not in chart_data_monthly:
            chart_data_monthly[month_key] = {'revenue': 0, 'cost': 0}

        chart_data_monthly[month_key]['revenue'] += inv['total_revenue']
        chart_data_monthly[month_key]['cost'] += inv['total_cost']

    chart_data_monthly_list = []
    for month, data in sorted(chart_data_monthly.items()):
        chart_data_monthly_list.append({
            'date': month,
            'revenue': data['revenue'],
            'cost': data['cost'],
            'profit': data['revenue'] - data['cost']
        })

    # Ordenar por fecha descendente para tabla
    invoice_details = sorted(invoice_details, key=lambda x: x['date'], reverse=True)

    chart_json = json.dumps(chart_data_daily)
    chart_json_weekly = json.dumps(chart_data_weekly_list)
    chart_json_monthly = json.dumps(chart_data_monthly_list)

    return render_template_string(TEMPLATE,
                                 invoice_details=invoice_details,
                                 product_list=product_list,
                                 total_revenue=total_revenue,
                                 total_cost_all=total_cost_all,
                                 total_profit=total_profit,
                                 avg_profit_margin=avg_profit_margin,
                                 chart_data=chart_json,
                                 chart_data_weekly=chart_json_weekly,
                                 chart_data_monthly=chart_json_monthly,
                                 theme=Theme)

@app.route('/admin/cash-flow')
def cash_flow():
    if session.get('role') != 'admin': return redirect(url_for('login'))
    from datetime import datetime, timedelta

    today = datetime.strptime('2026-09-27', '%Y-%m-%d')
    date_30_days_ago = (today - timedelta(days=30)).strftime('%d/%m/%Y')

    purchases = Purchase.query.filter(Purchase.date >= date_30_days_ago).all()
    total_purchases = sum(p.quantity * p.unit_cost for p in purchases)

    sales = Sale.query.filter(Sale.date >= date_30_days_ago).all()
    total_sales = sum(s.quantity * s.unit_price for s in sales)

    balance = total_sales - total_purchases

    cash_by_date = {}
    for p in purchases:
        if p.date not in cash_by_date:
            cash_by_date[p.date] = {'compras': 0, 'ventas': 0}
        cash_by_date[p.date]['compras'] += p.quantity * p.unit_cost

    for s in sales:
        if s.date not in cash_by_date:
            cash_by_date[s.date] = {'compras': 0, 'ventas': 0}
        cash_by_date[s.date]['ventas'] += s.quantity * s.unit_price

    cash_flow_data = sorted([(date, data) for date, data in cash_by_date.items()])

    return render_template_string(TEMPLATE,
                                 total_purchases=total_purchases,
                                 total_sales=total_sales,
                                 balance=balance,
                                 cash_flow_data=cash_flow_data,
                                 theme=Theme)

@app.route('/admin/price-guide')
def price_guide():
    if session.get('role') != 'admin': return redirect(url_for('login'))
    from datetime import datetime, timedelta

    products = Product.query.all()
    product_data = []

    today = datetime.strptime('2026-09-27', '%Y-%m-%d')  # Data atual
    date_15_days_ago = (today - timedelta(days=15)).strftime('%d/%m/%Y')
    date_30_days_ago = (today - timedelta(days=30)).strftime('%d/%m/%Y')

    for p in products:
        tp = db.session.query(db.func.sum(Purchase.quantity)).filter_by(product_code=p.code).scalar() or 0
        ts = db.session.query(db.func.sum(Sale.quantity)).filter_by(product_code=p.code).scalar() or 0
        stock = tp - ts

        # Vendas últimos 15 días
        sales_15 = db.session.query(Sale).filter_by(product_code=p.code).filter(Sale.date >= date_15_days_ago).all()
        qty_15 = sum(s.quantity for s in sales_15)
        price_avg_15 = sum(s.unit_price * s.quantity for s in sales_15) / qty_15 if qty_15 > 0 else 0

        # Vendas últimos 30 días
        sales_30 = db.session.query(Sale).filter_by(product_code=p.code).filter(Sale.date >= date_30_days_ago).all()
        qty_30 = sum(s.quantity for s in sales_30)
        price_avg_30 = sum(s.unit_price * s.quantity for s in sales_30) / qty_30 if qty_30 > 0 else 0

        # Calcular custo médio
        purchases = Purchase.query.filter_by(product_code=p.code).all()
        if purchases:
            total_cost = sum(pur.quantity * pur.unit_cost for pur in purchases)
            total_qty = sum(pur.quantity for pur in purchases)
            avg_cost = total_cost / total_qty if total_qty > 0 else 0
        else:
            avg_cost = p.cost_price

        product_data.append({
            'code': p.code,
            'name': p.name,
            'category': p.category,
            'stock': stock,
            'avg_cost': round(avg_cost, 2),
            'qty_15': qty_15,
            'price_avg_15': round(price_avg_15, 2),
            'qty_30': qty_30,
            'price_avg_30': round(price_avg_30, 2),
            'status': p.status
        })

    return render_template_string(TEMPLATE, product_data=product_data, theme=Theme)

@app.route('/admin/catalog')
def admin_catalog():
    if session.get('role') != 'admin': return redirect(url_for('login'))
    products = Product.query.all()
    for p in products:
        tp = db.session.query(db.func.sum(Purchase.quantity)).filter_by(product_code=p.code).scalar() or 0
        ts = db.session.query(db.func.sum(Sale.quantity)).filter_by(product_code=p.code).scalar() or 0
        p.stock = tp - ts

        # Calcular custo médio
        purchases = Purchase.query.filter_by(product_code=p.code).all()
        if purchases:
            total_cost = sum(pur.quantity * pur.unit_cost for pur in purchases)
            total_qty = sum(pur.quantity for pur in purchases)
            p.avg_cost = total_cost / total_qty if total_qty > 0 else 0
        else:
            p.avg_cost = 0

        # Calcular venta media (todos los tiempos)
        sales = Sale.query.filter_by(product_code=p.code).all()
        if sales:
            total_sale = sum(s.quantity * s.unit_price for s in sales)
            total_qty_sale = sum(s.quantity for s in sales)
            p.avg_sale = total_sale / total_qty_sale if total_qty_sale > 0 else 0
        else:
            p.avg_sale = 0

    return render_template_string(TEMPLATE, products=products, theme=Theme)

@app.route('/admin/product/new', methods=['GET', 'POST'])
def admin_new_product():
    if session.get('role') != 'admin': return redirect(url_for('login'))
    if request.method == 'POST':
        code = generate_sku()
        name = request.form['name'].upper()
        category = request.form['category'].upper()

        db.session.add(Product(code=code, name=name, category=category, cost_price=0, sale_price=0, min_stock=5, status='ativo'))
        db.session.commit()
        flash(f'¡Producto registrado con éxito! SKU: <b>{code}</b>')
        return redirect(url_for('admin_catalog'))
    return render_template_string(TEMPLATE, theme=Theme)

@app.route('/admin/purchase', methods=['GET', 'POST'])
def admin_purchase():
    if session.get('role') != 'admin': return redirect(url_for('login'))
    products = Product.query.all()
    products_data = []
    for p in products:
        tp = db.session.query(db.func.sum(Purchase.quantity)).filter_by(product_code=p.code).scalar() or 0
        ts = db.session.query(db.func.sum(Sale.quantity)).filter_by(product_code=p.code).scalar() or 0
        p.stock = tp - ts

        # Calcular custo médio
        purchases = Purchase.query.filter_by(product_code=p.code).all()
        if purchases:
            total_cost = sum(pur.quantity * pur.unit_cost for pur in purchases)
            total_qty = sum(pur.quantity for pur in purchases)
            avg_cost = total_cost / total_qty if total_qty > 0 else 0
        else:
            avg_cost = p.cost_price

        products_data.append({
            'code': p.code,
            'name': p.name,
            'stock': p.stock,
            'avg_cost': round(avg_cost, 2),
            'last_cost': purchases[-1].unit_cost if purchases else p.cost_price,
            'last_date': purchases[-1].date if purchases else 'N/A',
            'purchase_count': len(purchases)
        })

    if request.method == 'POST':
        date = request.form['date']
        product_code = request.form['product_code']
        quantity = int(request.form['quantity'])
        unit_cost = float(request.form['unit_cost'])

        db.session.add(Purchase(date=date, product_code=product_code, quantity=quantity, unit_cost=unit_cost))
        db.session.commit()
        flash('¡Entrada de stock registrada correctamente!')
        return redirect(url_for('admin_dashboard'))
    import json
    return render_template_string(TEMPLATE, products=products, products_json=json.dumps(products_data), theme=Theme)

@app.route('/admin/sale', methods=['GET', 'POST'])
def admin_sale():
    if session.get('role') != 'admin': return redirect(url_for('login'))

    if request.method == 'POST':
        from datetime import datetime
        invoice_number = generate_invoice_number()
        date = request.form.get('date', datetime.now().strftime('%d/%m/%Y'))

        items = []
        total_amount = 0

        # Procesar todos los items del carrito
        i = 0
        while True:
            code = request.form.get(f'item_{i}_code')
            if not code:
                break

            quantity = int(request.form.get(f'item_{i}_quantity', 0))
            unit_price = float(request.form.get(f'item_{i}_price', 0))

            if quantity > 0 and unit_price > 0:
                subtotal = quantity * unit_price
                items.append({
                    'product_code': code,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'subtotal': subtotal
                })
                total_amount += subtotal

                # Registrar la venta individual para compatibilidad
                db.session.add(Sale(date=date, product_code=code, quantity=quantity, unit_price=unit_price))

            i += 1

        if not items:
            flash('❌ El carrito está vacío. Agregue productos antes de vender.')
            return redirect(url_for('admin_sale'))

        # Crear invoice
        invoice = Invoice(invoice_number=invoice_number, date=date, total_amount=total_amount)
        db.session.add(invoice)
        db.session.flush()

        # Crear items de la invoice
        for item in items:
            invoice_item = InvoiceItem(
                invoice_number=invoice_number,
                product_code=item['product_code'],
                quantity=item['quantity'],
                unit_price=item['unit_price'],
                subtotal=item['subtotal']
            )
            db.session.add(invoice_item)

        db.session.commit()
        flash(f'✅ ¡Venta procesada! ID Nota Fiscal: <b>{invoice_number}</b> | Total: <b>$ {total_amount:.2f}</b>')
        return redirect(url_for('admin_dashboard'))

    # GET: Mostrar formulario POS
    products = Product.query.all()
    products_data = []

    for p in products:
        tp = db.session.query(db.func.sum(Purchase.quantity)).filter_by(product_code=p.code).scalar() or 0
        ts = db.session.query(db.func.sum(Sale.quantity)).filter_by(product_code=p.code).scalar() or 0
        stock = tp - ts

        # Obtener precio promedio de venta
        sales = Sale.query.filter_by(product_code=p.code).all()
        if sales:
            avg_price = sum(s.unit_price * s.quantity for s in sales) / sum(s.quantity for s in sales)
        else:
            avg_price = p.sale_price

        products_data.append({
            'code': p.code,
            'name': p.name,
            'category': p.category,
            'stock': stock,
            'avg_price': round(avg_price, 2),
            'status': p.status
        })

    import json
    from datetime import datetime
    today = datetime.now().strftime('%d/%m/%Y')

    return render_template_string(TEMPLATE,
                                 products_data=json.dumps(products_data),
                                 today=today,
                                 theme=Theme)

@app.route('/admin/product/edit/<code>', methods=['GET', 'POST'])
def edit_product(code):
    if session.get('role') != 'admin': return redirect(url_for('login'))
    product = Product.query.filter_by(code=code).first()
    if not product: return redirect(url_for('admin_catalog'))

    if request.method == 'POST':
        product.name = request.form['name'].upper()
        product.category = request.form['category'].upper()
        db.session.commit()
        flash(f'¡Producto {code} actualizado correctamente!')
        return redirect(url_for('admin_catalog'))

    return render_template_string(TEMPLATE, edit_product=product, theme=Theme)

@app.route('/admin/product/toggle/<code>')
def toggle_product(code):
    if session.get('role') != 'admin': return redirect(url_for('login'))
    status = toggle_product_status(code)
    if status:
        flash(f'Producto {code} marcado como {status.upper()}.')
    return redirect(url_for('admin_catalog'))

@app.route('/admin/product/delete/<code>')
def delete_prod(code):
    if session.get('role') != 'admin': return redirect(url_for('login'))
    if delete_product(code):
        flash(f'Producto {code} eliminado correctamente.')
    return redirect(url_for('admin_catalog'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_ENV') != 'production'
    port = int(os.getenv('PORT', 5000))
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
