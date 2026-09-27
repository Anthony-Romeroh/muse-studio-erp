from models import Product, Invoice
from database import db
from datetime import datetime

def generate_invoice_number():
    """Genera un número de nota fiscal sequencial"""
    today = datetime.now().strftime('%Y%m%d')
    last_invoice = Invoice.query.filter(Invoice.invoice_number.like(f'{today}%')).count()
    invoice_num = f"{today}{str(last_invoice + 1).zfill(5)}"
    return invoice_num

def generate_sku():
    """Gera um SKU sequencial automaticamente"""
    # Conta quantos produtos existem
    product_count = Product.query.count()
    next_number = product_count + 1

    # Formato: MS-000001, MS-000002, etc
    sku = f"MS-{next_number:06d}"

    return sku

def toggle_product_status(product_code):
    """Alterna status do produto entre ativo e inativo"""
    product = Product.query.filter_by(code=product_code).first()
    if product:
        product.status = 'inativo' if product.status == 'ativo' else 'ativo'
        db.session.commit()
        return product.status
    return None

def delete_product(product_code):
    """Deleta um produto"""
    product = Product.query.filter_by(code=product_code).first()
    if product:
        db.session.delete(product)
        db.session.commit()
        return True
    return False
