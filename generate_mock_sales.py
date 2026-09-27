"""
Script para generar ventas mocadas de los productos cadastrados
Usa los 13 productos de Casa Matriz y crea ventas realistas
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

def generate_mock_sales():
    with app.app_context():
        # Obtener todos los productos
        products = Product.query.all()

        if not products:
            print("❌ No hay productos cadastrados. Ejecuta load_fatura.py primero.")
            return

        print(f"📦 Encontrados {len(products)} productos")

        # Crear ventas para los últimos 15 días
        base_date = datetime.strptime('2026-09-27', '%Y-%m-%d')

        for day_offset in range(15):
            sale_date = (base_date - timedelta(days=day_offset)).strftime('%d/%m/%Y')

            # Generar 2-5 facturas por día
            num_invoices = random.randint(2, 5)

            for _ in range(num_invoices):
                invoice_number = generate_invoice_number()

                # Seleccionar 1-4 productos aleatorios
                num_products = random.randint(1, 4)
                selected_products = random.sample(products, min(num_products, len(products)))

                total_amount = 0
                items = []

                for product in selected_products:
                    # Obtener costo promedio del producto
                    purchases = Purchase.query.filter_by(product_code=product.code).all()
                    if purchases:
                        total_cost = sum(p.quantity * p.unit_cost for p in purchases)
                        total_qty = sum(p.quantity for p in purchases)
                        avg_cost = total_cost / total_qty if total_qty > 0 else 10
                    else:
                        avg_cost = 10

                    # Generar precio de venta (costo + 25-50% margen)
                    margin = random.uniform(0.25, 0.50)
                    unit_price = round(avg_cost * (1 + margin), 2)

                    # Cantidad vendida: 1-10 unidades
                    quantity = random.randint(1, 10)

                    subtotal = unit_price * quantity
                    total_amount += subtotal

                    items.append({
                        'product_code': product.code,
                        'quantity': quantity,
                        'unit_price': unit_price,
                        'subtotal': subtotal
                    })

                    # Registrar en tabla Sale para compatibilidad
                    sale = Sale(
                        date=sale_date,
                        product_code=product.code,
                        quantity=quantity,
                        unit_price=unit_price
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
                        product_code=item['product_code'],
                        quantity=item['quantity'],
                        unit_price=item['unit_price'],
                        subtotal=item['subtotal']
                    )
                    db.session.add(invoice_item)

        db.session.commit()
        print("✅ ¡Datos mocados generados exitosamente!")
        print("📊 Creadas ventas para los últimos 15 días")
        print("🎯 Ve a: http://127.0.0.1:5000/admin/sales-history para ver los análisis")

if __name__ == '__main__':
    generate_mock_sales()
