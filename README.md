# 🎀 Muse Studio ERP

Sistema ERP completo para **Muse Studio** - Mayorista de Belleza & Accesorios.

## ✨ Features

### 🛒 Punto de Venta (POS)
- Carrinho de compras dinâmico
- Búsqueda rápida de productos
- Generación automática de NF
- Cálculo automático de totales
- exS
### 📦 Gestión de Inventário
- SKU automático (MS-000001, MS-000002...)
- Stock en tiempo real
- Costo promedio de productos
- Estado: Ativo/Inactivo

### 📊 Análisis de Vendas
- Gráficos de tendencias
- Vistas: Diario, Semanal, Mensual
- Top productos por ganancia
- Exportar a Excel
- Filtro por rango de fechas

### 💰 Dashboard
- KPIs principales
- Alertas de stock bajo
- Margen de ganancia promedio

## 📱 Acceso desde Celular

### IP Local (Mismo WiFi)
\\\
http://192.168.1.XXX:5000/admin
\\\

### VS Code Port Forwarding
1. Abre VS Code
2. PORTS tab → Digita 5000
3. Copia el link generado
4. Abre en tu celular

## 🚀 Instalación

\\\ash
git clone https://github.com/USUARIO/muse-studio-erp.git
cd muse_studio_erp
pip install -r requirements.txt
python app.py
\\\

## 🔐 Login

- **Usuario:** admin
- **Contraseña:** admin123

## 📊 Estoque Inicial

- **13 Productos** cadastrados
- **109 Unidades** en total
- **\$ 87,500** valor total
- **0 Vendas** (listo para empezar)

## 📈 URLs Principales

- Dashboard: http://localhost:5000/admin
- POS: http://localhost:5000/admin/sale
- Catálogo: http://localhost:5000/admin/catalog
- Análisis: http://localhost:5000/admin/sales-history

## 💻 Tecnologías

- Flask, SQLAlchemy, Chart.js, XLSX.js

---

**Made with ❤️ para Muse Studio**
