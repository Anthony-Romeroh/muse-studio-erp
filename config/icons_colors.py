class Theme:
    # Logo e Branding
    LOGO = {
        'path': '/static/images/muse_logo.jpg',
        'alt': 'Muse Studio - Tu mayorista online',
        'width': '120px',
        'height': '120px',
    }

    BRAND = {
        'name': 'Muse Studio',
        'tagline': 'Tu mayorista online',
        'description': 'Beauty • Makeup • Accessories',
    }

    # Cores principais
    COLORS = {
        'primary': '#FF6B9D',      # Rosa/Pink
        'secondary': '#000000',    # Preto
        'warning': '#FFC107',      # Amarelo
        'dark': '#1a1a1a',         # Cinza escuro
        'light': '#f5f5f5',        # Cinza claro
        'success': '#4CAF50',      # Verde
        'danger': '#f44336',       # Vermelho
        'info': '#2196F3',         # Azul
    }

    # Ícones para menu rápido (Flujo Operativo)
    QUICK_ACCESS = {
        'venta': {
            'icon': '🛍️',
            'label': '1. Venta',
            'color': COLORS['primary'],
            'route': 'sales'
        },
        'catalogo': {
            'icon': '📦',
            'label': '2. Catálogo',
            'color': COLORS['secondary'],
            'route': 'catalog'
        },
        'nuevo': {
            'icon': '➕',
            'label': '3. Nuevo',
            'color': COLORS['warning'],
            'route': 'new_product'
        },
        'entrada': {
            'icon': '📥',
            'label': '4. Entrada',
            'color': COLORS['dark'],
            'route': 'entry'
        }
    }

    # Ícones para navegação
    NAV_ICONS = {
        'dashboard': '📊',
        'products': '📦',
        'sales': '💰',
        'purchases': '🛒',
        'inventory': '📦',
        'admin': '⚙️',
        'dev': '💻',
        'logout': '🚪',
    }

    # Status de alertas
    ALERTS = {
        'success': '✅',
        'warning': '⚠️',
        'error': '❌',
        'info': 'ℹ️',
    }

    # Cards de status
    CARD_STYLES = {
        'active_products': {
            'icon': '📦',
            'color': COLORS['primary'],
            'bg_color': '#FFE8F0',
        },
        'low_stock': {
            'icon': '⚠️',
            'color': COLORS['danger'],
            'bg_color': '#FFEBEE',
        },
        'inventory_value': {
            'icon': '💵',
            'color': COLORS['warning'],
            'bg_color': '#FFF8E1',
        }
    }

    # Ícones para operaciones
    OPERATIONS = {
        'entrada': '📥',
        'salida': '📤',
        'venta': '🛍️',
        'compra': '🛒',
        'historial': '📊',
        'manual': '💬',
        'promedio': '📊',
        'ultima': '📅',
    }

    # Ícones para acciones
    ACTIONS = {
        'guardar': '💾',
        'cancelar': '❌',
        'eliminar': '🗑️',
        'activar': '🟢',
        'desactivar': '🔴',
        'editar': '✏️',
        'confirmar': '✅',
        'buscar': '🔍',
        'filtrar': '⚙️',
    }

    # Ícones informativos
    INFORMATION = {
        'codigo': '📌',
        'nombre': '📝',
        'cantidad': '📊',
        'precio': '💰',
        'stock': '📦',
        'costo': '💵',
        'fecha': '📅',
        'estado': '🔔',
        'activo': '✓',
        'inactivo': '✗',
    }
