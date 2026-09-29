"""
=============================================================================
PROYECTO: Mini ERP - Muse Studio ("Tu mayorista online")
MÓDULO: app.py
=============================================================================
"""
import os
import json
from datetime import date, datetime, time
from flask import Flask, render_template_string, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from database import db
from sqlalchemy import func
from models import User, Product, Purchase, Sale, Invoice, InvoiceItem, InventoryCount, InventoryCountItem
from config.icons_colors import Theme
from utils import generate_sku, toggle_product_status, delete_product, generate_invoice_number

class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return str(obj)
        return super().default(obj)

load_dotenv(override=True)

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
    if not User.query.filter_by(username='vendedor').first():
        db.session.add(User(username='vendedor', password=generate_password_hash('vendedor123'), role='vendedor'))
    db.session.commit()

TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Muse Studio - Mini ERP</title>
    <style>
        :root {
            --bg-dark: #121212; --gold: #D4AF37; --pink: #FF69B4; --light-pink: #FFF0F5; --danger: #ff6b6b;
            --base-font: clamp(0.875rem, 2.5vw, 1.125rem);
            --h2-font: clamp(1.5rem, 5vw, 1.75rem);
            --h3-font: clamp(1.25rem, 4vw, 1.5rem);
            --btn-font: clamp(0.875rem, 2.5vw, 1.25rem);
            --table-font: clamp(0.75rem, 2vw, 1.125rem);
        }
        * { -webkit-text-size-adjust: 100%; }
        html { font-size: 16px; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f9f9f9; margin: 0; padding: 0; color: #333; font-size: var(--base-font); line-height: 1.5; }
        h1, h2, h3 { margin: 0.5rem 0; }
        h2 { font-size: var(--h2-font); }
        h3 { font-size: var(--h3-font); }
        label { font-size: clamp(0.875rem, 2.5vw, 1.125rem); font-weight: 600; display: block; margin-bottom: 0.5rem; }
        .header { background: var(--bg-dark); color: var(--gold); padding: clamp(2rem, 8vw, 3rem) 1.5rem; text-align: center; border-bottom: 4px solid var(--pink); }
        .header h1 { margin: 0; font-size: clamp(2rem, 8vw, 2.5rem); }
        .header p { margin: 1rem 0 0 0; color: var(--pink); font-size: clamp(1.25rem, 4vw, 1.75rem); }
        .container { max-width: 1000px; margin: clamp(0.625rem, 2vw, 1.25rem) auto; background: white; padding: clamp(1rem, 4vw, 1.875rem); border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); }
        .btn { background: var(--gold); color: #000; padding: clamp(0.75rem, 2vw, 1.125rem) clamp(1rem, 3vw, 1.5rem); border: none; border-radius: 8px; font-weight: bold; cursor: pointer; text-decoration: none; display: flex; align-items: center; justify-content: center; font-size: var(--btn-font); min-height: clamp(2.5rem, 8vw, 3.5rem); min-width: clamp(2.5rem, 8vw, 3.5rem); touch-action: manipulation; }
        .btn-pink { background: var(--pink); color: white; }
        .btn-dark { background: var(--bg-dark); color: var(--gold); }
        table { width: 100%; border-collapse: collapse; margin-top: 1.25rem; font-size: var(--table-font); overflow-x: auto; display: block; }
        th, td { border: 1px solid #e0e0e0; padding: clamp(0.625rem, 2vw, 1.25rem); text-align: left; }
        th { background-color: var(--light-pink); font-weight: bold; }
        .alert { padding: 1rem; background: #d4edda; color: #155724; margin-bottom: 1.25rem; border-radius: 8px; font-size: var(--base-font); }
        form input, form select, textarea { padding: clamp(0.875rem, 2.5vw, 1.125rem); margin: clamp(0.875rem, 2vw, 1.25rem) 0 clamp(1.25rem, 3vw, 1.5rem) 0; width: 100%; box-sizing: border-box; border: 2px solid #ddd; border-radius: 8px; font-size: var(--base-font); min-height: clamp(2.75rem, 8vw, 3.125rem); }
        td .btn { font-size: clamp(0.75rem, 2vw, 1rem); padding: clamp(0.5rem, 1.5vw, 0.875rem) clamp(0.75rem, 2vw, 1.125rem); min-height: clamp(2rem, 6vw, 2.75rem); margin: clamp(0.25rem, 1vw, 0.5rem); }
        form input:focus, form select:focus, textarea:focus { border-color: var(--pink); outline: none; }
        .nav-bar { background: #222; color: white; border-bottom: 3px solid var(--pink); padding: clamp(1.5rem, 4vw, 2rem); overflow-x: auto; }
        .nav-bar a { color: var(--gold); text-decoration: none; transition: all 0.3s ease; font-size: clamp(1.25rem, 3.5vw, 1.75rem); min-height: 88px; display: flex; align-items: center; padding: clamp(1rem, 2.5vw, 1.5rem); }
        .nav-bar a:hover { background: rgba(212, 175, 55, 0.2) !important; transform: translateY(-2px); }
        .kpi-container { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: clamp(1rem, 2vw, 1.875rem); margin-bottom: 1.875rem; }
        .kpi-card { background: #fff5f8; border: 2px solid #ffccd5; padding: clamp(1rem, 3vw, 1.5rem); border-radius: 12px; text-align: center; }
        .kpi-card h3 { margin: 0; color: #666; font-size: clamp(0.875rem, 2vw, 1rem); }
        .kpi-card p { margin: clamp(0.75rem, 2vw, 1rem) 0 0 0; font-size: clamp(1.5rem, 6vw, 2rem); font-weight: bold; color: var(--pink); }
        .quick-actions { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: clamp(1rem, 2vw, 1.125rem); margin-bottom: 1.5rem; }
        .quick-actions .btn { padding: clamp(1.5rem, 4vw, 2rem) clamp(1rem, 2vw, 1rem); font-size: clamp(1rem, 3vw, 1.5rem); min-height: clamp(5rem, 15vw, 7.5rem); flex-direction: column; gap: clamp(0.75rem, 2vw, 1rem); line-height: 1.3; }
        .kpi-value { transition: filter 0.3s ease; }
        .kpi-value.hidden { filter: blur(8px); }
        .kpi-value.hidden::after { content: '••••'; position: absolute; left: 50%; transform: translateX(-50%); }
        button[onclick*="toggleValues"] { transition: all 0.3s ease; }

        @media (max-width: 768px) {
            :root { --base-font: clamp(0.875rem, 2vw, 1rem); --table-font: clamp(0.75rem, 1.5vw, 0.875rem); }
            .container { padding: clamp(1rem, 3vw, 1.25rem); margin: clamp(0.5rem, 1vw, 1rem) auto; }
            table { font-size: var(--table-font); }
            th, td { padding: clamp(0.5rem, 1.5vw, 0.875rem); }
            .kpi-container { grid-template-columns: 1fr; }
            .quick-actions { grid-template-columns: 1fr; }
            .quick-actions .btn { min-height: clamp(4rem, 12vw, 5rem); font-size: clamp(0.875rem, 2.5vw, 1rem); }
            .btn { min-height: clamp(2.5rem, 7vw, 2.75rem); }
            td .btn { display: block; width: 100%; margin-bottom: clamp(0.25rem, 1vw, 0.5rem); }
            form input, form select, textarea { min-height: clamp(2.5rem, 7vw, 2.75rem); }
            label { font-size: clamp(0.75rem, 2vw, 0.875rem); }
            .nav-bar a { font-size: clamp(1rem, 2.5vw, 1.25rem); min-height: 70px; }
            .nav-bar { padding: clamp(1rem, 2vw, 1.5rem); }
        }
    </style>
</head>
<body>

<div class="header">
    <img src="{{ theme.LOGO.path }}" alt="{{ theme.LOGO.alt }}" style="max-width: 180px; max-height: 180px; margin-bottom: 16px;">
    <h1>{{ theme.BRAND.name }}</h1>
    <p>{{ theme.BRAND.tagline }} • {{ theme.BRAND.description }}</p>
</div>

{% if session.get('user') %}
<div class="nav-bar" style="display: flex; justify-content: space-between; align-items: center; padding: 15px 30px;">
    <div style="display: flex; align-items: center; gap: 16px;">
        <span style="font-size: 18px; color: #999;">Sesión activa:</span>
        <b style="color: var(--gold); font-size: 16px;">{{ session['user'] | upper }}</b>
        <span style="background: var(--pink); color: white; padding: 3px 8px; border-radius: 3px; font-size: 16px; font-weight: bold;">{{ session['role'] | upper }}</span>
    </div>

    <div style="display: flex; gap: 20px; align-items: center;">
        {% if session['role'] == 'dev' %}
            <a href="/dev" style="display: flex; align-items: center; gap: 8px; color: var(--gold); text-decoration: none; font-weight: bold; padding: 12px 15px; background: rgba(255,255,255,0.1); border-radius: 5px; transition: all 0.3s;">
                🏠 Inicio
            </a>
        {% elif session['role'] == 'admin' %}
            <a href="/admin" style="display: flex; align-items: center; gap: 8px; color: var(--gold); text-decoration: none; font-weight: bold; padding: 12px 15px; background: rgba(255,255,255,0.1); border-radius: 5px; transition: all 0.3s;">
                🏠 Inicio
            </a>
        {% endif %}

        <div style="height: 25px; width: 1px; background: rgba(255,255,255,0.2);"></div>

        <a href="/logout" style="display: flex; align-items: center; gap: 8px; color: #ff6b6b; text-decoration: none; font-weight: bold; padding: 12px 15px; background: rgba(255,107,107,0.1); border-radius: 5px; transition: all 0.3s; border: 1px solid rgba(255,107,107,0.3);">
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

    {% elif session.get('role') == 'dev' or (session.get('role') == 'admin' and request.endpoint == 'admin_users') %}
        {% if session.get('role') == 'dev' %}
        <h2>Panel de Desarrollador - Gestión de Usuarios</h2>
        {% else %}
        <h2>👥 Gestión de Usuarios - Vendedores</h2>
        {% endif %}
        <form method="POST" action="/dev/create_user" style="background: #fafafa; padding: 20px; border-radius: 8px; border: 1px solid #eee;">
            {% if session.get('role') == 'dev' %}
            <h3>Registrar Nuevo Usuario</h3>
            {% else %}
            <h3>👨‍💼 Crear Nuevo Vendedor</h3>
            {% endif %}
            <label>Nombre de Usuario:</label>
            <input type="text" name="new_user" required style="padding: 16px; font-size: 18px;">
            <label>Contraseña:</label>
            <input type="password" name="new_password" required style="padding: 16px; font-size: 18px;">
            {% if session.get('role') == 'dev' %}
            <label>Rol:</label>
            <select name="role" style="padding: 16px; font-size: 18px;">
                <option value="vendedor">Vendedor (POS)</option>
                <option value="admin">Admin (ERP)</option>
                <option value="dev">Dev</option>
            </select>
            {% else %}
            <input type="hidden" name="role" value="vendedor">
            <div style="background: #e8f5e9; padding: 14px; border-radius: 8px; margin-bottom: 18px; border-left: 4px solid #4CAF50;">
                <strong style="color: #4CAF50; font-size: 16px;">✅ Rol: VENDEDOR (Automático)</strong>
            </div>
            {% endif %}
            <button type="submit" class="btn btn-pink" style="width: 100%; padding: 16px; font-size: 18px;">
                {% if session.get('role') == 'dev' %}
                ✅ Crear Usuario
                {% else %}
                👨‍💼 Crear Vendedor
                {% endif %}
            </button>
        </form>

        <div style="margin-top: 30px;">
            {% if session.get('role') == 'dev' %}
            <h3>📋 Todos los Usuarios</h3>
            {% else %}
            <h3>👥 Vendedores Creados</h3>
            {% endif %}
        </div>
        <table style="margin-top: 15px;">
            <tr>
                <th style="font-size: 18px;">ID</th>
                <th style="font-size: 18px;">👤 Usuario</th>
                <th style="font-size: 18px;">🏷️ Rol</th>
                <th style="font-size: 18px;">⚙️ Acciones</th>
            </tr>
            {% for u in users %}
                {% if session.get('role') == 'dev' or u.role == 'vendedor' %}
                <tr>
                    <td style="font-size: 18px;">{{ u.id }}</td>
                    <td style="font-size: 18px;"><b>{{ u.username }}</b></td>
                    <td style="font-size: 18px; color: {% if u.role == 'vendedor' %}#4CAF50{% elif u.role == 'admin' %}#FF6B9D{% else %}#2196F3{% endif %}; font-weight: bold;">
                        {% if u.role == 'vendedor' %}👨‍💼 VENDEDOR{% elif u.role == 'admin' %}🔐 ADMIN{% else %}🔧 DEV{% endif %}
                    </td>
                    <td>
                        <a href="/dev/reset_password/{{ u.id }}" class="btn btn-dark" style="padding: 12px 18px; font-size: 16px; text-decoration: none; margin: 4px;">🔑 Reset Pass</a>
                        {% if (session.get('role') == 'dev' and u.role != 'dev') or (session.get('role') == 'admin' and u.role == 'vendedor') %}
                        <a href="/dev/delete_user/{{ u.id }}" class="btn" style="background: #f44336; color: white; padding: 12px 18px; font-size: 16px; text-decoration: none; margin: 4px;" onclick="return confirm('¿Eliminar usuario?');">🗑️ Eliminar</a>
                        {% endif %}
                    </td>
                </tr>
                {% endif %}
            {% endfor %}
        </table>

    {% elif session.get('role') in ['admin', 'vendedor'] and request.endpoint == 'admin_dashboard' %}
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px;">
            <h2 style="margin: 0;">{{ theme.OPERATIONS.historial }} Dashboard General - Muse Studio</h2>
            <button type="button" onclick="toggleValuesVisibility()" style="background: var(--bg-dark); color: var(--gold); border: 3px solid var(--gold); padding: 28px 30px; border-radius: 8px; cursor: pointer; font-size: 36px; font-weight: bold; min-height: 90px; display: flex; align-items: center; justify-content: center;">
                Mostrar
            </button>
        </div>

        {% if session['role'] == 'admin' %}
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
        {% endif %}

        <div style="margin-top: 35px; margin-bottom: 25px; border-top: 2px solid #e0e0e0; padding-top: 25px;">
            <h3 style="margin-bottom: 20px;">⚡ Accesos Rápidos (Flujo Operativo)</h3>
            <div class="quick-actions">
                <a href="/admin/sale" class="btn btn-pink">💳 Venta</a>
                <a href="/admin/catalog" class="btn btn-dark">📚 Catálogo</a>
                {% if session['role'] == 'admin' %}
                <a href="/admin/product/new" class="btn" style="background: #4CAF50; color: white;">✨ Nuevo</a>
                <a href="/admin/purchase" class="btn btn-dark">📦 Entrada</a>
                <a href="/admin/sales-history" class="btn" style="background: #FF6B9D; color: white;">📊 Análisis</a>
                {% endif %}
                <a href="/admin/price-guide" class="btn" style="background: #2196F3; color: white;">💰 Guía</a>
                {% if session['role'] == 'admin' %}
                <a href="/admin/inventory" class="btn" style="background: #FF9800; color: white;">📦 Inventario</a>
                <a href="/admin/vendors" class="btn" style="background: #9C27B0; color: white;">👥 Vendedores</a>
                <a href="/admin/users" class="btn" style="background: #607D8B; color: white;">👤 Usuarios</a>
                {% endif %}
            </div>
        </div>

        <script>
            let valuesVisible = false;
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

                button.textContent = valuesVisible ? 'Ocultar' : 'Mostrar';
                button.style.background = valuesVisible ? '#f44336' : 'var(--bg-dark)';
                button.style.borderColor = valuesVisible ? 'var(--gold)' : '#f44336';
            }
        </script>


    {% elif request.endpoint == 'cash_flow' %}
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h2>{{ theme.OPERATIONS.historial }} Flujo de Caja (últimos 30 días)</h2>
            <a href="/admin" class="btn-dark btn" style="font-size: 18px;">← Volver al Dashboard</a>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-bottom: 30px;">
            <div style="background: #fff5f8; padding: 20px; border-radius: 8px; text-align: center; border-left: 4px solid #4CAF50;">
                <h3 style="margin: 0; color: #666; font-size: 18px;">💰 Total Ventas (Entrada)</h3>
                <p style="font-size: 24px; color: #4CAF50; font-weight: bold; margin: 10px 0;">$ {{ "%.2f"|format(total_sales) }}</p>
            </div>
            <div style="background: #fff5f8; padding: 20px; border-radius: 8px; text-align: center; border-left: 4px solid #f44336;">
                <h3 style="margin: 0; color: #666; font-size: 18px;">🛒 Total Compras (Salida)</h3>
                <p style="font-size: 24px; color: #f44336; font-weight: bold; margin: 10px 0;">$ {{ "%.2f"|format(total_purchases) }}</p>
            </div>
            <div style="background: {% if balance >= 0 %}#e8f5e9{% else %}#ffebee{% endif %}; padding: 20px; border-radius: 8px; text-align: center; border-left: 4px solid {% if balance >= 0 %}#4CAF50{% else %}#f44336{% endif %};">
                <h3 style="margin: 0; color: #666; font-size: 18px;">📊 Saldo Neto</h3>
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
            <a href="/admin" class="btn-dark btn" style="font-size: 18px;">← Volver al Dashboard</a>
        </div>
        <p style="color: #666; margin-bottom: 20px; font-size: 18px;">Histórico de ventas y precios promedio (últimos 15 y 30 días)</p>
        <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 18px; margin-top: 20px;">
            {% for p in product_data %}
            <div style="background: white; border-left: 6px solid var(--pink); border-radius: 10px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); {% if p.status == 'inactivo' %}opacity: 0.6;{% endif %}">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px;">
                    <div>
                        <div style="font-size: 20px; font-weight: bold; color: #333;">{{ p.name }}</div>
                        <div style="font-size: 14px; color: #999;">{{ p.code }}</div>
                    </div>
                    <span style="background: {% if p.status == 'ativo' %}#e8f5e9{% else %}#ffebee{% endif %}; color: {% if p.status == 'ativo' %}#4CAF50{% else %}#f44336{% endif %}; padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: bold;">{{ p.status | upper }}</span>
                </div>
                <div style="border-top: 1px solid #eee; padding-top: 12px; margin-bottom: 12px;">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; font-size: 16px;">
                        <div>
                            <div style="color: #999; font-size: 12px; margin-bottom: 4px;">💰 Costo Promedio</div>
                            <div style="color: #FF6B9D; font-weight: bold; font-size: 18px;">{{ p.avg_cost | money }}</div>
                        </div>
                        <div>
                            <div style="color: #999; font-size: 12px; margin-bottom: 4px;">📊 Stock</div>
                            <div style="color: #4CAF50; font-weight: bold; font-size: 18px;">{{ p.stock }} un</div>
                        </div>
                    </div>
                </div>
                <div style="background: #f8f8f8; padding: 14px; border-radius: 8px; font-size: 14px;">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                        <div style="text-align: center; padding-bottom: 10px; border-bottom: 1px solid #ddd;">
                            <div style="color: #666; font-size: 12px; margin-bottom: 6px;">📊 15 días</div>
                            <div style="font-weight: bold;">{{ p.qty_15 }} un</div>
                            <div style="color: #2196F3; font-weight: bold; font-size: 16px;">{{ p.price_avg_15 | money }}</div>
                        </div>
                        <div style="text-align: center; padding-bottom: 10px; border-bottom: 1px solid #ddd;">
                            <div style="color: #666; font-size: 12px; margin-bottom: 6px;">📊 30 días</div>
                            <div style="font-weight: bold;">{{ p.qty_30 }} un</div>
                            <div style="color: #4CAF50; font-weight: bold; font-size: 16px;">{{ p.price_avg_30 | money }}</div>
                        </div>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>

    {% elif request.endpoint == 'admin_catalog' %}
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h2>{{ theme.OPERATIONS.historial }} Catálogo de Productos</h2>
            <a href="/admin" class="btn-dark btn" style="font-size: 18px;">← Volver al Dashboard</a>
        </div>
        {% if session['role'] == 'admin' %}
        <div style="margin: 15px 0;">
            <a href="/admin/product/new" class="btn btn-pink">➕ Nuevo Producto</a>
        </div>
        {% endif %}
        <div style="margin-bottom: 20px;">
            <input type="text" id="filterInput" placeholder="🔍 Buscar en tabla..." style="padding: 14px; border: 2px solid #D4AF37; border-radius: 5px; width: 100%; max-width: 400px; font-size: 16px;">
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 18px; margin-top: 20px;">
            {% for p in products %}
            <div style="background: white; border-left: 6px solid var(--pink); border-radius: 10px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); {% if p.status == 'inativo' %}opacity: 0.6;{% endif %}" data-sku="{{ p.code }}" data-nombre="{{ p.name }}" data-categoria="{{ p.category }}" data-costo="{{ p.avg_cost }}" data-salida="{{ p.avg_sale }}" data-stock="{{ p.stock }}" data-estado="{{ p.status }}">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px;">
                    <div style="flex: 1;">
                        <div style="font-size: 20px; font-weight: bold; color: #333;">{{ p.name }}</div>
                        <div style="font-size: 14px; color: #999; margin-bottom: 8px;">{{ p.code }}</div>
                        <div style="display: inline-block; background: #f0f0f0; padding: 6px 12px; border-radius: 20px; font-size: 13px; color: #666;">{{ p.category }}</div>
                    </div>
                    <span style="background: {% if p.status == 'ativo' %}#e8f5e9{% else %}#ffebee{% endif %}; color: {% if p.status == 'ativo' %}#4CAF50{% else %}#f44336{% endif %}; padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: bold;">{{ p.status | upper }}</span>
                </div>
                <div style="border-top: 1px solid #eee; padding-top: 12px; margin-bottom: 16px;">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; font-size: 16px;">
                        <div>
                            <div style="color: #999; font-size: 12px; margin-bottom: 4px;">💰 Costo Prom.</div>
                            <div style="color: #FF6B9D; font-weight: bold; font-size: 18px;">{{ p.avg_cost | money }}</div>
                        </div>
                        <div>
                            <div style="color: #999; font-size: 12px; margin-bottom: 4px;">📊 Venta Prom.</div>
                            <div style="color: #4CAF50; font-weight: bold; font-size: 18px;">{{ p.avg_sale | money }}</div>
                        </div>
                    </div>
                </div>
                <div style="background: #f8f8f8; padding: 12px; border-radius: 8px; margin-bottom: 16px; text-align: center;">
                    <div style="color: #999; font-size: 12px; margin-bottom: 4px;">📦 Stock</div>
                    <div style="font-size: 20px; font-weight: bold; color: {% if p.stock > p.min_stock %}#4CAF50{% else %}#FF6B9D{% endif %};">{{ p.stock }} un {% if p.stock <= p.min_stock %} ⚠️{% endif %}</div>
                </div>
                {% if session['role'] == 'admin' %}
                <div style="display: flex; flex-direction: column; gap: 8px;">
                    <button type="button" onclick="openEditModal('{{ p.code }}', '{{ p.name }}', '{{ p.category }}', {{ p.sale_price }})" class="btn" style="background: #2196F3; color: white; padding: 12px 16px; font-size: 16px; cursor: pointer;">
                        ✏️ Editar
                    </button>
                    <a href="/admin/product/toggle/{{ p.code }}" class="btn" style="background: #FFC107; color: #000; padding: 12px 16px; font-size: 16px;">
                        {% if p.status == 'ativo' %} 🔒 Desactivar {% else %} ✅ Activar {% endif %}
                    </a>
                    <a href="/admin/product/delete/{{ p.code }}" class="btn" style="background: #f44336; color: white; padding: 12px 16px; font-size: 16px;" onclick="return confirm('¿Seguro de eliminar?');">
                        🗑️ Eliminar
                    </a>
                </div>
                {% endif %}
            </div>
            {% endfor %}
        </div>

        <!-- MODAL DE EDICIÓN -->
        <div id="editModal" style="display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index: 1000; align-items: center; justify-content: center; flex-direction: column;">
            <div style="background: white; padding: 30px; border-radius: 12px; max-width: 500px; width: 90%; box-shadow: 0 4px 20px rgba(0,0,0,0.2);">
                <h2 style="margin: 0 0 20px 0;">✏️ Editar Producto</h2>

                <form id="editForm" style="display: flex; flex-direction: column; gap: 16px;">
                    <input type="hidden" name="product_code" id="modalProductCode">

                    <div>
                        <label style="font-weight: bold;">Nombre:</label>
                        <input type="text" id="modalName" name="name" required style="padding: 12px; border: 2px solid #ddd; border-radius: 5px; width: 100%; box-sizing: border-box;">
                    </div>

                    <div>
                        <label style="font-weight: bold;">Categoría:</label>
                        <input type="text" id="modalCategory" name="category" required style="padding: 12px; border: 2px solid #ddd; border-radius: 5px; width: 100%; box-sizing: border-box;">
                    </div>

                    <div>
                        <label style="font-weight: bold;">🛍️ Valor de Venta Unitário ($):</label>
                        <input type="number" step="0.01" id="modalSalePrice" name="sale_price" required style="padding: 12px; border: 2px solid #4CAF50; border-radius: 5px; width: 100%; box-sizing: border-box;">
                    </div>

                    <hr style="margin: 10px 0; border: none; border-top: 1px solid #eee;">

                    <h4 style="margin: 10px 0; color: #FF9800;">➕ Agregar Cantidad</h4>

                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                        <div>
                            <label style="font-weight: bold;">Cantidad:</label>
                            <input type="number" id="modalQuantity" name="quantity_adjustment" min="0" placeholder="0" style="padding: 12px; border: 2px solid #FF9800; border-radius: 5px; width: 100%; box-sizing: border-box;">
                        </div>
                        <div>
                            <label style="font-weight: bold;">Valor Compra ($):</label>
                            <input type="number" step="0.01" id="modalCostTotal" name="cost_adjustment_total" placeholder="0.00" style="padding: 12px; border: 2px solid #FF9800; border-radius: 5px; width: 100%; box-sizing: border-box;">
                        </div>
                    </div>

                    <div style="display: flex; gap: 12px; margin-top: 20px;">
                        <button type="button" onclick="submitEditForm(event)" class="btn btn-pink" style="flex: 1; padding: 12px;">✅ Guardar</button>
                        <button type="button" onclick="closeEditModal()" style="flex: 1; padding: 12px; background: #ccc; border: none; border-radius: 8px; cursor: pointer; font-weight: bold;">❌ Cancelar</button>
                    </div>
                </form>
            </div>
        </div>

        <script>
            console.log('Script initialized for catalog modal');
            // Funciones para el modal de edición
            function openEditModal(code, name, category, salePrice) {
                console.log('openEditModal called with code:', code);
                document.getElementById('modalProductCode').value = code;
                document.getElementById('modalName').value = name;
                document.getElementById('modalCategory').value = category;
                document.getElementById('modalSalePrice').value = salePrice;
                document.getElementById('modalQuantity').value = 0;
                document.getElementById('modalCostTotal').value = 0;
                document.getElementById('editModal').style.display = 'flex';
                window.currentProductCode = code;
                console.log('currentProductCode set to:', window.currentProductCode);
            }

            function closeEditModal() {
                document.getElementById('editModal').style.display = 'none';
            }

            function submitEditForm(event) {
                event.preventDefault();
                const form = document.getElementById('editForm');
                const code = window.currentProductCode;
                console.log('Code from window:', code);
                const url = '/admin/product/edit/' + code;
                console.log('Posting to:', url);
                const formData = new FormData(form);

                fetch(url, {
                    method: 'POST',
                    body: formData
                }).then(response => {
                    console.log('Response:', response.status);
                    if (response.ok) {
                        window.location.href = '/admin/catalog';
                    } else {
                        alert('Error al guardar: ' + response.status);
                    }
                }).catch(error => {
                    console.error('Error:', error);
                    alert('Error: ' + error);
                });
            }

            // Cerrar modal al hacer click fuera
            document.getElementById('editModal').addEventListener('click', function(e) {
                if (e.target === this) closeEditModal();
            });

        </script>

    {% elif request.endpoint == 'edit_product' %}
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h2>{{ theme.ACTIONS.editar }} Editar Producto</h2>
            <a href="/admin/catalog" class="btn-dark btn" style="font-size: 18px;">← Volver al Catálogo</a>
        </div>
        <form method="POST" style="max-width: 700px;">
            <label style="font-weight: bold; color: #333;">{{ theme.INFORMATION.codigo }} SKU: <span style="color: var(--pink);">{{ edit_product.code }}</span></label>

            <label style="margin-top: 20px;">{{ theme.INFORMATION.nombre }} Nombre del Producto:</label>
            <input type="text" name="name" value="{{ edit_product.name }}" required style="padding: 14px; border: 2px solid #ddd; border-radius: 5px; width: 100%; box-sizing: border-box; font-size: 16px;">

            <label style="margin-top: 20px;">{{ theme.INFORMATION.precio }} Categoría:</label>
            <input type="text" name="category" value="{{ edit_product.category }}" required style="padding: 14px; border: 2px solid #ddd; border-radius: 5px; width: 100%; box-sizing: border-box; font-size: 16px;">

            <div style="background: #f9f9f9; padding: 16px; border-radius: 8px; margin-top: 20px; border-left: 4px solid #2196F3;">
                <label style="margin-top: 0; font-weight: bold;">🛍️ Precio de Venta Unitario ($):</label>
                <div style="color: #999; font-size: 12px; margin-bottom: 8px;">Precio que cobras por cada unidad</div>
                <input type="number" step="0.01" name="sale_price" value="{{ edit_product.sale_price }}" required id="salePriceInput" style="padding: 14px; border: 2px solid #4CAF50; border-radius: 5px; width: 100%; box-sizing: border-box; font-size: 16px;">
            </div>

            <div style="background: #fff3e0; padding: 16px; border-radius: 8px; margin-top: 20px; border-left: 4px solid #FF9800;">
                <h4 style="margin: 0 0 16px 0; color: #FF9800; font-size: 16px;">➕ Agregar más Cantidad al Stock</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 16px;">
                    <div>
                        <label style="margin-top: 0;">📦 Cantidad:</label>
                        <input type="number" name="quantity_adjustment" min="0" placeholder="0" id="qtyAdjustInput" style="padding: 14px; border: 2px solid #FF9800; border-radius: 5px; width: 100%; box-sizing: border-box; font-size: 16px;">
                    </div>
                    <div>
                        <label style="margin-top: 0;">💵 Valor da Compra ($):</label>
                        <div style="color: #999; font-size: 12px; margin-bottom: 4px;">Total que gastaste</div>
                        <input type="number" step="0.01" id="costTotalAdjustment" placeholder="0.00" style="padding: 14px; border: 2px solid #FF9800; border-radius: 5px; width: 100%; box-sizing: border-box; font-size: 16px;">
                    </div>
                </div>
                <div style="background: white; padding: 12px; border-radius: 6px; border: 1px solid #FFD699;">
                    <div style="font-size: 12px; color: #999; margin-bottom: 4px;">💰 Costo Unitário (calculado):</div>
                    <div style="font-size: 20px; font-weight: bold; color: #FF9800;" id="calcCostUnitario">$ 0.00</div>
                </div>
            </div>

            <div style="background: #f0f8ff; padding: 16px; border-radius: 8px; margin-top: 20px; border-left: 4px solid #2196F3;">
                <div style="font-size: 14px; color: #666; margin-bottom: 8px;">📊 Margen de Ganancia:</div>
                <div id="marginResult" style="font-size: 24px; font-weight: bold; color: #4CAF50;">-</div>
                <div id="marginPercent" style="font-size: 14px; color: #999; margin-top: 4px;">-</div>
            </div>

            <input type="hidden" name="cost_adjustment_total" id="costAdjustmentHidden" value="0">

            <div style="display: flex; gap: 16px; margin-top: 28px;">
                <button type="submit" class="btn btn-pink" style="flex: 1; padding: 16px; font-size: 18px;">✅ Guardar Cambios</button>
                <a href="/admin/catalog" class="btn" style="background: #ccc; flex: 1; text-align: center; padding: 16px; font-size: 18px;">❌ Cancelar</a>
            </div>
            <p style="color: #666; margin-top: 20px; font-size: 14px;">✓ Todos los textos se convertirán a MAYÚSCULA automáticamente</p>
        </form>

        <script>
            const saleInput = document.getElementById('salePriceInput');
            const qtyInput = document.getElementById('qtyAdjustInput');
            const costTotalInput = document.getElementById('costTotalAdjustment');
            const marginResult = document.getElementById('marginResult');
            const marginPercent = document.getElementById('marginPercent');
            const calcCostUnitarioDiv = document.getElementById('calcCostUnitario');
            const costHiddenInput = document.getElementById('costAdjustmentHidden');
            const form = document.querySelector('form');

            function updateMargin() {
                const costTotal = parseFloat(costTotalInput.value) || 0;
                const saleUnitario = parseFloat(saleInput.value) || 0;
                const qty = parseInt(qtyInput.value) || 0;

                // Calcular costo unitario
                const costUnitario = qty > 0 ? (costTotal / qty) : 0;

                // Calcular ganancias
                const ventaTotal = saleUnitario * qty;
                const marginTotal = ventaTotal - costTotal;
                const marginUnitario = saleUnitario - costUnitario;
                const percent = saleUnitario > 0 ? ((marginUnitario / saleUnitario) * 100).toFixed(1) : 0;

                // Mostrar costo unitario calculado
                calcCostUnitarioDiv.textContent = '$ ' + costUnitario.toFixed(2);

                // Mostrar margen de ganancia
                if (qty > 0) {
                    marginResult.textContent = '$ ' + marginTotal.toFixed(2) + ' (' + qty + 'x)';
                    marginPercent.textContent = marginUnitario.toFixed(2) + ' unitario | ' + percent + '% ganancia';
                    marginResult.style.color = marginTotal >= 0 ? '#4CAF50' : '#f44336';
                } else {
                    marginResult.textContent = '-';
                    marginPercent.textContent = '-';
                }
            }

            saleInput.addEventListener('input', updateMargin);
            qtyInput.addEventListener('input', updateMargin);
            costTotalInput.addEventListener('input', updateMargin);

            // Manejar el costo total cuando se envía el formulario
            if (form) {
                form.addEventListener('submit', function(e) {
                    costHiddenInput.value = costTotalInput.value || 0;
                });
            }

            updateMargin();
        </script>

    {% elif request.endpoint == 'admin_new_product' %}
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h2>{{ theme.ACTIONS.guardar }} ➕ Nuevo Producto</h2>
            <a href="/admin" class="btn-dark btn" style="font-size: 18px;">← Volver</a>
        </div>
        <p style="color: #666; font-size: 16px; margin-bottom: 20px;">{{ theme.INFORMATION.codigo }} SKU se genera automáticamente</p>

        <form method="POST" style="max-width: 700px;">
            <label>{{ theme.INFORMATION.nombre }} Nombre del Producto:</label>
            <input type="text" name="name" placeholder="Ej: Labial Mate Velvet" required style="padding: 14px; border: 2px solid #ddd; border-radius: 5px; width: 100%; box-sizing: border-box; font-size: 16px;">

            <label style="margin-top: 20px;">{{ theme.INFORMATION.precio }} Categoría:</label>
            <input type="text" name="category" placeholder="Ej: Makeup / Beauty / Accessories" required style="padding: 14px; border: 2px solid #ddd; border-radius: 5px; width: 100%; box-sizing: border-box; font-size: 16px;">

            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-top: 20px;">
                <div>
                    <label style="margin-top: 0;">💰 Precio de Costo ($):</label>
                    <input type="number" step="0.01" name="cost_price" placeholder="0.00" required style="padding: 14px; border: 2px solid #FF6B9D; border-radius: 5px; width: 100%; box-sizing: border-box; font-size: 16px;">
                </div>
                <div>
                    <label style="margin-top: 0;">🛍️ Precio de Venta ($):</label>
                    <input type="number" step="0.01" name="sale_price" placeholder="0.00" required style="padding: 14px; border: 2px solid #4CAF50; border-radius: 5px; width: 100%; box-sizing: border-box; font-size: 16px;">
                </div>
                <div>
                    <label style="margin-top: 0;">📦 Cantidad Inicial:</label>
                    <input type="number" name="initial_quantity" min="0" placeholder="0" style="padding: 14px; border: 2px solid #2196F3; border-radius: 5px; width: 100%; box-sizing: border-box; font-size: 16px;">
                </div>
            </div>

            <div style="display: flex; gap: 16px; margin-top: 28px;">
                <button type="submit" class="btn btn-pink" style="flex: 1; padding: 16px; font-size: 18px;">✅ Crear Producto</button>
                <a href="/admin" class="btn" style="background: #ccc; flex: 1; text-align: center; padding: 16px; font-size: 18px;">❌ Cancelar</a>
            </div>
            <p style="color: #666; margin-top: 20px; font-size: 14px;">✓ Todos los textos se convertirán a MAYÚSCULA automáticamente</p>
        </form>

    {% elif request.endpoint == 'admin_purchase' %}
        <h2>📥 Registrar Entrada de Compra (Reabastecimiento)</h2>
        <form method="POST">
            <label>Fecha:</label>
            <input type="date" name="date" required>
            <label>Buscar Producto (por SKU o Nombre):</label>
            <div style="position: relative; margin-bottom: 15px;">
                <input type="text" id="productSearch" placeholder="Ej: MS-000001 o Labial Mate" style="width: 100%; padding: 14px; border: 2px solid #ccc; border-radius: 5px; box-sizing: border-box; font-size: 18px;">
                <ul id="productList" style="position: absolute; top: 100%; left: 0; right: 0; background: white; border: 2px solid #ccc; border-top: none; border-radius: 0 0 5px 5px; max-height: 400px; overflow-y: auto; list-style: none; padding: 0; margin: 0; display: none; z-index: 1000;">
                </ul>
            </div>
            <input type="hidden" name="product_code" id="productCode" required>
            <div id="productInfo" style="background: #f0f0f0; padding: 20px; border-radius: 5px; margin-bottom: 15px; display: none; font-size: 18px;">
                <strong style="font-size: 20px;">Producto Seleccionado:</strong> <span id="selectedProduct" style="font-size: 20px;"></span><br>
                <strong style="font-size: 20px;">Stock Actual:</strong> <span id="selectedStock" style="font-size: 20px;"></span><br>
                <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #ccc;">
                    <strong style="font-size: 18px;">{{ theme.OPERATIONS.historial }} Historial de Compras:</strong><br>
                    <div style="color: #666; margin-top: 10px; font-size: 18px;">
                        Compras anteriores: <span id="purchaseCount" style="color: #FF6B9D; font-weight: bold;">0</span><br>
                        Costo Promedio: $ <span id="avgCost" style="color: #4CAF50; font-weight: bold;">0.00</span><br>
                        Última Compra: $ <span id="lastCost" style="color: #2196F3; font-weight: bold;">0.00</span> (<span id="lastDate">-</span>)
                    </div>
                </div>
            </div>
            <label>Cantidad Comprada:</label>
            <input type="number" name="quantity" min="1" required>
            <label>Costo Unitario de Adquisición ($):</label>
            <div style="display: grid; grid-template-columns: 1fr auto; gap: 16px; margin-bottom: 15px;">
                <input type="number" step="0.01" name="unit_cost" id="unitCost" required style="padding: 14px; border: 1px solid #ccc; border-radius: 5px; box-sizing: border-box;">
                <select id="costSelector" style="padding: 14px; border: 1px solid #ccc; border-radius: 5px; background: white; cursor: pointer; font-size: 18px; min-width: 140px;">
                    <option value="manual">{{ theme.OPERATIONS.manual }} Manual</option>
                    <option value="avg">{{ theme.OPERATIONS.promedio }} Promedio</option>
                    <option value="last">{{ theme.OPERATIONS.ultima }} Última</option>
                </select>
            </div>
            <div style="display: flex; gap: 16px; margin-top: 20px;">
                <button type="submit" class="btn btn-pink" style="flex: 1;">Registrar Entrada y Actualizar Stock</button>
                <a href="/admin" class="btn" style="background: #ccc; flex: 1; text-align: center;">Cancelar</a>
            </div>
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
                    li.style.cssText = 'padding: 14px; border-bottom: 1px solid #eee; cursor: pointer; transition: background 0.2s; font-size: 16px;';
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
            <a href="/admin" class="btn-dark btn" style="font-size: 18px;">← Volver al Dashboard</a>
        </div>

        <div style="display: block; margin-bottom: 520px;">
            <h3 style="margin-bottom: 15px; font-size: 22px;">📦 Catálogo de Productos</h3>
            <input type="text" id="searchInput" placeholder="🔍 Buscar por nombre..." style="padding: 16px; border: 2px solid #D4AF37; border-radius: 8px; width: 100%; margin-bottom: 20px; box-sizing: border-box; font-size: 18px; font-weight: 500;">

            <div id="productsContainer" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 18px; max-height: 70vh; overflow-y: auto; padding-right: 8px;">
                <!-- Los productos se cargan aquí con JavaScript -->
            </div>
            <style>
                @media (max-width: 768px) {
                    #productsContainer { grid-template-columns: 1fr !important; }
                }
            </style>
        </div>

        <!-- CARRITO FLOTANTE PARA MOBILE -->
        <div style="position: fixed; bottom: 0; left: 0; right: 0; background: #f8f8f8; border-top: 3px solid #D4AF37; box-shadow: 0 -4px 10px rgba(0,0,0,0.1); z-index: 1000;">
            <div style="padding: 30px; max-width: 1000px; margin: 0 auto;">
                <!-- Info del Carrito -->
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 28px;">
                    <div>
                        <h4 style="margin: 0; color: var(--pink); font-size: 28px; font-weight: bold;">🛒 Carrito</h4>
                        <small style="color: #666; font-size: 22px;">Items: <span id="cartCount" style="font-weight: bold; color: var(--pink); font-size: 26px;">0</span></small>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 20px; color: #999; margin-bottom: 10px; font-weight: bold;">TOTAL</div>
                        <div id="cartTotal" style="font-size: 40px; font-weight: bold; color: #4CAF50;">$ 0.00</div>
                    </div>
                </div>

                <!-- Botones - Stack en mobile, grid en desktop -->
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px;">
                    <button type="button" onclick="toggleCartModal()" class="btn" style="background: #FFC107; color: black; padding: 0; font-size: 44px; font-weight: bold; border: none; border-radius: 8px; cursor: pointer; transition: all 0.2s; min-height: 140px; display: flex; align-items: center; justify-content: center;">
                        Ver Carrito
                    </button>
                    <button type="button" onclick="toggleDiscountMode()" id="discountToggleBtn" class="btn" style="background: #FF9800; color: white; padding: 0; font-size: 44px; font-weight: bold; border: none; border-radius: 8px; cursor: pointer; transition: all 0.2s; min-height: 140px; display: flex; align-items: center; justify-content: center;">
                        Descuento
                    </button>
                    <form method="POST" id="checkoutForm" style="margin: 0;">
                        <input type="hidden" name="date" value="{{ today }}">
                        <div id="formItems"></div>
                        <button type="submit" class="btn btn-pink" style="width: 100%; padding: 0; font-size: 44px; font-weight: bold; border: none; border-radius: 8px; cursor: pointer; background: var(--pink); color: white; box-shadow: 0 2px 8px rgba(0,0,0,0.15); transition: all 0.2s; min-height: 140px; display: flex; align-items: center; justify-content: center;">
                            PROCESAR
                        </button>
                    </form>
                </div>

                <!-- Responsive: Stack en mobile muy pequeño -->
                <style>
                    @media (max-width: 600px) {
                        #checkoutForm button {
                            padding: 16px !important;
                            font-size: 16px !important;
                        }
                    }
                </style>
            </div>
        </div>

        <!-- MODAL CARRITO FULLSCREEN -->
        <div id="cartModal" style="display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: white; z-index: 3000; padding: 0; overflow: hidden; flex-direction: column;">
            <!-- Header -->
            <div style="background: var(--pink); color: white; padding: 25px; display: flex; justify-content: space-between; align-items: center; flex-shrink: 0; box-shadow: 0 4px 10px rgba(0,0,0,0.15);">
                <h2 style="margin: 0; font-size: 32px; font-weight: bold;">🛒 Tu Carrito</h2>
                <button type="button" onclick="toggleCartModal()" style="background: rgba(255,255,255,0.3); border: none; color: white; font-size: 40px; cursor: pointer; padding: 0; border-radius: 50%; width: 60px; height: 60px; display: flex; align-items: center; justify-content: center; font-weight: bold;">✕</button>
            </div>

            <!-- Contenido Items - Scroll -->
            <div id="cartItemsModal" style="padding: 25px; padding-bottom: 450px; flex: 1; overflow-y: auto;">
                <p style="text-align: center; color: #999; margin: 80px 0; font-size: 22px;">Carrito vacío</p>
            </div>

            <!-- Footer Total y Botones - FIJO -->
            <div style="position: fixed; bottom: 0; left: 0; right: 0; background: #f8f8f8; padding: 30px; border-top: 3px solid #D4AF37; z-index: 100; box-shadow: 0 -4px 10px rgba(0,0,0,0.1);">
                <div style="display: flex; justify-content: space-between; margin-bottom: 28px; font-size: 40px; font-weight: bold; padding: 18px 0; border-bottom: 2px solid #DDD;">
                    <span style="color: #333;">TOTAL:</span>
                    <span id="cartTotalModal" style="color: #4CAF50;">$ 0.00</span>
                </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px;">
                        <button type="button" onclick="toggleCartModal()" class="btn" style="background: #FFC107; color: black; padding: 0; font-size: 44px; font-weight: bold; border: none; border-radius: 8px; cursor: pointer; transition: all 0.2s; min-height: 140px; display: flex; align-items: center; justify-content: center;">
                            Seguir Comprando
                        </button>
                        <button type="button" onclick="toggleDiscountMode()" id="discountToggleBtn" class="btn" style="background: #FF9800; color: white; padding: 0; font-size: 44px; font-weight: bold; border: none; border-radius: 8px; cursor: pointer; transition: all 0.2s; min-height: 140px; display: flex; align-items: center; justify-content: center;">
                            Descuento
                        </button>
                        <button type="button" onclick="clearCart()" class="btn" style="background: #f44336; color: white; padding: 0; font-size: 44px; font-weight: bold; border: none; border-radius: 8px; cursor: pointer; transition: all 0.2s; min-height: 140px; display: flex; align-items: center; justify-content: center;">
                            Limpiar
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <script>
            const productsData = {{ products_data | safe }};
            let cart = [];
            let discountMode = false;

            function toggleCartModal() {
                const modal = document.getElementById('cartModal');
                modal.style.display = modal.style.display === 'none' ? 'flex' : 'none';
                updateCartModal();
            }

            function toggleDiscountMode() {
                discountMode = !discountMode;
                const btn = document.getElementById('discountToggleBtn');
                btn.style.background = discountMode ? '#4CAF50' : '#FF9800';
                btn.textContent = discountMode ? '✅ Descuento Activo' : '💰 Descuento';
                updateCartModal();
            }

            function renderProducts() {
                const container = document.getElementById('productsContainer');
                const searchValue = document.getElementById('searchInput').value.toLowerCase();
                container.innerHTML = '';

                const filtered = productsData.filter(p =>
                    p.name.toLowerCase().includes(searchValue) ||
                    p.code.toLowerCase().includes(searchValue)
                );

                if (filtered.length === 0) {
                    container.innerHTML = '<div style="text-align: center; padding: 40px; color: #999;">No hay productos que coincidan</div>';
                    return;
                }

                filtered.forEach(product => {
                    const isInactive = product.status !== 'ativo';
                    const cardHTML = `
                        <div style="background: white; border-left: 8px solid var(--pink); border-radius: 10px; padding: 28px; cursor: pointer; transition: all 0.3s; display: flex; flex-direction: column; gap: 20px; ${isInactive ? 'opacity: 0.5; pointer-events: none;' : 'box-shadow: 0 2px 8px rgba(0,0,0,0.12);'}">
                            <div>
                                <div style="font-weight: bold; color: #333; margin-bottom: 10px; font-size: 26px;">${product.name}</div>
                                <div style="font-size: 18px; color: #999; margin-bottom: 12px;">${product.code}</div>
                                <div style="display: flex; gap: 20px; font-size: 18px;">
                                    <span style="color: var(--pink); font-weight: bold; font-size: 22px;">$ ${product.avg_price.toFixed(2)}</span>
                                    <span style="color: #666;">Stock: <strong style="color: ${product.stock > 0 ? '#4CAF50' : '#f44336'}; font-size: 22px;">${product.stock}</strong></span>
                                </div>
                            </div>
                            <div>
                                ${product.stock > 0 ? `
                                    <button type="button" onclick="addToCart('${product.code}', '${product.name}', ${product.avg_price}, ${product.stock})" class="btn" style="width: 100%; padding: 20px 24px; font-size: 22px; background: var(--pink); color: white; border: none; border-radius: 8px; font-weight: bold; cursor: pointer;">
                                        Agregar
                                    </button>
                                ` : `
                                    <div style="width: 100%; padding: 20px 24px; color: #f44336; font-size: 22px; font-weight: bold; background: #ffebee; border-radius: 8px; text-align: center;">
                                        Sin Stock
                                    </div>
                                `}
                            </div>
                        </div>
                    `;
                    container.innerHTML += cardHTML;
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
                    } else {
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
                        const discount = item.discount || 0;
                        const finalPrice = item.price - discount;
                        formHTML += `
                            <input type="hidden" name="item_${index}_code" value="${item.code}">
                            <input type="hidden" name="item_${index}_quantity" value="${item.quantity}">
                            <input type="hidden" name="item_${index}_price" value="${finalPrice}">
                            <input type="hidden" name="item_${index}_discount" value="${discount}">
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
                    const discount = item.discount || 0;
                    total += (item.price - discount) * item.quantity;
                    itemCount += item.quantity;
                });

                document.getElementById('cartTotal').textContent = '$ ' + total.toFixed(2);
                document.getElementById('cartCount').textContent = itemCount;
            }

            function updateDiscount(code, discountValue) {
                const item = cart.find(i => i.code === code);
                if (item) {
                    item.discount = Math.max(0, Math.min(discountValue, item.price)); // Máximo = precio unit
                    updateCart();
                }
            }

            function updateCartModal() {
                const cartItemsDiv = document.getElementById('cartItemsModal');
                const cartTotalModal = document.getElementById('cartTotalModal');

                if (cart.length === 0) {
                    cartItemsDiv.innerHTML = '<p style="text-align: center; color: #999; margin: 40px 0; font-size: 20px;">Carrito vacío</p>';
                    cartTotalModal.textContent = '$ 0.00';
                } else {
                    let html = '';
                    let total = 0;

                    cart.forEach(item => {
                        const discount = item.discount || 0;
                        const finalPrice = item.price - discount;
                        const subtotal = finalPrice * item.quantity;
                        total += subtotal;

                        html += `
                            <div style="background: white; padding: 51px; margin-bottom: 34px; border-radius: 10px; border-left: 10px solid var(--pink); box-shadow: 0 2px 6px rgba(0,0,0,0.08);">
                                <div style="font-weight: bold; font-size: 54px; margin-bottom: 24px; color: #333;">${item.name}</div>
                                <div style="font-size: 31px; color: #999; margin-bottom: 27px;">${item.code}</div>
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 27px; font-size: 37px;">
                                    <span style="color: #666;">Precio: <strong style="color: var(--pink); font-size: 48px;">$ ${item.price.toFixed(2)}</strong></span>
                                    <span style="color: #666;">Qty: <input type="number" value="${item.quantity}" min="1" max="${item.stock}" onchange="updateQuantity('${item.code}', parseInt(this.value))" style="width: 119px; padding: 17px; text-align: center; border: 3px solid #ccc; border-radius: 5px; font-size: 41px; font-weight: bold;"></span>
                                </div>
                                ${discountMode ? `
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 27px; font-size: 34px;">
                                    <label style="color: #FF9800; font-weight: bold; font-size: 34px;">💰 Descuento:</label>
                                    <input type="number" min="0" max="${item.price}" step="0.01" value="${discount}" onchange="updateDiscount('${item.code}', parseFloat(this.value))" placeholder="0.00" style="width: 153px; padding: 17px; text-align: right; border: 3px solid #FF9800; border-radius: 5px; font-size: 34px; font-weight: bold;">
                                </div>
                                ` : ''}
                                <div style="display: flex; justify-content: space-between; align-items: center; padding-top: 27px; border-top: 2px solid #eee;">
                                    <strong style="color: #4CAF50; font-size: 51px;">$ ${subtotal.toFixed(2)}</strong>
                                    <button type="button" onclick="removeFromCart('${item.code}')" class="btn" style="padding: 20px 34px; font-size: 31px; background: #f44336; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; min-height: 68px;">
                                        Quitar
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

        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 16px;">
            <h2 style="margin: 0;">📊 Histórico de Ventas - Análisis de Ganancias</h2>
            <div style="display: flex; gap: 16px;">
                <button onclick="exportToExcel()" class="btn" style="background: #4CAF50; color: white; padding: 14px 15px; font-size: 18px;">
                    📥 Exportar a Excel
                </button>
                <a href="/admin" class="btn-dark btn" style="font-size: 18px;">← Volver</a>
            </div>
        </div>

        <!-- FILTROS -->
        <div style="background: #f9f9f9; padding: 15px; border-radius: 8px; margin-bottom: 20px; display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 16px;">
            <div>
                <label style="font-size: 16px; color: #666;">Desde:</label>
                <input type="date" id="dateFrom" style="width: 100%; padding: 12px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box;">
            </div>
            <div>
                <label style="font-size: 16px; color: #666;">Hasta:</label>
                <input type="date" id="dateTo" style="width: 100%; padding: 12px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box;">
            </div>
            <div style="display: flex; align-items: flex-end; gap: 8px;">
                <button onclick="applyDateFilter()" class="btn btn-pink" style="padding: 12px 15px; font-size: 16px; flex: 1;">Filtrar</button>
                <button onclick="resetDateFilter()" class="btn" style="padding: 12px 15px; font-size: 16px; background: #ccc; flex: 1;">Limpiar</button>
            </div>
        </div>

        <!-- ESTADÍSTICAS GENERALES -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 30px;">
            <div style="background: #e8f5e9; border-left: 4px solid #4CAF50; padding: 20px; border-radius: 8px;">
                <h4 style="margin: 0; color: #666; font-size: 18px;">💰 Ingresos Totales</h4>
                <p style="margin: 10px 0 0 0; font-size: 24px; font-weight: bold; color: #4CAF50;">{{ total_revenue | money }}</p>
            </div>
            <div style="background: #ffebee; border-left: 4px solid #f44336; padding: 20px; border-radius: 8px;">
                <h4 style="margin: 0; color: #666; font-size: 18px;">📦 Costo Total de Productos</h4>
                <p style="margin: 10px 0 0 0; font-size: 24px; font-weight: bold; color: #f44336;">{{ total_cost_all | money }}</p>
            </div>
            <div style="background: {% if total_profit >= 0 %}#e3f2fd{% else %}#ffebee{% endif %}; border-left: 4px solid {% if total_profit >= 0 %}#2196F3{% else %}#f44336{% endif %}; padding: 20px; border-radius: 8px;">
                <h4 style="margin: 0; color: #666; font-size: 18px;">💎 Ganancia Neta</h4>
                <p style="margin: 10px 0 0 0; font-size: 24px; font-weight: bold; color: {% if total_profit >= 0 %}#2196F3{% else %}#f44336{% endif %};">{{ total_profit | money }}</p>
            </div>
            <div style="background: #fff3e0; border-left: 4px solid #FF9800; padding: 20px; border-radius: 8px;">
                <h4 style="margin: 0; color: #666; font-size: 18px;">📈 Margen de Ganancia Promedio</h4>
                <p style="margin: 10px 0 0 0; font-size: 24px; font-weight: bold; color: #FF9800;">{{ "%.1f"|format(avg_profit_margin) }}%</p>
            </div>
        </div>

        <!-- GRÁFICOS DE TENDENCIAS -->
        <h3 style="margin-top: 40px;">📈 Gráficos de Tendencias</h3>

        <!-- BOTONES DE VISTA -->
        <div style="margin-bottom: 20px; display: flex; gap: 8px; flex-wrap: wrap; justify-content: center;">
            <button onclick="changeChartView('daily')" class="btn btn-pink" id="btnDaily" style="padding: 14px 15px; font-size: 18px; font-weight: bold;">📅 Diario</button>
            <button onclick="changeChartView('weekly')" class="btn" style="padding: 14px 15px; font-size: 18px; background: #2196F3; color: white;">📊 Semanal</button>
            <button onclick="changeChartView('monthly')" class="btn" style="padding: 14px 15px; font-size: 18px; background: #FF9800; color: white;">📈 Mensual</button>
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
            <input type="text" id="filterSales" placeholder="🔍 Buscar por NF o fecha..." style="padding: 14px; border: 1px solid #ccc; border-radius: 5px; width: 100%; max-width: 400px; box-sizing: border-box;">
        </div>

        <div style="overflow-x: auto;">
            <table id="salesTable" style="width: 100%; border-collapse: collapse;">
                <tr style="background-color: #fff5f8; cursor: pointer; user-select: none;">
                    <th style="cursor: pointer; padding: 12px; text-align: left; border: 1px solid #e0e0e0;">📅 Fecha ↕️</th>
                    <th style="cursor: pointer; padding: 12px; text-align: left; border: 1px solid #e0e0e0;">🧾 NF/Invoice ↕️</th>
                    <th style="cursor: pointer; padding: 12px; text-align: center; border: 1px solid #e0e0e0;">📦 Items ↕️</th>
                    <th style="cursor: pointer; padding: 12px; text-align: right; border: 1px solid #e0e0e0;">💰 Ingresos ↕️</th>
                    <th style="cursor: pointer; padding: 12px; text-align: right; border: 1px solid #e0e0e0;">🏷️ Descuento ↕️</th>
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
                    <td style="padding: 12px; border: 1px solid #e0e0e0; text-align: right; color: #FF9800; font-weight: bold;">{{ inv.total_discount | money }}</td>
                    <td style="padding: 12px; border: 1px solid #e0e0e0; text-align: right; color: #f44336;">{{ inv.total_cost | money }}</td>
                    <td style="padding: 12px; border: 1px solid #e0e0e0; text-align: right; font-weight: bold; color: {% if inv.profit >= 0 %}#2196F3{% else %}#f44336{% endif %};">{{ inv.profit | money }}</td>
                    <td style="padding: 12px; border: 1px solid #e0e0e0; text-align: center; background: {% if inv.profit_margin >= 30 %}#e8f5e9{% elif inv.profit_margin >= 15 %}#fff3e0{% else %}#ffebee{% endif %};">{{ "%.1f"|format(inv.profit_margin) }}%</td>
                </tr>
                {% else %}
                <tr>
                    <td colspan="8" style="padding: 20px; text-align: center; color: #999;">No hay ventas registradas aún</td>
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

    {% elif request.endpoint == 'admin_vendors' %}
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h2>👥 Reporte de Vendedores</h2>
            <a href="/admin" class="btn-dark btn" style="font-size: 18px;">← Volver al Dashboard</a>
        </div>
        <p style="color: #666; margin-bottom: 20px; font-size: 18px;">📊 Vendedores activos y su desempeño de ventas</p>

        <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; margin-top: 20px;">
            {% for v in vendedor_data %}
            <div style="background: white; border-left: 6px solid #9C27B0; border-radius: 10px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 16px;">
                    <div>
                        <div style="font-size: 22px; font-weight: bold; color: #333;">👨‍💼 {{ v.username }}</div>
                        <div style="font-size: 14px; color: #999; margin-top: 4px;">ID: #{{ v.user_id }}</div>
                    </div>
                    <span style="background: #e8f5e9; color: #4CAF50; padding: 8px 14px; border-radius: 20px; font-size: 12px; font-weight: bold;">ACTIVO</span>
                </div>
                <div style="background: #f8f8f8; padding: 16px; border-radius: 8px; margin-top: 16px;">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; text-align: center;">
                        <div>
                            <div style="color: #999; font-size: 12px; margin-bottom: 6px;">📊 Ventas</div>
                            <div style="font-size: 24px; font-weight: bold; color: #2196F3;">{{ v.total_sales }}</div>
                        </div>
                        <div>
                            <div style="color: #999; font-size: 12px; margin-bottom: 6px;">💰 Valor Total</div>
                            <div style="font-size: 20px; font-weight: bold; color: #4CAF50;">{{ v.total_value | money }}</div>
                        </div>
                    </div>
                </div>
                <a href="/admin/vendor/{{ v.user_id }}/sales" class="btn" style="background: #2196F3; color: white; width: 100%; padding: 14px; margin-top: 16px; text-align: center; text-decoration: none;">
                    📈 Ver Detalle
                </a>
            </div>
            {% endfor %}
        </div>

    {% elif request.endpoint == 'vendor_sales' %}
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px;">
            <h2>👤 Detalles de Vendedor: {{ vendedor.username }}</h2>
            <a href="/admin/vendors" class="btn-dark btn" style="font-size: 18px;">← Volver</a>
        </div>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px;">
            <div style="background: #fff5f8; border: 2px solid #ffccd5; padding: 24px; border-radius: 12px; text-align: center;">
                <h3 style="margin: 0; color: #666; font-size: 18px;">👥 Vendedor</h3>
                <p style="margin: 12px 0 0 0; font-size: 28px; font-weight: bold; color: var(--pink);">{{ vendedor.username }}</p>
            </div>
            <div style="background: #e8f5e9; border: 2px solid #c8e6c9; padding: 24px; border-radius: 12px; text-align: center;">
                <h3 style="margin: 0; color: #666; font-size: 18px;">📊 Total Ventas</h3>
                <p style="margin: 12px 0 0 0; font-size: 28px; font-weight: bold; color: #4CAF50;">{{ total_sales }}</p>
            </div>
            <div style="background: #fff3e0; border: 2px solid #ffe0b2; padding: 24px; border-radius: 12px; text-align: center;">
                <h3 style="margin: 0; color: #666; font-size: 18px;">💰 Valor Total</h3>
                <p style="margin: 12px 0 0 0; font-size: 28px; font-weight: bold; color: #FF9800;">{{ total_value | money }}</p>
            </div>
        </div>

        <p style="color: #999; text-align: center; margin-top: 40px;">📍 Aquí irán más detalles y reportes del vendedor</p>

    {% elif request.endpoint == 'admin_inventory' %}
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h2>📦 Auditoria de Inventario</h2>
            <a href="/admin" class="btn-dark btn" style="font-size: 18px;">← Volver</a>
        </div>

        <table style="width: 100%; border-collapse: collapse;">
            <tr><th>📅 Fecha</th><th>👤 Usuario</th><th>Estado</th><th>📊 Varianza Total</th><th>❌ Pérdida</th><th>⚙️ Acciones</th></tr>
            {% for count in counts %}
            <tr>
                <td style="padding: 12px; border: 1px solid #e0e0e0;">{{ count.count_date }}</td>
                <td style="padding: 12px; border: 1px solid #e0e0e0;">{{ count.user_id }}</td>
                <td style="padding: 12px; border: 1px solid #e0e0e0;"><b>{{ count.status | upper }}</b></td>
                <td style="padding: 12px; border: 1px solid #e0e0e0;">{{ count.total_variance }}</td>
                <td style="padding: 12px; border: 1px solid #e0e0e0; color: #f44336; font-weight: bold;">{{ count.total_loss }}</td>
                <td style="padding: 12px; border: 1px solid #e0e0e0;"><a href="/admin/inventory/{{ count.id }}" class="btn" style="padding: 5px 10px; font-size: 16px;">📋 Ver</a></td>
            </tr>
            {% else %}
            <tr><td colspan="6" style="padding: 20px; text-align: center; color: #999;">Sin conteos aún</td></tr>
            {% endfor %}
        </table>

        <br>
        <form method="POST" style="display: inline;">
            <button type="submit" class="btn btn-pink" style="padding: 14px 20px;">➕ Iniciar Nueva Conteo</button>
        </form>

    {% elif request.endpoint == 'view_inventory' %}
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h2>📦 Conteo de Inventario #{{ count.id }} - {{ count.count_date }}</h2>
            <a href="/admin/inventory" class="btn-dark btn" style="font-size: 18px;">← Volver</a>
        </div>

        <div style="background: #fff5f8; padding: 15px; border-radius: 5px; margin-bottom: 20px; border-left: 4px solid #FF9800;">
            <b>Estado:</b> <span style="color: {% if count.status == 'finalizado' %}#4CAF50{% else %}#FF9800{% endif %};">{{ count.status | upper }}</span> |
            <b>Varianza:</b> {{ total_variance }} |
            <b>Pérdida Total:</b> <span style="color: #f44336; font-weight: bold;">{{ total_loss }}</span>
        </div>

        {% if count.status == 'em_progreso' %}
        <h3>Agregar Producto a Conteo</h3>
        <form method="POST" style="background: #f9f9f9; padding: 20px; border-radius: 5px; margin-bottom: 20px;">
            <div style="display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 15px;">
                <div>
                    <label>Buscar Producto:</label>
                    <input type="text" id="productSearch" placeholder="Digita nombre o código..." style="width: 100%; padding: 14px; border: 1px solid #ccc; border-radius: 5px;">
                    <input type="hidden" name="product_code" id="productCode" required>
                    <div id="productList" style="position: absolute; background: white; border: 1px solid #ccc; border-radius: 5px; max-height: 200px; overflow-y: auto; width: 300px; display: none;"></div>
                    <div id="productInfo" style="margin-top: 10px; padding: 14px; background: #e8f5e9; border-radius: 5px; display: none;">
                        <b>Estoque Sistema:</b> <span id="systemStockDisplay">-</span>
                    </div>
                </div>
                <div>
                    <label>Cantidad Física:</label>
                    <input type="number" name="physical_count" id="physicalCount" min="0" required style="width: 100%; padding: 14px; border: 1px solid #ccc; border-radius: 5px;">
                </div>
                <div>
                    <label>Motivo (si aplica):</label>
                    <select name="loss_reason" style="width: 100%; padding: 14px; border: 1px solid #ccc; border-radius: 5px;">
                        <option value="">-- Sin motivo --</option>
                        <option value="QUEBRA_DANO">Quebra/Daño</option>
                        <option value="ROUBO_FURTO">Robo/Furto</option>
                        <option value="VENCIMIENTO">Vencimiento</option>
                        <option value="PERDA_DESCONOCIDA">Pérdida Desconocida</option>
                        <option value="AJUSTE_ANTERIOR">Ajuste Anterior</option>
                        <option value="OTRO">Otro</option>
                    </select>
                </div>
            </div>
            <textarea name="notes" placeholder="Notas adicionales..." style="width: 100%; padding: 14px; border: 1px solid #ccc; border-radius: 5px; margin-top: 10px; height: 60px;"></textarea>
            <button type="submit" class="btn btn-pink" style="padding: 14px 20px; margin-top: 10px;">✅ Agregar Producto</button>
        </form>

        <script>
            const productos = {{ products_json | safe }};
            const productSearch = document.getElementById('productSearch');
            const productList = document.getElementById('productList');
            const productCode = document.getElementById('productCode');
            const productInfo = document.getElementById('productInfo');
            const systemStockDisplay = document.getElementById('systemStockDisplay');

            productSearch.addEventListener('input', (e) => {
                const query = e.target.value.toLowerCase();
                if (query.length < 1) {
                    productList.style.display = 'none';
                    return;
                }

                const filtered = productos.filter(p =>
                    p.code.toLowerCase().includes(query) ||
                    p.name.toLowerCase().includes(query)
                );

                productList.innerHTML = filtered.map(p =>
                    `<div style="padding: 14px; border-bottom: 1px solid #eee; cursor: pointer; font-size: 16px;" onclick="selectProduct('${p.code}', '${p.name}', ${p.system_stock || 0})">
                        <b style="font-size: 18px;">${p.code}</b> - ${p.name}<br>
                        <div style="color: #666; font-size: 20px; margin-top: 5px;">Stock sistema: ${p.system_stock || 0}</div>
                    </div>`
                ).join('');

                productList.style.display = filtered.length > 0 ? 'block' : 'none';
            });

            function selectProduct(code, name, systemStock) {
                productCode.value = code;
                productSearch.value = `${code} - ${name}`;
                systemStockDisplay.textContent = systemStock;
                productInfo.style.display = 'block';
                productList.style.display = 'none';
                document.getElementById('physicalCount').focus();
            }
        </script>
        {% endif %}

        <h3>Productos Contados</h3>
        <div style="overflow-x: auto;">
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="background-color: #fff5f8;">
                    <th style="padding: 12px; text-align: left; border: 1px solid #e0e0e0;">Código</th>
                    <th style="padding: 12px; text-align: center; border: 1px solid #e0e0e0;">Sistema</th>
                    <th style="padding: 12px; text-align: center; border: 1px solid #e0e0e0;">Físico</th>
                    <th style="padding: 12px; text-align: center; border: 1px solid #e0e0e0;">Varianza</th>
                    <th style="padding: 12px; text-align: left; border: 1px solid #e0e0e0;">Tipo</th>
                    <th style="padding: 12px; text-align: left; border: 1px solid #e0e0e0;">Motivo / Estado</th>
                    <th style="padding: 12px; text-align: center; border: 1px solid #e0e0e0;">⚙️</th>
                </tr>
                {% for item in items %}
                <tr style="background: {% if item.status == 'analisis' %}#FFF3E0{% elif item.variance_type == 'FALTA' %}#ffebee{% elif item.variance_type == 'EXCESO' %}#fff3e0{% else %}#e8f5e9{% endif %};">
                    <td style="padding: 12px; border: 1px solid #e0e0e0;"><b>{{ item.product_code }}</b></td>
                    <td style="padding: 12px; border: 1px solid #e0e0e0; text-align: center;">{{ item.system_quantity }}</td>
                    <td style="padding: 12px; border: 1px solid #e0e0e0; text-align: center;">{{ item.physical_count }}</td>
                    <td style="padding: 12px; border: 1px solid #e0e0e0; text-align: center; font-weight: bold; color: {% if item.variance_type == 'FALTA' %}#f44336{% elif item.variance_type == 'EXCESO' %}#FF9800{% else %}#4CAF50{% endif %};">{{ item.variance }}</td>
                    <td style="padding: 12px; border: 1px solid #e0e0e0;">{{ item.variance_type }}</td>
                    <td style="padding: 12px; border: 1px solid #e0e0e0;">
                        {% if item.status == 'analisis' %}
                            <span style="background: #FF9800; color: white; padding: 5px 8px; border-radius: 3px; font-size: 16px;">🔍 Análisis</span>
                        {% else %}
                            {{ item.loss_reason or '-' }}
                        {% endif %}
                    </td>
                    <td style="padding: 12px; border: 1px solid #e0e0e0; text-align: center;">
                        {% if item.status == 'analisis' %}
                            <button onclick="openResolveAnalysisModal({{ item.id }}, '{{ item.loss_reason }}', '{{ item.notes }}')" class="btn" style="padding: 5px 10px; font-size: 18px; background: #FF9800; color: white;">✏️ Resolver</button>
                        {% else %}
                            <a href="/admin/inventory/{{ count.id }}/remove/{{ item.id }}" class="btn" style="padding: 5px 10px; font-size: 18px; background: #f44336;">🗑️</a>
                        {% endif %}
                    </td>
                </tr>
                {% else %}
                <tr><td colspan="7" style="padding: 20px; text-align: center; color: #999;">Sin items agregados aún</td></tr>
                {% endfor %}
            </table>
        </div>

        <!-- Modal para resolver análisis -->
        <div id="resolveAnalysisModal" style="display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index: 1000; display: flex; justify-content: center; align-items: center;">
            <div style="background: white; padding: 40px; border-radius: 10px; max-width: 700px; width: 90%; max-height: 90vh; overflow-y: auto;">
                <h2 style="font-size: 26px; margin-top: 0;">Resolver Análisis</h2>
                <form method="POST" style="display: flex; flex-direction: column; gap: 20px;">
                    <input type="hidden" name="action" value="update_reason">
                    <input type="hidden" name="item_id" id="editItemId">
                    <div>
                        <label style="font-size: 18px; font-weight: 600; display: block; margin-bottom: 10px;">Motivo de Pérdida:</label>
                        <select name="loss_reason" id="editReason" required style="width: 100%; padding: 14px; border: 2px solid #ccc; border-radius: 5px; font-size: 18px;">
                            <option value="QUEBRA_DANO">Quebra/Daño</option>
                            <option value="ROUBO_FURTO">Robo/Furto</option>
                            <option value="VENCIMIENTO">Vencimiento</option>
                            <option value="PERDA_DESCONOCIDA">Pérdida Desconocida</option>
                            <option value="AJUSTE_ANTERIOR">Ajuste Anterior</option>
                            <option value="OTRO">Otro</option>
                        </select>
                    </div>
                    <textarea name="notes" id="editNotes" placeholder="Notas..." style="width: 100%; padding: 14px; border: 2px solid #ccc; border-radius: 5px; height: 120px; font-size: 18%;"></textarea>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                        <button type="submit" class="btn btn-pink" style="padding: 16px 20px; font-size: 18px;">✅ Guardar</button>
                        <button type="button" onclick="closeResolveAnalysisModal()" class="btn btn-dark" style="padding: 16px 20px; font-size: 18px;">Cancelar</button>
                    </div>
                </form>
            </div>
        </div>

        <script>
            function openResolveAnalysisModal(itemId, reason, notes) {
                document.getElementById('editItemId').value = itemId;
                document.getElementById('editReason').value = reason || '';
                document.getElementById('editNotes').value = notes || '';
                document.getElementById('resolveAnalysisModal').style.display = 'flex';
            }
            function closeResolveAnalysisModal() {
                document.getElementById('resolveAnalysisModal').style.display = 'none';
            }
        </script>

        {% if count.status == 'em_progreso' and items %}
        <div style="margin-top: 20px; display: flex; gap: 16px;">
            <a href="/admin/inventory/{{ count.id }}/finalize" class="btn" style="padding: 14px 20px; background: #4CAF50; color: white;">✅ Finalizar Conteo</a>
            <a href="/admin/inventory" class="btn btn-dark" style="padding: 14px 20px;">Cancelar</a>
        </div>
        {% endif %}

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
            if user.role == 'dev':
                return redirect(url_for('dev_panel'))
            elif user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:  # vendedor
                return redirect(url_for('admin_sale'))
        flash('Credenciales inválidas.')
    return render_template_string(TEMPLATE, theme=Theme)

@app.route('/dev')
def dev_panel():
    if session.get('role') != 'dev': return redirect(url_for('login'))
    return render_template_string(TEMPLATE, users=User.query.all(), theme=Theme)

@app.route('/dev/create_user', methods=['POST'])
def create_user():
    if session.get('role') not in ['dev', 'admin']: return redirect(url_for('login'))
    new_username = request.form['new_user']
    new_password = request.form['new_password']
    role = request.form['role']

    # Admin solo puede crear vendedores
    if session.get('role') == 'admin' and role != 'vendedor':
        flash('❌ Admin solo puede crear Vendedores!')
        return redirect(url_for('admin_users'))

    if User.query.filter_by(username=new_username).first():
        flash('❌ El nombre de usuario ya existe.')
        redirect_to = 'dev_panel' if session.get('role') == 'dev' else 'admin_users'
        return redirect(url_for(redirect_to))

    hashed_pw = generate_password_hash(new_password, method='pbkdf2:sha256')
    db.session.add(User(username=new_username, password=hashed_pw, role=role))
    db.session.commit()

    if role == 'vendedor':
        flash(f'✅ Vendedor "{new_username}" creado con éxito! (Contraseña: {new_password})')
    else:
        flash(f'✅ Usuario "{new_username}" creado con éxito.')

    redirect_to = 'dev_panel' if session.get('role') == 'dev' else 'admin_users'
    return redirect(url_for(redirect_to))

@app.route('/dev/reset_password/<int:user_id>')
def reset_password(user_id):
    if session.get('role') not in ['dev', 'admin']: return redirect(url_for('login'))
    user = User.query.get(user_id)
    redirect_url = 'dev_panel' if session.get('role') == 'dev' else 'admin_users'
    if not user: return redirect(url_for(redirect_url))

    new_password = f"{user.username}123"
    hashed_pw = generate_password_hash(new_password, method='pbkdf2:sha256')
    user.password = hashed_pw
    db.session.commit()
    flash(f'🔑 Contraseña de "{user.username}" reseteada a: <b>{new_password}</b>')
    return redirect(url_for(redirect_url))

@app.route('/dev/delete_user/<int:user_id>')
def delete_user(user_id):
    if session.get('role') not in ['dev', 'admin']: return redirect(url_for('login'))
    user = User.query.get(user_id)
    redirect_url = 'dev_panel' if session.get('role') == 'dev' else 'admin_users'
    if not user: return redirect(url_for(redirect_url))

    if session.get('role') == 'admin' and user.role != 'vendedor':
        flash('❌ Admin solo puede eliminar Vendedores!')
        return redirect(url_for(redirect_url))

    username = user.username
    db.session.delete(user)
    db.session.commit()
    flash(f'🗑️ Usuario "{username}" eliminado exitosamente')
    return redirect(url_for(redirect_url))

@app.route('/admin/users')
def admin_users():
    if session.get('role') != 'admin': return redirect(url_for('login'))
    return render_template_string(TEMPLATE, users=User.query.all(), theme=Theme)

@app.route('/admin')
def admin_dashboard():
    if session.get('role') not in ['admin', 'vendedor']: return redirect(url_for('login'))
    
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
        total_discount = 0

        for item in items:
            purchases = Purchase.query.filter_by(product_code=item.product_code).all()
            if purchases:
                total_cost_item = sum(p.quantity * p.unit_cost for p in purchases)
                total_qty = sum(p.quantity for p in purchases)
                unit_cost = total_cost_item / total_qty if total_qty > 0 else 0
                total_cost += unit_cost * item.quantity

            # Calcular descuento total
            discount = item.discount if hasattr(item, 'discount') else 0
            total_discount += discount * item.quantity

            # Análisis por producto
            if item.product_code not in product_analysis:
                product = Product.query.filter_by(code=item.product_code).first()
                product_analysis[item.product_code] = {
                    'code': item.product_code,
                    'name': product.name if product else 'Producto Desconocido',
                    'quantity_sold': 0,
                    'total_revenue': 0,
                    'total_cost': 0,
                    'sales_count': 0,
                    'total_discount': 0
                }

            product_analysis[item.product_code]['quantity_sold'] += item.quantity
            product_analysis[item.product_code]['total_revenue'] += item.subtotal
            product_analysis[item.product_code]['sales_count'] += 1
            product_analysis[item.product_code]['total_discount'] += discount * item.quantity

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
            'total_discount': round(total_discount, 2),
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
        # Convertir fecha a datetime
        if isinstance(inv['date'], str):
            day, month, year = map(int, inv['date'].split('/'))
            date_obj = datetime(year, month, day)
        else:
            date_obj = datetime.combine(inv['date'], time.min)
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
        if isinstance(inv['date'], str):
            day, month, year = map(int, inv['date'].split('/'))
        else:
            year = inv['date'].year
            month = inv['date'].month
            day = inv['date'].day
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

    chart_json = json.dumps(chart_data_daily, cls=DateEncoder)
    chart_json_weekly = json.dumps(chart_data_weekly_list, cls=DateEncoder)
    chart_json_monthly = json.dumps(chart_data_monthly_list, cls=DateEncoder)

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
    if session.get('role') not in ['admin', 'vendedor']: return redirect(url_for('login'))
    from datetime import datetime, timedelta

    products = Product.query.all()
    product_data = []

    today = datetime.strptime('2026-09-28', '%Y-%m-%d').date()
    date_15_days_ago = today - timedelta(days=15)
    date_30_days_ago = today - timedelta(days=30)

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
    if session.get('role') not in ['admin', 'vendedor']: return redirect(url_for('login'))
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
        cost_price = float(request.form['cost_price'])
        sale_price = float(request.form['sale_price'])
        initial_quantity = int(request.form.get('initial_quantity', 0) or 0)

        db.session.add(Product(code=code, name=name, category=category, cost_price=cost_price, sale_price=sale_price, min_stock=5, status='ativo'))
        db.session.commit()

        if initial_quantity > 0:
            unit_cost = cost_price / initial_quantity
            db.session.add(Purchase(product_code=code, quantity=initial_quantity, unit_cost=unit_cost, date=date.today()))
            db.session.commit()

        margin = sale_price - cost_price
        flash(f'✅ Producto registrado con éxito! SKU: <b>{code}</b> | Margen: ${margin:.2f} | Stock: {initial_quantity}')
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
    return render_template_string(TEMPLATE, products=products, products_json=json.dumps(products_data, cls=DateEncoder), theme=Theme)

@app.route('/admin/sale', methods=['GET', 'POST'])
def admin_sale():
    if session.get('role') not in ['admin', 'vendedor']: return redirect(url_for('login'))

    if request.method == 'POST':
        from datetime import datetime

        # Obtener vendor_id del usuario actual
        current_user = User.query.filter_by(username=session.get('user')).first()
        vendor_id = current_user.id if current_user else None

        invoice_number = generate_invoice_number()
        date_str = request.form.get('date', datetime.now().strftime('%d/%m/%Y'))
        date_obj = datetime.strptime(date_str, '%d/%m/%Y').date()

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
            discount = float(request.form.get(f'item_{i}_discount', 0))

            if quantity > 0 and unit_price >= 0:
                subtotal = quantity * unit_price
                items.append({
                    'product_code': code,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'discount': discount,
                    'subtotal': subtotal
                })
                total_amount += subtotal

                # Registrar la venta individual con vendor_id
                db.session.add(Sale(date=date_obj, product_code=code, quantity=quantity, unit_price=unit_price, vendor_id=vendor_id))

            i += 1

        if not items:
            flash('❌ El carrito está vacío. Agregue productos antes de vender.')
            return redirect(url_for('admin_sale'))

        # Crear invoice con vendor_id
        invoice = Invoice(invoice_number=invoice_number, date=date_obj, total_amount=total_amount, vendor_id=vendor_id)
        db.session.add(invoice)
        db.session.flush()

        # Crear items de la invoice
        for item in items:
            invoice_item = InvoiceItem(
                invoice_number=invoice_number,
                product_code=item['product_code'],
                quantity=item['quantity'],
                unit_price=item['unit_price'],
                discount=item.get('discount', 0),
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
                                 products_data=json.dumps(products_data, cls=DateEncoder),
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
        product.sale_price = float(request.form['sale_price'])
        quantity_adjustment = int(request.form.get('quantity_adjustment', 0) or 0)

        if quantity_adjustment > 0:
            cost_adjustment_total = float(request.form.get('cost_adjustment_total', 0) or 0)
            unit_cost = cost_adjustment_total / quantity_adjustment if quantity_adjustment > 0 else 0
            db.session.add(Purchase(product_code=code, quantity=quantity_adjustment, unit_cost=unit_cost, date=date.today()))

        db.session.commit()
        msg = f'✅ Producto {code} actualizado correctamente! Costo: ${product.cost_price:.2f} | Venta: ${product.sale_price:.2f}'
        if quantity_adjustment > 0:
            msg += f' | +Stock: {quantity_adjustment}'
        flash(msg)
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

# ==================== VENDEDORES / REPORTE ====================

@app.route('/admin/vendors')
def admin_vendors():
    if session.get('role') != 'admin': return redirect(url_for('login'))

    vendedores = User.query.filter_by(role='vendedor').all()
    vendedor_data = []

    for v in vendedores:
        # Contar ventas por vendedor (asumimos que usuario_id está en tabla sale o invoice)
        # Por ahora: contar todas las ventas del sistema y mostrar por vendedor
        total_sales = db.session.query(db.func.count(Sale.id)).scalar() or 0
        total_value = db.session.query(db.func.sum(Sale.unit_price * Sale.quantity)).scalar() or 0

        vendedor_data.append({
            'username': v.username,
            'user_id': v.id,
            'total_sales': total_sales,
            'total_value': total_value
        })

    return render_template_string(TEMPLATE, vendedor_data=vendedor_data, theme=Theme)

@app.route('/admin/vendor/<int:vendor_id>/sales')
def vendor_sales(vendor_id):
    if session.get('role') != 'admin': return redirect(url_for('login'))

    vendedor = User.query.get(vendor_id)
    if not vendedor or vendedor.role != 'vendedor':
        flash('❌ Vendedor no encontrado')
        return redirect(url_for('admin_vendors'))

    # Obtener todas las ventas del sistema
    sales = Sale.query.all()
    total_sales = len(sales)
    total_value = db.session.query(db.func.sum(Sale.unit_price * Sale.quantity)).scalar() or 0

    return render_template_string(TEMPLATE,
        vendedor=vendedor,
        total_sales=total_sales,
        total_value=total_value,
        theme=Theme)

# ==================== INVENTARIO / AUDITORIA ====================

@app.route('/admin/inventory', methods=['GET', 'POST'])
def admin_inventory():
    if session.get('role') != 'admin': return redirect(url_for('login'))

    if request.method == 'POST':
        count = InventoryCount(count_date=date.today(), user_id=session.get('user_id'))
        db.session.add(count)
        db.session.commit()
        flash(f'Conteo iniciado - ID: {count.id}')
        return redirect(url_for('view_inventory', count_id=count.id))

    counts = InventoryCount.query.order_by(InventoryCount.count_date.desc()).all()
    return render_template_string(TEMPLATE,
                                 page='inventory_list',
                                 counts=counts,
                                 theme=Theme)

@app.route('/admin/inventory/<int:count_id>', methods=['GET', 'POST'])
def view_inventory(count_id):
    if session.get('role') != 'admin': return redirect(url_for('login'))

    count = InventoryCount.query.get_or_404(count_id)
    items = InventoryCountItem.query.filter_by(inventory_count_id=count_id).all()
    products = Product.query.all()

    total_variance = sum(item.variance for item in items)
    total_loss = sum(abs(item.variance) for item in items if item.variance_type == 'FALTA')

    if request.method == 'POST':
        action = request.form.get('action', 'add')

        if action == 'update_reason':
            item_id = request.form.get('item_id')
            loss_reason = request.form.get('loss_reason', '')
            notes = request.form.get('notes', '')
            item = InventoryCountItem.query.get_or_404(item_id)
            item.loss_reason = loss_reason
            item.notes = notes
            item.status = 'resuelto'
            db.session.commit()
            flash(f'Motivo actualizado para {item.product_code}')
            return redirect(url_for('view_inventory', count_id=count_id))

        code = request.form.get('product_code')
        physical_count = int(request.form.get('physical_count', 0))
        loss_reason = request.form.get('loss_reason', '')
        notes = request.form.get('notes', '')

        product = Product.query.filter_by(code=code).first()
        if not product:
            flash('Producto no encontrado')
            return redirect(url_for('view_inventory', count_id=count_id))

        # Calcular stock real del sistema (compras - ventas)
        purchases = Purchase.query.filter_by(product_code=code).with_entities(func.sum(Purchase.quantity)).scalar() or 0
        sales = Sale.query.filter_by(product_code=code).with_entities(func.sum(Sale.quantity)).scalar() or 0
        system_quantity = purchases - sales

        existing = InventoryCountItem.query.filter_by(
            inventory_count_id=count_id,
            product_code=code
        ).first()

        variance = physical_count - system_quantity
        variance_type = 'FALTA' if variance < 0 else ('EXCESO' if variance > 0 else 'OK')

        # Si no hay motivo y hay falta, status es "analisis"
        status = 'resuelto' if (loss_reason or variance_type != 'FALTA') else 'analisis'

        if existing:
            existing.physical_count = physical_count
            existing.variance = variance
            existing.variance_type = variance_type
            existing.loss_reason = loss_reason
            existing.notes = notes
            existing.status = status
        else:
            item = InventoryCountItem(
                inventory_count_id=count_id,
                product_code=code,
                system_quantity=system_quantity,
                physical_count=physical_count,
                variance=variance,
                variance_type=variance_type,
                loss_reason=loss_reason,
                notes=notes,
                status=status
            )
            db.session.add(item)

        db.session.commit()
        flash(f'Producto {code} agregado a conteo')
        return redirect(url_for('view_inventory', count_id=count_id))

    # Calcular stock para cada producto
    products_with_stock = []
    for p in products:
        purchases = Purchase.query.filter_by(product_code=p.code).with_entities(func.sum(Purchase.quantity)).scalar() or 0
        sales = Sale.query.filter_by(product_code=p.code).with_entities(func.sum(Sale.quantity)).scalar() or 0
        system_stock = purchases - sales
        products_with_stock.append({
            'code': p.code,
            'name': p.name,
            'system_stock': system_stock
        })

    return render_template_string(TEMPLATE,
                                 page='inventory_detail',
                                 count=count,
                                 items=items,
                                 products=products,
                                 products_json=json.dumps(products_with_stock, cls=DateEncoder),
                                 total_variance=total_variance,
                                 total_loss=total_loss,
                                 theme=Theme)

@app.route('/admin/inventory/<int:count_id>/remove/<item_id>')
def remove_inventory_item(count_id, item_id):
    if session.get('role') != 'admin': return redirect(url_for('login'))

    item = InventoryCountItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Item removido del conteo')
    return redirect(url_for('view_inventory', count_id=count_id))

@app.route('/admin/inventory/<int:count_id>/finalize')
def finalize_inventory(count_id):
    if session.get('role') != 'admin': return redirect(url_for('login'))

    count = InventoryCount.query.get_or_404(count_id)
    items = InventoryCountItem.query.filter_by(inventory_count_id=count_id).all()

    total_variance = sum(item.variance for item in items)
    total_loss = sum(abs(item.variance) for item in items if item.variance_type == 'FALTA')

    count.status = 'finalizado'
    count.total_variance = total_variance
    count.total_loss = total_loss
    db.session.commit()

    flash(f'Conteo finalizado. Perdida total: {total_loss} unidades')
    return redirect(url_for('view_inventory', count_id=count_id))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_ENV') != 'production'
    port = int(os.getenv('PORT', 5000))
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
