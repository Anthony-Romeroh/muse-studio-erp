#!/usr/bin/env python
"""
Script para carregar estoque de produtos a partir da imagem
"""
from datetime import date
from dotenv import load_dotenv
from app import app, db
from models import Product, Purchase

load_dotenv()

# Dados extraídos da imagem
stock_data = [
    {'code': 'MS-COLET-BEBE-300', 'name': 'Colet Panty Bebe Individual', 'category': 'Accesorios', 'cost': 300.0, 'price': 1100.0, 'qty': 24},
    {'code': 'MS-TIBURON-DOUBLE-3600', 'name': 'Tiburon Rectangular Double Agarre Color', 'category': 'Accesorios', 'cost': 3600.0, 'price': 12000.0, 'qty': 2},
    {'code': 'MS-TICTAC-ESTRELLA-700', 'name': 'Tictac Estrella G Color 1', 'category': 'Accesorios', 'cost': 700.0, 'price': 12600.0, 'qty': 18},
    {'code': 'MS-TICTAC-PUNTO-400', 'name': 'Tic Tac Punto + Cuadrille', 'category': 'Accesorios', 'cost': 400.0, 'price': 7200.0, 'qty': 18},
    {'code': 'MS-PINZA-DIFT-700', 'name': 'Pinza 6/3 DIFT', 'category': 'Accesorios', 'cost': 700.0, 'price': 12600.0, 'qty': 18},
    {'code': 'MS-COLET-MEDIANO-1500', 'name': 'Colet Panty Mediano Con Carton', 'category': 'Accesorios', 'cost': 1500.0, 'price': 9000.0, 'qty': 6},
    {'code': 'MS-CINILLO-AZUL-4800', 'name': 'Cinillo Nudo Surtido Azul', 'category': 'Accesorios', 'cost': 4800.0, 'price': 4800.0, 'qty': 1},
    {'code': 'MS-TIBURON-ENGOMADO-3600', 'name': 'Tiburon Engomado Rectangular', 'category': 'Accesorios', 'cost': 3600.0, 'price': 7200.0, 'qty': 2},
    {'code': 'MS-SET-CINTILLO-SPA-1400', 'name': 'Set Cintillo Spa + Hawai', 'category': 'Accesorios', 'cost': 1400.0, 'price': 5600.0, 'qty': 4},
    {'code': 'MS-TIBURON-NEGRO-1500', 'name': 'Tiburon Rectangular Negro 4cm', 'category': 'Accesorios', 'cost': 1500.0, 'price': 1500.0, 'qty': 1},
    {'code': 'MS-TIRA-MARIPOSA-1500', 'name': 'Tira Mariposa Chica', 'category': 'Accesorios', 'cost': 1500.0, 'price': 3000.0, 'qty': 2},
    {'code': 'MS-TIBURON-METAL-3600', 'name': 'Tiburon Metal Mediano Cuadrado', 'category': 'Accesorios', 'cost': 3600.0, 'price': 3600.0, 'qty': 1},
    {'code': 'MS-COLET-TRENZA-500', 'name': 'Colet Trenza Tubo', 'category': 'Accesorios', 'cost': 500.0, 'price': 6000.0, 'qty': 12},
]

def load_stock():
    with app.app_context():
        print("Cargando estoque de productos...")

        # Crear productos si no existen
        created = 0
        for item in stock_data:
            existing = Product.query.filter_by(code=item['code']).first()
            if not existing:
                p = Product(
                    code=item['code'],
                    name=item['name'],
                    category=item['category'],
                    cost_price=item['cost'],
                    sale_price=item['price'],
                    min_stock=1,
                    status='ativo'
                )
                db.session.add(p)
                created += 1

        db.session.commit()
        print(f"OK - {created} productos creados!")

        # Registrar compra
        print("Registrando entrada de estoque...")
        today = date.today()

        purchase_count = 0
        for item in stock_data:
            purchase = Purchase(
                date=today,
                product_code=item['code'],
                quantity=item['qty'],
                unit_cost=item['cost']
            )
            db.session.add(purchase)
            purchase_count += 1

        db.session.commit()
        print(f"OK - {purchase_count} items de estoque registrados!")

        # Resumen
        total_cost = sum(item['cost'] * item['qty'] for item in stock_data)
        total_items = sum(item['qty'] for item in stock_data)

        print("\n" + "="*60)
        print("RESUMEN DE ESTOQUE CARGADO")
        print("="*60)
        print(f"Fecha: {today}")
        print(f"Total de productos: {len(stock_data)}")
        print(f"Total de items: {total_items}")
        print(f"Costo total: $ {total_cost:,.2f}")
        print("="*60)

if __name__ == '__main__':
    load_stock()
