"""
Script para limpar TUDO e cadastrar apenas a nota de estoque
Data: 27/09/2026
"""
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from database import db
from models import Product, Purchase, Sale, Invoice, InvoiceItem
from app import app
from utils import generate_sku

# Dados do inventário da nota
NOTA_ESTOQUE = [
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

def clean_and_load():
    with app.app_context():
        print("🔥 LIMPANDO TUDO...")

        # Eliminar todos los datos
        print("   • Eliminando ventas...")
        InvoiceItem.query.delete()
        Invoice.query.delete()
        Sale.query.delete()

        print("   • Eliminando compras...")
        Purchase.query.delete()

        print("   • Eliminando productos...")
        Product.query.delete()

        db.session.commit()

        print("✅ BANCO DE DATOS LIMPIO\n")

        print("📦 CADASTRANDO NOTA DE ESTOQUE...")
        print(f"   Data: 27/09/2026")
        print(f"   Quantidade de produtos: {len(NOTA_ESTOQUE)}\n")

        today = '27/09/2026'
        total_value = 0

        for nombre, cantidad, precio_unitario in NOTA_ESTOQUE:
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

            # Crear entrada de compra (inventário)
            purchase = Purchase(
                date=today,
                product_code=sku,
                quantity=cantidad,
                unit_cost=precio_unitario
            )
            db.session.add(purchase)

            total_value += cantidad * precio_unitario

            print(f"   ✓ {sku} - {nombre.upper()}")
            print(f"      Cantidad: {cantidad} unidades × $ {precio_unitario:,} = $ {cantidad * precio_unitario:,}\n")

        db.session.commit()

        print("="*60)
        print("✅ NOTA DE ESTOQUE CADASTRADA COM SUCESSO!")
        print("="*60)
        print(f"\n📊 RESUMO FINAL:")
        print(f"   • Produtos cadastrados: {len(NOTA_ESTOQUE)}")
        print(f"   • Quantidade total: {sum(q for _, q, _ in NOTA_ESTOQUE)} unidades")
        print(f"   • Valor total: $ {total_value:,}")
        print(f"   • Vendas registradas: 0")
        print(f"   • Stock disponível: 100% (sem vendas)")
        print(f"\n🎯 Acesse:")
        print(f"   • Catálogo: http://127.0.0.1:5000/admin/catalog")
        print(f"   • Dashboard: http://127.0.0.1:5000/admin")
        print(f"   • Vendas: http://127.0.0.1:5000/admin/sale")

if __name__ == '__main__':
    clean_and_load()
