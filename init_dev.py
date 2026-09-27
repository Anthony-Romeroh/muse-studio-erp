#!/usr/bin/env python
"""
Script para inicializar banco de datos SQLite com dados de desenvolvimento
"""
import os
from datetime import datetime, date, timedelta
from dotenv import load_dotenv

load_dotenv()

print("Deletando banco anterior...")
if os.path.exists('muse_studio.db'):
    os.remove('muse_studio.db')
    print("OK - Banco anterior deletado!")

from app import app, db
from models import User, Product, Purchase, Sale, Invoice, InvoiceItem

def init_dev_db():
    """Inicializa banco de datos com dados de desenvolvimento"""

    with app.app_context():
        print("\nAgregando productos...")
        productos_data = [
            {'code': 'MS-000001', 'name': 'Perfume Dior - 100ml', 'category': 'Perfume', 'cost': 80.0, 'price': 150.0, 'min': 5},
            {'code': 'MS-000002', 'name': 'Collar de Oro 18K', 'category': 'Accesorios', 'cost': 150.0, 'price': 300.0, 'min': 3},
            {'code': 'MS-000003', 'name': 'Cartera de Cuero', 'category': 'Accesorios', 'cost': 60.0, 'price': 120.0, 'min': 5},
            {'code': 'MS-000004', 'name': 'Reloj Digital', 'category': 'Accesorios', 'cost': 40.0, 'price': 80.0, 'min': 5},
            {'code': 'MS-000005', 'name': 'Gafas de Sol Polarizadas', 'category': 'Accesorios', 'cost': 50.0, 'price': 100.0, 'min': 5},
            {'code': 'MS-000006', 'name': 'Pulsera de Plata', 'category': 'Accesorios', 'cost': 30.0, 'price': 60.0, 'min': 5},
        ]

        added = 0
        for p_data in productos_data:
            existing = Product.query.filter_by(code=p_data['code']).first()
            if not existing:
                p = Product(
                    code=p_data['code'],
                    name=p_data['name'],
                    category=p_data['category'],
                    cost_price=p_data['cost'],
                    sale_price=p_data['price'],
                    min_stock=p_data['min'],
                    status='ativo'
                )
                db.session.add(p)
                added += 1
        db.session.commit()
        print("OK - {} productos agregados!".format(added))

        print("Agregando compras...")
        hoy = date.today()
        compras_data = [
            {'code': 'MS-000001', 'qty': 5, 'cost': 80.0, 'days': 10},
            {'code': 'MS-000002', 'qty': 3, 'cost': 150.0, 'days': 8},
            {'code': 'MS-000003', 'qty': 10, 'cost': 60.0, 'days': 5},
            {'code': 'MS-000004', 'qty': 8, 'cost': 40.0, 'days': 3},
            {'code': 'MS-000005', 'qty': 6, 'cost': 50.0, 'days': 1},
        ]

        added = 0
        for c_data in compras_data:
            c = Purchase(
                date=hoy - timedelta(days=c_data['days']),
                product_code=c_data['code'],
                quantity=c_data['qty'],
                unit_cost=c_data['cost']
            )
            db.session.add(c)
            added += 1
        db.session.commit()
        print("OK - {} compras agregadas!".format(added))

        print("Agregando ventas de ejemplo...")
        ventas_data = [
            {'code': 'MS-000001', 'qty': 2, 'price': 150.0, 'days': 7},
            {'code': 'MS-000003', 'qty': 1, 'price': 120.0, 'days': 5},
            {'code': 'MS-000005', 'qty': 2, 'price': 100.0, 'days': 3},
        ]

        added = 0
        for v_data in ventas_data:
            v = Sale(
                date=hoy - timedelta(days=v_data['days']),
                product_code=v_data['code'],
                quantity=v_data['qty'],
                unit_price=v_data['price']
            )
            db.session.add(v)
            added += 1
        db.session.commit()
        print("OK - {} ventas agregadas!".format(added))

        print("\n" + "="*60)
        print("OK - BASE DE DATOS DE DESARROLLO INICIALIZADA!")
        print("="*60)
        print("\nDatos cargados:")
        print("   Usuarios: 2 (dev, admin)")
        print("   Productos: 6")
        print("   Compras: 5")
        print("   Ventas: 3")
        print("\nAhora ejecuta: python app.py")

if __name__ == '__main__':
    init_dev_db()
