"""
Script para carregar novo inventário com 0 vendas
Data: Hoje (27/09/2026)
"""
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from database import db
from models import Product, Purchase
from app import app
from utils import generate_sku

# Dados do novo inventário
NOVO_INVENTARIO = [
    ('COLET PANTY BEBE INDIVIDUAL', 24, 300),
    ('TIBURON RECTANGULO DOUBLE AGARRE COLOR', 2, 3600),
    ('TICTAC ESTRELLA G COLOR 1', 18, 700),
    ('TIC TAC PUNTO + CUADRILLE', 18, 400),
    ('PINZA 6/3 DIFT', 18, 700),
    ('COLET PANTY MEDIANO CON CARTON', 6, 1500),
    ('CINTILLO NUDO SURTIDO AZUL', 1, 4800),
    ('TIBURON ENGOMADO RECTANGULAR', 2, 3600),
    ('SET CINTILLO SPA + HAWAI', 4, 1400),
    ('TIBURON RECTANGULO NEGRO 4CM', 1, 1500),
    ('TIRA MARIPOSA CHICA', 2, 1500),
    ('TIBURON METAL MEDIANO CUADRADO', 1, 3600),
    ('COLET TRENZA TUBO', 12, 500),
]

def load_new_inventory():
    with app.app_context():
        print("🗑️  Limpando dados anteriores...")

        # Eliminar todos los productos, compras y ventas anteriores
        Product.query.delete()
        Purchase.query.delete()
        db.session.commit()

        print("✅ Datos anteriores eliminados")

        print("\n📦 Carregando novo inventário...")
        print(f"   Data: 27/09/2026")
        print(f"   Quantidade de produtos: {len(NOVO_INVENTARIO)}")

        today = datetime.now().strftime('%d/%m/%Y')
        total_value = 0

        for nombre, cantidad, precio_unitario in NOVO_INVENTARIO:
            # Generar SKU automático
            sku = generate_sku()

            # Crear producto
            product = Product(
                code=sku,
                name=nombre.upper(),
                category='ACCESORIOS',
                cost_price=precio_unitario,
                sale_price=0,
                min_stock=5,
                status='ativo'
            )
            db.session.add(product)
            db.session.flush()

            # Crear compra (entrada de inventário)
            purchase = Purchase(
                date=today,
                product_code=sku,
                quantity=cantidad,
                unit_cost=precio_unitario
            )
            db.session.add(purchase)

            total_value += cantidad * precio_unitario

            print(f"   ✓ {sku} - {nombre.upper()}: {cantidad} un × $ {precio_unitario:,}")

        db.session.commit()

        print(f"\n✅ Novo inventário carregado com sucesso!")
        print(f"\n📊 Resumo:")
        print(f"   • Produtos: {len(NOVO_INVENTARIO)}")
        print(f"   • Quantidade Total: {sum(q for _, q, _ in NOVO_INVENTARIO)} unidades")
        print(f"   • Valor Total: $ {total_value:,}")
        print(f"   • Vendas: 0 (Stock = Inventário)")
        print(f"\n🎯 Acesse: http://127.0.0.1:5000/admin")

if __name__ == '__main__':
    load_new_inventory()
