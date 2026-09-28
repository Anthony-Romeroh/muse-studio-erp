# 🎀 Muse Studio ERP - Sistema de Gestión Integral

Sistema ERP completo para **Muse Studio** - Mayorista Online de Belleza, Makeup & Accesorios. Diseñado con mobile-first responsive design y seguimiento de vendedores.

---

## ✨ Features Principales

### 🛒 Punto de Venta (POS) - Mobile First
- Carrinho de compras dinámico fullscreen
- **Editar cantidad en carrito** - Sin límite de stock
- Búsqueda rápida de productos por nombre/código
- Generación automática de facturas (NF)
- Cálculo automático de totales con descuentos
- **Rastreo de vendedor** (vendor_id) en cada venta
- **Responsive design:** Mobile (1 col) / Desktop (2-3 cols)
- Layout adaptativo con media queries

### 📦 Gestión de Inventário
- SKU automático (MS-000001, MS-000002...)
- Stock en tiempo real con cálculo dinámico
- **Editar cantidad en catálogo** - Ajustar stock directamente
- **Cantidad inicial al crear producto** - Cargar estoque desde el inicio
- Editar precios de costo y venta en catálogo
- Costo promedio de productos
- Estados: Ativo / Inactivo
- Alertas de stock bajo
- Historial de compras por producto

### 👥 Gestión de Usuarios (Roles)
- **Dev:** Acceso total a panel administrativo
- **Admin:** Gestión de vendedores, dashboard, reportes
- **Vendedor:** Acceso directo a POS para realizar ventas
- Crear/editar/eliminar usuarios
- Reset de contraseña automático

### 📊 Análisis de Vendas
- Gráficos de tendencias (Chart.js)
- Vistas: Diario, Semanal, Mensual
- Top productos por ganancia
- Análisis por vendedor (vendor_id)
- Filtro por rango de fechas
- Margen de ganancia por producto

### 💰 Dashboard Ejecutivo
- KPIs principales en tiempo real
- Total de productos en stock
- Valor total del inventário
- Alertas de stock bajo
- Margen de ganancia promedio

### 📋 Guía de Precios
- Histórico de vendas últimos 15/30 días
- Precio promedio de venta
- Cantidad vendida por período
- Tendencias de precios

---

## 🚀 Quick Start - Desarrollo Local

### Requisitos
- Python 3.8+
- Git
- pip

### Instalación

```bash
git clone https://github.com/Anthony-Romeroh/muse-studio-erp.git
cd muse_studio_erp
pip install -r requirements.txt
python app.py
```

Abre: `http://localhost:5000`

### Base de Datos Local (SQLite)

El proyecto viene pre-configurado con SQLite y se crea automáticamente al iniciar.

---

## 🔐 Credenciales de Prueba

| Usuario | Contraseña | Rol | Acceso |
|---------|-----------|-----|--------|
| dev | dev123 | Dev | Panel administrativo completo |
| admin | admin123 | Admin | Dashboard + gestión de vendedores |
| vendedor | vendedor123 | Vendedor | Punto de Venta (POS) |

---

## 📊 Datos Iniciales

- **13 Productos:** Accesorios para belleza (coletas, tiburones, cintillos, etc.)
- **109 Unidades:** Stock inicial
- **$87,500:** Valor total del inventário al costo

---

## 📱 Acceso Remoto (Mobile)

### IP Local (Mismo WiFi)
```
http://192.168.X.X:5000/admin
```

### VS Code Port Forwarding
1. Abre VS Code → PORTS tab
2. Forward port 5000
3. Copia el link → Abre en celular

---

## 🌍 Deployment - Vercel + Supabase (Producción)

### 1. Restaurar Base de Datos Supabase

En Supabase Dashboard SQL Editor:

```sql
1. Abre: https://supabase.com/dashboard → tu proyecto
2. SQL Editor → New Query
3. Copia TODO de: supabase_restore_complete.sql
4. RUN
```

**Esto crea:** 8 tablas + 3 usuarios + 13 productos + 109 unidades de stock

### 2. Configurar Variables de Entorno

Crea `.env.production` (o actualiza en Vercel):

```env
FLASK_ENV=production
SECRET_KEY=tu-clave-secreta
DATABASE_URL=postgresql://user:password@host/database
```

### 3. Deploy a Vercel

```bash
vercel --prod
```

O vincula GitHub → Vercel (auto-deploy en cada push)

---

## 📈 URLs Principales

### Desarrollo Local
- **Dashboard:** http://localhost:5000/admin
- **POS:** http://localhost:5000/admin/sale
- **Catálogo:** http://localhost:5000/admin/catalog
- **Análisis:** http://localhost:5000/admin/sales-history
- **Guía Precios:** http://localhost:5000/admin/price-guide
- **Gestión Usuarios:** http://localhost:5000/admin/users
- **Cash Flow:** http://localhost:5000/admin/cash-flow

### Producción (Vercel)
- Acceso en: `https://muse-studio-erp.vercel.app`

---

## 💻 Stack Tecnológico

| Componente | Tecnología |
|-----------|-----------|
| Backend | Flask (Python) |
| Base de Datos | SQLite (dev) / PostgreSQL (prod) |
| ORM | SQLAlchemy |
| Frontend | HTML5 + CSS3 + Vanilla JS |
| Gráficos | Chart.js |
| Responsive | Mobile-First + Media Queries |
| Servidor | Gunicorn (Vercel) |
| Hosting | Vercel + Supabase |

---

## 🎨 Diseño & UX

- **Mobile-First:** Optimizado para celular primero
- **Responsive:** Funciona en todos los dispositivos
- **Tema:** Dark header + White content + Pink/Gold accents
- **Fuentes:** Responsive con `clamp()` para escalado fluido
- **Accesibilidad:** Botones grandes (min-height 2.5rem - 3.5rem)

---

## 📁 Estructura del Proyecto

```
muse-studio-erp/
├── app.py                         # Aplicación Flask principal
├── models.py                      # Modelos SQLAlchemy
├── database.py                    # Inicialización de BD
├── utils.py                       # Funciones utilitarias
├── wsgi.py                        # Entrada para Vercel
├── config/
│   └── icons_colors.py            # Tema y configuración visual
├── requirements.txt               # Dependencias Python
├── .env                           # Variables de entorno
├── supabase_restore_complete.sql  # Script de restauración BD (IMPORTANTE)
└── README.md                      # Este archivo
```

---

## 🔄 Workflow de Desarrollo

```
1. Editar código en local
2. Probar en http://localhost:5000
3. git add -A && git commit -m "descripción"
4. git push origin main
5. ✅ Auto-deploy en Vercel
```

---

## 🐛 Troubleshooting

### "Error 500 en /admin/sale, /admin/catalog, etc."
**Solución:** Restaura el BD en Supabase usando `supabase_restore_complete.sql`
```
1. Abre Supabase SQL Editor
2. Copia TODA la SQL del archivo
3. RUN
4. Redeploy en Vercel
```

### "Database URL inválido en producción"
- Verifica Vercel → Settings → Environment Variables
- `DATABASE_URL` debe ser: `postgresql://user:password@host:5432/database`

### "Puerto 5000 en uso localmente"
- Cambia en `.env`: `PORT=5001` (o cualquier puerto libre)
- Reinicia: `python app.py`

---

## 📝 Licencia

Privado - Derechos reservados Muse Studio

---

## 👨‍💻 Autor

Desarrollado por Anthony Hernández  
Email: anthonyhernandez@bemol.com.br

**Made with ❤️ para Muse Studio** 🎀
