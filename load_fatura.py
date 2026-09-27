#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para cargar la fatura del 29-08-2026 al ERP
"""

import sys
sys.path.insert(0, '.')

from app import app, db
from models import Product, Purchase
from utils import generate_sku

# Datos de la fatura
FATURA_DATA = [
    ("COLET PANTY BEBE INDIVIDUAL", "ACCESORIOS", 24, 300),
    ("TIBURON RECTANGULO DOUBLE AGARRE COLOR", "ACCESORIOS", 2, 3600),
    ("TICTAC ESTRELLA G COLOR 1", "ACCESORIOS", 18, 700),
    ("TIC TAC PUNTO + CUADRILLE", "ACCESORIOS", 18, 400),
    ("PINZA 6/3 DIFT", "ACCESORIOS", 18, 700),
    ("COLET PANTY MEDIANO CON CARTON", "ACCESORIOS", 6, 1500),
    ("CINTILLO NUDO SURTIDO AZUL", "ACCESORIOS", 1, 4800),
    ("TIBURON ENGOMADO RECTANGULAR", "ACCESORIOS", 2, 3600),
    ("SET CINTILLO SPA + HAWAI", "ACCESORIOS", 4, 1400),
    ("TIBURON RECTANGULO NEGRO 4CM", "ACCESORIOS", 1, 1500),
    ("TIRA MARIPOSA CHICA", "ACCESORIOS", 2, 1500),
    ("TIBURON METAL MEDIANO CUADRADO", "ACCESORIOS", 1, 3600),
    ("COLET TRENZA TUBO", "ACCESORIOS", 12, 500),
]

def load_fatura():
    with app.app_context():
        print("🔨 Iniciando carga de fatura...")
        print(f"📦 Agregando {len(FATURA_DATA)} productos...")

        for nombre, categoria, cantidad, precio_unitario in FATURA_DATA:
            try:
                # Generar SKU
                sku = generate_sku()

                # Crear producto
                product = Product(
                    code=sku,
                    name=nombre,
                    category=categoria,
                    cost_price=precio_unitario,
                    sale_price=0,
                    min_stock=5,
                    status='ativo'
                )
                db.session.add(product)
                db.session.flush()  # Para obtener el ID

                # Crear entrada de compra
                purchase = Purchase(
                    date='29/08/2026',
                    product_code=sku,
                    quantity=cantidad,
                    unit_cost=precio_unitario
                )
                db.session.add(purchase)

                print(f"✅ {sku} - {nombre} ({cantidad} x ${precio_unitario})")

            except Exception as e:
                print(f"❌ Error: {e}")
                db.session.rollback()

        # Commit final
        try:
            db.session.commit()
            print(f"\n🎉 ¡Fatura cargada exitosamente!")
            print(f"📊 Total: {len(FATURA_DATA)} productos")
            print(f"💰 Valor total: $87.500")
        except Exception as e:
            print(f"❌ Error al guardar: {e}")
            db.session.rollback()

if __name__ == '__main__':
    load_fatura()
