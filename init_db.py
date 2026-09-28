#!/usr/bin/env python
"""
Script para inicializar o banco de dados do zero com todas as tabelas
"""
import os
from dotenv import load_dotenv
from app import app, db
from models import User, Product, Purchase, Sale, Invoice, InvoiceItem, InventoryCount, InventoryCountItem
from werkzeug.security import generate_password_hash

load_dotenv(override=True)

with app.app_context():
    print("🔨 Reconstruindo banco de dados...")

    # Drop all tables
    print("  ❌ Deletando tabelas antigas...")
    db.drop_all()

    # Create all tables from models
    print("  ✅ Criando novas tabelas...")
    db.create_all()

    # Verify Sale has vendor_id
    print("\n📋 Verificando schema...")
    inspector = db.inspect(db.engine)
    sale_columns = [col['name'] for col in inspector.get_columns('sale')]
    print(f"  Colunas de 'sale': {sale_columns}")

    if 'vendor_id' in sale_columns:
        print("  ✅ vendor_id presente em sale")
    else:
        print("  ❌ ERRO: vendor_id NÃO está em sale!")

    invoice_columns = [col['name'] for col in inspector.get_columns('invoice')]
    print(f"  Colunas de 'invoice': {invoice_columns}")

    if 'vendor_id' in invoice_columns:
        print("  ✅ vendor_id presente em invoice")
    else:
        print("  ❌ ERRO: vendor_id NÃO está em invoice!")

    # Insert default users
    print("\n👤 Criando usuários...")
    db.session.add(User(username='dev', password=generate_password_hash('dev123'), role='dev'))
    db.session.add(User(username='admin', password=generate_password_hash('admin123'), role='admin'))
    db.session.add(User(username='vendedor', password=generate_password_hash('vendedor123'), role='vendedor'))
    db.session.commit()
    print("  ✅ Usuários criados: dev, admin, vendedor")

    print("\n✅ BANCO DE DADOS INICIALIZADO COM SUCESSO!")
