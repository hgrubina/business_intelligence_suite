"""
Generador de datos robusto y garantizado.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from typing import Dict
import os

class RobustDataGenerator:
    """Generador que siempre funciona."""
    
    def __init__(self, seed=42):
        self.seed = seed
        np.random.seed(seed)
        random.seed(seed)
        
    def generate_products(self):
        """Genera productos simples."""
        n_products = 100
        categories = ['Electronics', 'Clothing', 'Home', 'Sports', 'Books']
        
        data = []
        for i in range(1, n_products + 1):
            category = random.choice(categories)
            price = round(np.random.uniform(10, 500), 2)
            cost = round(price * np.random.uniform(0.3, 0.7), 2)
            
            data.append({
                'product_id': i,
                'name': f'Product {i}',
                'category': category,
                'price': price,
                'cost': cost,
                'margin_pct': round((price - cost) / price * 100, 1)
            })
        
        return pd.DataFrame(data)
    
    def generate_sales(self, products_df, n_days=365):
        """Genera ventas para un período."""
        sales = []
        start_date = datetime.now() - timedelta(days=n_days)
        
        for day in range(n_days):
            current_date = start_date + timedelta(days=day)
            
            # Número de ventas del día (más en fin de semana)
            is_weekend = current_date.weekday() >= 5
            n_sales = np.random.poisson(60 if is_weekend else 40)
            
            for _ in range(n_sales):
                product = products_df.sample(1).iloc[0]
                quantity = np.random.randint(1, 4)
                total = round(product['price'] * quantity, 2)
                profit = round((product['price'] - product['cost']) * quantity, 2)
                
                sales.append({
                    'date': current_date.date(),
                    'product_id': product['product_id'],
                    'product_name': product['name'],
                    'category': product['category'],
                    'quantity': quantity,
                    'unit_price': product['price'],
                    'total': total,
                    'cost': round(product['cost'] * quantity, 2),
                    'profit': profit,
                    'customer_id': np.random.randint(1, 1001),
                    'region': random.choice(['North', 'South', 'East', 'West', 'Central'])
                })
        
        return pd.DataFrame(sales)
    
    def generate_all(self, save=True):
        """Genera todo y guarda."""
        print("🚀 Iniciando generación de datos...")
        
        # 1. Productos
        print("📦 Generando productos...")
        products = self.generate_products()
        
        # 2. Ventas
        print("💰 Generando ventas...")
        sales = self.generate_sales(products, n_days=180)  # 6 meses
        
        # 3. Guardar
        if save:
            os.makedirs('data/raw', exist_ok=True)
            
            products.to_csv('data/raw/products.csv', index=False)
            sales.to_csv('data/raw/sales.csv', index=False)
            
            print(f"\n💾 Datos guardados:")
            print(f"   - products.csv: {len(products):,} productos")
            print(f"   - sales.csv: {len(sales):,} ventas")
        
        # 4. Resumen
        print("\n📊 RESUMEN:")
        print("=" * 40)
        print(f"Período: {sales['date'].min()} a {sales['date'].max()}")
        print(f"Ventas totales: {len(sales):,}")
        print(f"Revenue total: ${sales['total'].sum():,.2f}")
        print(f"Profit total: ${sales['profit'].sum():,.2f}")
        print(f"Margen promedio: {(sales['profit'].sum() / sales['total'].sum() * 100):.1f}%")
        print(f"Valor promedio por venta: ${sales['total'].mean():.2f}")
        
        return {'products': products, 'sales': sales}

# Ejecutar
if __name__ == "__main__":
    generator = RobustDataGenerator(seed=42)
    data = generator.generate_all(save=True)
    
    print("\n✅ Generación completada exitosamente!")
    print("🎯 Ahora puedes ejecutar: streamlit run dashboards/sales_dashboard.py")
