"""
Script para vender 30% do estoque da NF de Casa Matriz (29/08/2026)
Carrega os dados reales da fatura compartilhada e cria vendas
"""
import os
import sys
from datetime import datetime, timedelta
import random

sys.path.insert(0, os.path.dirname(__file__))

from database import db
from models import Product, Purchase, Invoice, InvoiceItem, Sale
from app import app
from utils import generate_invoice_number

# Dados da NF original (Casa Matriz 29/08/2026)
PRODUCTOS_NF = [
    ('MS-000001', 'COLET PANTY BEBE INDIVIDUAL', 30, 49.99),
    ('MS-000002', 'TIBURON RECTANGULO DOUBLE AGARRE COLOR', 25, 79.99),
    ('MS-000003', 'HILADO LYCRA LARGO', 20, 39.99),
    ('MS-000004', 'PANTY LYCRA LARGO CONFOR', 35, 44.99),
    ('MS-000005', 'COLET PANTY BEBE BLANCO CAJA', 28, 54.99),
    ('MS-000006', 'TIBURON DOBLE AGARRE LARGO', 22, 74.99),
    ('MS-000007', 'HILADO CLASICO CORTO', 40, 34.99),
    ('MS-000008', 'PANTY PREMIUM LYCRA', 18, 59.99),
    ('MS-000009', 'COLET BEBE DOBLE AGARRE', 32, 49.99),
    ('MS-000010', 'TIBURON CLASICO RECTANGULAR', 26, 69.99),
    ('MS-000011', 'HILADO LYCRA CORTO PREMIUM', 19, 44.99),
    ('MS-000012', 'PANTY CLASICO LARGO', 38, 39.99),
    ('MS-000013', 'COLET PREMIUM INDIVIDUAL AGARRE', 24, 59.99),
]

def load_nf_sales():
    with app.app_context():
        print("📦 Carregando estoque de la NF de Casa Matriz (29/08/2026)...")

        # Obtener todos los productos
        products = Product.query.all()
        product_dict = {p.code: p for p in products}

        # Calcular 30% del estoque para vender
        sales_data = []

        for sku, nombre, cantidad_nf, precio in PRODUCTOS_NF:
            product = product_dict.get(sku)
            if product:
                # 30% del stock de la NF
                cantidad_vender = max(1, int(cantidad_nf * 0.30))

                # Obtener precio promedio de venta (con margen 30-50%)
                purchases = Purchase.query.filter_by(product_code=sku).all()
                if purchases:
                    total_cost = sum(p.quantity * p.unit_cost for p in purchases)
                    total_qty = sum(p.quantity for p in purchases)
                    avg_cost = total_cost / total_qty if total_qty > 0 else precio
                else:
                    avg_cost = precio

                # Precio de venta con margen 30-45%
                margin = random.uniform(0.30, 0.45)
                unit_price = round(avg_cost * (1 + margin), 2)

                sales_data.append({
                    'code': sku,
                    'name': nombre,
                    'cantidad_vender': cantidad_vender,
                    'unit_price': unit_price
                })

        print(f"\n📊 Vendiendo 30% del estoque de {len(sales_data)} productos:")

        # Crear ventas distribuidas en varios días (desde 30/08 hasta 15/09)
        base_date = datetime.strptime('2026-08-30', '%Y-%m-%d')

        for day_offset in range(17):  # 17 días
            sale_date = (base_date + timedelta(days=day_offset)).strftime('%d/%m/%Y')

            # 1-3 facturas por día
            num_invoices = random.randint(1, 3)

            for _ in range(num_invoices):
                invoice_number = generate_invoice_number()

                # Seleccionar 1-4 productos aleatorios
                num_items = random.randint(1, 4)
                selected_items = random.sample(sales_data, min(num_items, len(sales_data)))

                total_amount = 0
                items = []

                for item in selected_items:
                    # 20-80% de lo que se planeó vender
                    qty = max(1, int(item['cantidad_vender'] * random.uniform(0.20, 0.80)))
                    subtotal = item['unit_price'] * qty
                    total_amount += subtotal

                    items.append({
                        'code': item['code'],
                        'quantity': qty,
                        'unit_price': item['unit_price'],
                        'subtotal': subtotal
                    })

                    # Registrar en tabla Sale
                    sale = Sale(
                        date=sale_date,
                        product_code=item['code'],
                        quantity=qty,
                        unit_price=item['unit_price']
                    )
                    db.session.add(sale)

                # Crear Invoice
                invoice = Invoice(
                    invoice_number=invoice_number,
                    date=sale_date,
                    total_amount=round(total_amount, 2)
                )
                db.session.add(invoice)
                db.session.flush()

                # Crear InvoiceItems
                for item in items:
                    invoice_item = InvoiceItem(
                        invoice_number=invoice_number,
                        product_code=item['code'],
                        quantity=item['quantity'],
                        unit_price=item['unit_price'],
                        subtotal=item['subtotal']
                    )
                    db.session.add(invoice_item)

        db.session.commit()

        print("\n✅ ¡Vendas de 30% do estoque criadas com sucesso!")
        print(f"\n📈 Resumo:")
        print(f"   • Período: 30/08/2026 até 15/09/2026 (17 dias)")
        print(f"   • Produtos: {len(sales_data)} itens")

        # Calcular totais
        total_qty_sold = 0
        total_revenue = 0
        for item in sales_data:
            total_qty_sold += item['cantidad_vender']

        invoices = Invoice.query.all()
        total_revenue = sum(inv.total_amount for inv in invoices)

        print(f"   • Quantidade total: {total_qty_sold} unidades")
        print(f"   • Faturamento total: R$ {total_revenue:.2f}")
        print(f"\n🎯 Ve a: http://127.0.0.1:5000/admin/sales-history")

if __name__ == '__main__':
    load_nf_sales()
