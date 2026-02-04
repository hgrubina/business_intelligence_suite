"""
Generador de datos sintéticos realistas para e-commerce.
Incluye ventas, productos, clientes, inventario con patrones realistas.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from typing import Dict, List, Optional
from faker import Faker

class EcommerceDataGenerator:
    """Genera datasets sintéticos realistas para análisis de negocios."""
    
    def __init__(self, seed: int = 42):
        """Inicializa el generador con semilla para reproducibilidad."""
        self.fake = Faker()
        Faker.seed(seed)
        random.seed(seed)
        np.random.seed(seed)
        
        # Configuración
        self.n_products = 50
        self.n_customers = 200
        self.n_days = 365  # Un año de datos
        
        # Productos
        self.categories = ["Electrónica", "Ropa", "Hogar", "Deportes", "Libros", "Juguetes"]
        self.subcategories = {
            "Electrónica": ["Smartphones", "Laptops", "Tablets", "Accesorios"],
            "Ropa": ["Hombre", "Mujer", "Niños", "Deportiva"],
            "Hogar": ["Cocina", "Decoración", "Muebles", "Jardín"],
            "Deportes": ["Fitness", "Running", "Natación", "Ciclismo"],
            "Libros": ["Ficción", "No Ficción", "Técnicos", "Infantiles"],
            "Juguetes": ["Educativos", "Videojuegos", "Exterior", "Bebés"]
        }
        
    def generate_products(self) -> pd.DataFrame:
        """Genera catálogo de productos."""
        products = []
        
        for i in range(1, self.n_products + 1):
            category = random.choice(self.categories)
            subcategory = random.choice(self.subcategories[category])
            
            # Precios con distribución log-normal (más realista)
            base_price = np.random.lognormal(mean=3.5, sigma=0.8) * 10
            price = round(base_price, 2)
            
            # Costo basado en precio con margen variable
            margin = np.random.uniform(0.3, 0.7)
            cost = round(price * (1 - margin), 2)
            
            product = {
                "product_id": i,
                "product_name": f"{self.fake.word().capitalize()} {self.fake.word().capitalize()}",
                "category": category,
                "subcategory": subcategory,
                "price": price,
                "cost": cost,
                "margin": round(margin * 100, 1),  # Porcentaje
                "sku": f"SKU-{i:04d}",
                "supplier": self.fake.company(),
                "weight_kg": round(np.random.uniform(0.1, 5.0), 2),
                "created_date": self.fake.date_between(start_date="-2y", end_date="-1y")
            }
            products.append(product)
        
        return pd.DataFrame(products)
    
    def generate_customers(self) -> pd.DataFrame:
        """Genera base de clientes."""
        customers = []
        
        regions = ["Norte", "Sur", "Este", "Oeste", "Centro"]
        customer_types = ["Ocasional", "Regular", "Premium", "Empresa"]
        
        for i in range(1, self.n_customers + 1):
            signup_date = self.fake.date_between(start_date="-3y", end_date="today")
            
            customers.append({
                "customer_id": i,
                "first_name": self.fake.first_name(),
                "last_name": self.fake.last_name(),
                "email": self.fake.email(),
                "phone": self.fake.phone_number(),
                "city": self.fake.city(),
                "region": random.choice(regions),
                "customer_type": random.choice(customer_types),
                "signup_date": signup_date,
                "last_purchase_date": None,  # Se actualizará después
                "total_spent": 0.0,  # Se actualizará después
                "total_orders": 0  # Se actualizará después
            })
        
        return pd.DataFrame(customers)
    
    def generate_sales(self, products_df: pd.DataFrame, customers_df: pd.DataFrame) -> pd.DataFrame:
        """Genera transacciones de ventas con patrones realistas."""
        sales = []
        current_date = datetime.now() - timedelta(days=self.n_days)
        
        # Patrones estacionales
        def seasonal_factor(date):
            """Factor de estacionalidad: más ventas en fin de semana, Navidad, etc."""
            day_factor = 1.5 if date.weekday() >= 4 else 1.0  # Fin de semana
            month = date.month
            
            # Temporadas altas (Navidad, Black Friday, verano)
            if month == 12:  # Diciembre (Navidad)
                month_factor = 2.5
            elif month == 11:  # Noviembre (Black Friday)
                month_factor = 2.0
            elif month in [6, 7]:  # Verano
                month_factor = 1.3
            else:
                month_factor = 1.0
            
            return day_factor * month_factor
        
        sale_id = 1
        for day in range(self.n_days):
            current_date += timedelta(days=1)
            
            # Número de ventas del día basado en estacionalidad
            base_sales = np.random.poisson(lam=50)  # Media de 50 ventas/día
            seasonal_adjustment = seasonal_factor(current_date)
            daily_sales = int(base_sales * seasonal_adjustment)
            
            for _ in range(daily_sales):
                # Seleccionar producto y cliente
                product = products_df.iloc[np.random.randint(0, len(products_df))]
                customer = customers_df.iloc[np.random.randint(0, len(customers_df))]
                
                # Cantidad (mayor probabilidad de 1, menor de más)
                quantity = np.random.choice([1, 2, 3, 4, 5], p=[0.6, 0.2, 0.1, 0.05, 0.05])
                
                # Descuento ocasional (20% de probabilidad)
                discount = np.random.uniform(0, 0.3) if np.random.random() < 0.2 else 0
                
                # Calcular totales
                subtotal = product["price"] * quantity
                discount_amount = subtotal * discount
                total = subtotal - discount_amount
                profit = (product["price"] - product["cost"]) * quantity * (1 - discount)
                
                sale = {
                    "sale_id": sale_id,
                    "date": current_date.date(),
                    "datetime": current_date,
                    "customer_id": customer["customer_id"],
                    "product_id": product["product_id"],
                    "quantity": quantity,
                    "unit_price": product["price"],
                    "subtotal": round(subtotal, 2),
                    "discount_pct": round(discount * 100, 1),
                    "discount_amount": round(discount_amount, 2),
                    "total": round(total, 2),
                    "cost": product["cost"] * quantity,
                    "profit": round(profit, 2),
                    "payment_method": random.choice(["Tarjeta", "Transferencia", "Efectivo", "MercadoPago"]),
                    "channel": random.choice(["Web", "App", "Físico", "Marketplace"]),
                    "region": customer["region"],
                    "category": product["category"],
                    "subcategory": product["subcategory"]
                }
                
                sales.append(sale)
                sale_id += 1
        
        return pd.DataFrame(sales)
    
    def generate_inventory(self, products_df: pd.DataFrame) -> pd.DataFrame:
        """Genera datos de inventario con movimientos."""
        inventory = []
        
        for _, product in products_df.iterrows():
            current_stock = np.random.randint(10, 100)
            reorder_point = int(current_stock * 0.3)
            ideal_stock = int(current_stock * 1.5)
            
            # Movimientos históricos
            for day in range(30):  # Últimos 30 días
                date = datetime.now() - timedelta(days=30 - day)
                
                # Ventas del día (aleatorio)
                daily_sales = np.random.poisson(lam=2)
                current_stock = max(0, current_stock - daily_sales)
                
                # Reabastecimiento aleatorio
                if current_stock <= reorder_point and np.random.random() < 0.3:
                    restock = np.random.randint(reorder_point, ideal_stock)
                    current_stock += restock
                
                inventory.append({
                    "date": date.date(),
                    "product_id": product["product_id"],
                    "product_name": product["product_name"],
                    "category": product["category"],
                    "current_stock": current_stock,
                    "daily_sales": daily_sales,
                    "reorder_point": reorder_point,
                    "ideal_stock": ideal_stock,
                    "stock_status": "OK" if current_stock > reorder_point else "LOW"
                })
        
        return pd.DataFrame(inventory)
    
        def generate_all_data(self, save_to_csv: bool = True) -> Dict[str, pd.DataFrame]:
        """Genera todos los datasets y los guarda como CSV - VERSIÓN CORREGIDA."""
        print("🚀 Generando datos sintéticos para e-commerce...")

        # Generar datasets básicos
        print("📦 Generando productos...")
        products = self.generate_products()

        print("👥 Generando clientes...")
        customers = self.generate_customers()

        print("💰 Generando ventas...")
        sales = self.generate_sales(products, customers)

        print("📊 Generando inventario...")
        inventory = self.generate_inventory(products)

        # ACTUALIZACIÓN DE CLIENTES - FORMA ROBUSTA
        print("🔄 Actualizando datos de clientes...")

        # 1. Primero, asegurar que las columnas existen en customers
        if "total_spent" not in customers.columns:
            customers["total_spent"] = 0.0
        if "total_orders" not in customers.columns:
            customers["total_orders"] = 0
        if "last_purchase_date" not in customers.columns:
            customers["last_purchase_date"] = pd.NaT

        # 2. Si hay ventas, calcular estadísticas
        if not sales.empty and len(sales) > 0:
            try:
                # Calcular estadísticas por cliente
                customer_stats = sales.groupby("customer_id").agg({
                    "total": "sum",
                    "sale_id": "count",
                    "date": "max"
                }).reset_index()

                # Renombrar columnas
                customer_stats.columns = ["customer_id", "calc_total_spent", "calc_total_orders", "calc_last_purchase"]

                # Hacer merge con customers
                customers = pd.merge(
                    customers,
                    customer_stats,
                    on="customer_id",
                    how="left",
                    suffixes=("", "_calc")
                )

                # Actualizar valores donde haya cálculos
                mask = customers["calc_total_spent"].notna()
                customers.loc[mask, "total_spent"] = customers.loc[mask, "calc_total_spent"]
                customers.loc[mask, "total_orders"] = customers.loc[mask, "calc_total_orders"]
                customers.loc[mask, "last_purchase_date"] = customers.loc[mask, "calc_last_purchase"]

                # Eliminar columnas temporales
                customers = customers.drop(
                    columns=["calc_total_spent", "calc_total_orders", "calc_last_purchase"],
                    errors="ignore"
                )

            except Exception as e:
                print(f"⚠️  Error actualizando estadísticas de clientes: {e}")
                print("Continuando con valores por defecto...")

        # 3. Asegurar tipos de datos correctos
        customers["total_spent"] = customers["total_spent"].fillna(0).astype(float)
        customers["total_orders"] = customers["total_orders"].fillna(0).astype(int)

        # 4. Guardar a CSV si se solicita
        if save_to_csv:
            # Crear directorio si no existe
            import os
            os.makedirs("data/raw", exist_ok=True)

            print("💾 Guardando datos en CSV...")

            # Guardar todos los datasets
            datasets = {
                "products": products,
                "customers": customers,
                "sales": sales,
                "inventory": inventory
            }

            for name, df in datasets.items():
                filename = f"data/raw/{name}.csv"
                df.to_csv(filename, index=False)
                print(f"   - {name}: {len(df):,} registros → {filename}")

        # 5. Resumen final
        print("\n📈 RESUMEN FINAL:")
        print("=" * 50)

        if not sales.empty:
            total_revenue = sales["total"].sum()
            total_profit = sales["profit"].sum() if "profit" in sales.columns else 0
            total_orders = len(sales)

            print(f"Total Revenue: ${total_revenue:,.2f}")
            print(f"Total Profit: ${total_profit:,.2f}")
            print(f"Total Orders: {total_orders:,}")
            print(f"Date Range: {sales['date'].min()} to {sales['date'].max()}")
        else:
            print("⚠️  No se generaron ventas")

        print(f"Total Products: {len(products):,}")
        print(f"Total Customers: {len(customers):,}")
        print(f"Total Inventory Records: {len(inventory):,}")

        return {
            "products": products,
            "customers": customers,
            "sales": sales,
            "inventory": inventory
        }
