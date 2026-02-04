"""
Dashboard de Business Intelligence para análisis de ventas.
Dashboard interactivo con Streamlit y Plotly.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Configuración de la página
st.set_page_config(
    page_title="Business Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("📊 Business Intelligence Dashboard")
st.markdown("""
**Dashboard profesional para análisis de ventas y performance de negocio**  
*Generado automáticamente con Python | PhD Data Engineer*
""")

# Cargar datos
@st.cache_data
def load_data():
    """Carga los datasets con caching para mejor performance."""
    try:
        products = pd.read_csv("data/raw/products.csv")
        sales = pd.read_csv("data/raw/sales.csv")
        
        # Convertir fechas
        sales['date'] = pd.to_datetime(sales['date'])
        
        # Calcular métricas adicionales
        sales['month'] = sales['date'].dt.to_period('M').astype(str)
        sales['week'] = sales['date'].dt.isocalendar().week
        sales['day_of_week'] = sales['date'].dt.day_name()
        
        return products, sales
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return pd.DataFrame(), pd.DataFrame()

# Cargar datos
products, sales = load_data()

# Verificar que hay datos
if sales.empty:
    st.warning("No hay datos disponibles. Por favor genera datos primero.")
    st.stop()

# ========== SIDEBAR ==========
st.sidebar.header("⚙️ Filtros y Configuración")

# Filtro de fecha
st.sidebar.subheader("Rango de Fechas")
min_date = sales['date'].min().date()
max_date = sales['date'].max().date()

date_range = st.sidebar.date_input(
    "Seleccionar período",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Convertir a datetime para filtrado
if len(date_range) == 2:
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    sales_filtered = sales[(sales['date'] >= start_date) & (sales['date'] <= end_date)]
else:
    sales_filtered = sales.copy()

# Filtro de categoría
st.sidebar.subheader("Filtros por Categoría")
all_categories = sorted(sales_filtered['category'].unique())
selected_categories = st.sidebar.multiselect(
    "Seleccionar categorías",
    options=all_categories,
    default=all_categories[:3] if len(all_categories) > 3 else all_categories
)

if selected_categories:
    sales_filtered = sales_filtered[sales_filtered['category'].isin(selected_categories)]

# Filtro de región
if 'region' in sales_filtered.columns:
    regions = sorted(sales_filtered['region'].unique())
    selected_regions = st.sidebar.multiselect(
        "Seleccionar regiones",
        options=regions,
        default=regions
    )
    if selected_regions:
        sales_filtered = sales_filtered[sales_filtered['region'].isin(selected_regions)]

# Métricas KPI en sidebar
st.sidebar.subheader("📈 KPIs del Período")
total_revenue = sales_filtered['total'].sum()
total_profit = sales_filtered['profit'].sum()
avg_order_value = sales_filtered['total'].mean()
total_orders = len(sales_filtered)

st.sidebar.metric("Revenue Total", f"${total_revenue:,.0f}")
st.sidebar.metric("Profit Total", f"${total_profit:,.0f}")
st.sidebar.metric("Órdenes Totales", f"{total_orders:,}")
st.sidebar.metric("Valor Promedio", f"${avg_order_value:,.0f}")

# ========== MAIN DASHBOARD ==========
st.markdown("---")

# Row 1: Métricas principales
st.subheader("📊 Métricas Clave del Negocio")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Margen Promedio", 
        f"{(total_profit/total_revenue*100 if total_revenue > 0 else 0):.1f}%",
        delta=f"{(total_profit/total_revenue*100 - 50):+.1f}%" if total_revenue > 0 else "0%"
    )

with col2:
    # Crecimiento vs período anterior
    if len(date_range) == 2:
        days_diff = (end_date - start_date).days
        prev_start = start_date - pd.Timedelta(days=days_diff)
        prev_end = start_date - pd.Timedelta(days=1)
        prev_sales = sales[(sales['date'] >= prev_start) & (sales['date'] <= prev_end)]
        prev_revenue = prev_sales['total'].sum() if not prev_sales.empty else 0
        
        if prev_revenue > 0:
            growth = ((total_revenue - prev_revenue) / prev_revenue * 100)
            st.metric("Crecimiento Revenue", f"{growth:.1f}%")
        else:
            st.metric("Crecimiento Revenue", "N/A")
    else:
        st.metric("Crecimiento Revenue", "N/A")

with col3:
    # Producto más vendido
    if not sales_filtered.empty:
        top_product = sales_filtered.groupby('product_name')['quantity'].sum().idxmax()
        st.metric("Producto Top", top_product[:20] + "..." if len(top_product) > 20 else top_product)
    else:
        st.metric("Producto Top", "N/A")

with col4:
    # Categoría líder
    if not sales_filtered.empty:
        top_category = sales_filtered.groupby('category')['total'].sum().idxmax()
        category_revenue = sales_filtered.groupby('category')['total'].sum().max()
        st.metric("Categoría Líder", top_category, delta=f"${category_revenue:,.0f}")
    else:
        st.metric("Categoría Líder", "N/A")

st.markdown("---")

# Row 2: Gráficos principales
st.subheader("📈 Análisis de Tendencia y Performance")

tab1, tab2, tab3, tab4 = st.tabs(["📅 Tendencia Temporal", "🏷️ Análisis por Categoría", "📦 Productos Top", "🌍 Análisis Geográfico"])

with tab1:
    # Gráfico de tendencia temporal
    col1, col2 = st.columns([2, 1])

    with col1:
        # Ventas por día/semana/mes
        period_option = st.radio(
            "Agrupar por:",
            ["Día", "Semana", "Mes"],
            horizontal=True
        )

        if period_option == "Día":
            group_col = 'date'
            title = "Revenue Diario"
        elif period_option == "Semana":
            sales_filtered['year_week'] = sales_filtered['date'].dt.strftime('%Y-W%U')
            group_col = 'year_week'
            title = "Revenue Semanal"
        else:  # Mes
            group_col = 'month'
            title = "Revenue Mensual"

        # Data para el gráfico
        trend_data = sales_filtered.groupby(group_col).agg({
            'total': 'sum',
            'profit': 'sum',
            'quantity': 'sum'
        }).reset_index()

        # Gráfico de líneas
        fig_trend = make_subplots(specs=[[{"secondary_y": True}]])

        # Línea de revenue
        fig_trend.add_trace(
            go.Scatter(
                x=trend_data[group_col],
                y=trend_data['total'],
                name="Revenue",
                line=dict(color='#1f77b4', width=3),
                mode='lines+markers'
            ),
            secondary_y=False
        )

        # Línea de profit
        fig_trend.add_trace(
            go.Scatter(
                x=trend_data[group_col],
                y=trend_data['profit'],
                name="Profit",
                line=dict(color='#2ca02c', width=2, dash='dash'),
                mode='lines+markers'
            ),
            secondary_y=True
        )

        fig_trend.update_layout(
            title=title,
            xaxis_title=period_option,
            yaxis_title="Revenue ($)",
            yaxis2_title="Profit ($)",
            hovermode='x unified',
            template='plotly_white',
            height=400
        )

        st.plotly_chart(fig_trend, width='stretch')

    with col2:
        # Métricas de tendencia
        st.subheader("📋 Resumen de Tendencia")

        if len(trend_data) > 1:
            # Cálculo de crecimiento
            first_val = trend_data['total'].iloc[0]
            last_val = trend_data['total'].iloc[-1]
            growth_pct = ((last_val - first_val) / first_val * 100) if first_val > 0 else 0

            st.metric(
                "Crecimiento del Período",
                f"{growth_pct:+.1f}%",
                delta=f"{growth_pct:+.1f}%"
            )

            # Revenue promedio
            avg_revenue = trend_data['total'].mean()
            st.metric("Revenue Promedio", f"${avg_revenue:,.0f}")

            # Variabilidad
            revenue_std = trend_data['total'].std()
            cv = (revenue_std / avg_revenue * 100) if avg_revenue > 0 else 0
            st.metric("Coeficiente Variación", f"{cv:.1f}%")

            # Día/semana/mes pico
            peak_idx = trend_data['total'].idxmax()
            peak_period = trend_data.loc[peak_idx, group_col]
            peak_value = trend_data.loc[peak_idx, 'total']

            # Convertir a string si es Timestamp
            if hasattr(peak_period, 'date'):
                peak_display = str(peak_period.date())
            elif hasattr(peak_period, 'strftime'):
                peak_display = peak_period.strftime('%Y-%m-%d')
            else:
                peak_display = str(peak_period)

            st.metric(f"{period_option} Pico", peak_display, delta=f"${peak_value:,.0f}")

with tab2:
    # Análisis por categoría
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de barras por categoría
        cat_data = sales_filtered.groupby('category').agg({
            'total': 'sum',
            'profit': 'sum',
            'quantity': 'sum'
        }).reset_index()
        
        # Ordenar por revenue
        cat_data = cat_data.sort_values('total', ascending=False)
        
        fig_cat = px.bar(
            cat_data,
            x='category',
            y='total',
            color='profit',
            title="Revenue y Profit por Categoría",
            labels={'total': 'Revenue ($)', 'profit': 'Profit ($)', 'category': 'Categoría'},
            color_continuous_scale='Viridis',
            text_auto='.2s'
        )
        
        fig_cat.update_layout(height=500)
        st.plotly_chart(fig_cat, width='stretch')
    
    with col2:
        # Pie chart de distribución
        fig_pie = px.pie(
            cat_data,
            values='total',
            names='category',
            title="Distribución de Revenue por Categoría",
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(height=500)
        st.plotly_chart(fig_pie, width='stretch')
        
        # Tabla de métricas por categoría
        st.subheader("📋 Métricas por Categoría")
        cat_metrics = cat_data.copy()
        cat_metrics['margin_pct'] = (cat_metrics['profit'] / cat_metrics['total'] * 100).round(1)
        cat_metrics['avg_price'] = (cat_metrics['total'] / cat_metrics['quantity']).round(2)
        
        st.dataframe(
            cat_metrics[['category', 'total', 'profit', 'margin_pct', 'quantity', 'avg_price']]
            .rename(columns={
                'category': 'Categoría',
                'total': 'Revenue',
                'profit': 'Profit',
                'margin_pct': 'Margen %',
                'quantity': 'Cantidad',
                'avg_price': 'Precio Prom'
            })
            .style.format({
                'Revenue': '${:,.0f}',
                'Profit': '${:,.0f}',
                'Margen %': '{:.1f}%',
                'Cantidad': '{:,}',
                'Precio Prom': '${:.2f}'
            })
            .background_gradient(subset=['Margen %'], cmap='RdYlGn'),
            width='stretch'
        )

with tab3:
    # Análisis de productos
    st.subheader("🔍 Top 20 Productos por Revenue")
    
    # Calcular métricas por producto
    product_stats = sales_filtered.groupby(['product_id', 'product_name', 'category']).agg({
        'total': 'sum',
        'profit': 'sum',
        'quantity': 'sum'
    }).reset_index()
    
    product_stats['margin_pct'] = (product_stats['profit'] / product_stats['total'] * 100).round(1)
    product_stats['avg_price'] = (product_stats['total'] / product_stats['quantity']).round(2)
    
    # Ordenar y tomar top 20
    top_products = product_stats.sort_values('total', ascending=False).head(20)
    
    # Gráfico de barras horizontales
    fig_products = px.bar(
        top_products.sort_values('total'),
        y='product_name',
        x='total',
        orientation='h',
        color='margin_pct',
        title="Top 20 Productos por Revenue",
        labels={'total': 'Revenue ($)', 'product_name': 'Producto', 'margin_pct': 'Margen %'},
        color_continuous_scale='Blues',
        text_auto='.2s'
    )
    
    fig_products.update_layout(height=600)
    st.plotly_chart(fig_products, width='stretch')
    
    # Tabla detallada
    st.subheader("📋 Detalle de Productos Top")
    st.dataframe(
        top_products[['product_name', 'category', 'total', 'profit', 'margin_pct', 'quantity', 'avg_price']]
        .rename(columns={
            'product_name': 'Producto',
            'category': 'Categoría',
            'total': 'Revenue',
            'profit': 'Profit',
            'margin_pct': 'Margen %',
            'quantity': 'Cantidad',
            'avg_price': 'Precio Prom'
        })
        .style.format({
            'Revenue': '${:,.0f}',
            'Profit': '${:,.0f}',
            'Margen %': '{:.1f}%',
            'Cantidad': '{:,}',
            'Precio Prom': '${:.2f}'
        })
        .background_gradient(subset=['Revenue'], cmap='Blues')
        .background_gradient(subset=['Margen %'], cmap='RdYlGn'),
        width='stretch',
        height=400
    )

with tab4:
    # Análisis geográfico (si hay datos de región)
    if 'region' in sales_filtered.columns and not sales_filtered.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Revenue por región
            region_data = sales_filtered.groupby('region').agg({
                'total': 'sum',
                'profit': 'sum',
                'quantity': 'sum'
            }).reset_index()
            
            fig_region = px.bar(
                region_data,
                x='region',
                y='total',
                color='profit',
                title="Revenue por Región",
                labels={'total': 'Revenue ($)', 'profit': 'Profit ($)', 'region': 'Región'},
                color_continuous_scale='Greens',
                text_auto='.2s'
            )
            
            fig_region.update_layout(height=400)
            st.plotly_chart(fig_region, width='stretch')
        
        with col2:
            # Mapa de calor de margen por región
            region_margin = region_data.copy()
            region_margin['margin_pct'] = (region_margin['profit'] / region_margin['total'] * 100).round(1)
            
            fig_heatmap = px.imshow(
                [region_margin['margin_pct'].values],
                x=region_margin['region'].values,
                y=['Margen'],
                color_continuous_scale='RdYlGn',
                title="Margen por Región (%)",
                labels=dict(x="Región", y="", color="Margen %"),
                aspect="auto"
            )
            
            fig_heatmap.update_layout(height=300)
            st.plotly_chart(fig_heatmap, width='stretch')
            
            # Tabla de regiones
            st.dataframe(
                region_data[['region', 'total', 'profit', 'quantity']]
                .rename(columns={
                    'region': 'Región',
                    'total': 'Revenue',
                    'profit': 'Profit',
                    'quantity': 'Cantidad'
                })
                .style.format({
                    'Revenue': '${:,.0f}',
                    'Profit': '${:,.0f}',
                    'Cantidad': '{:,}'
                }),
                width='stretch'
            )
    else:
        st.info("No hay datos de región disponibles para análisis geográfico.")

# ========== SECCIÓN DE INSIGHTS AUTOMÁTICOS ==========
st.markdown("---")
st.subheader("💡 Insights Automáticos Generados")

# Generar insights automáticos
def generate_insights(sales_df, products_df):
    """Genera insights automáticos basados en los datos."""
    insights = []
    
    if sales_df.empty:
        return ["No hay datos suficientes para generar insights."]
    
    # 1. Insight de tendencia
    if len(sales_df) > 7:  # Si hay al menos una semana de datos
        daily_sales = sales_df.groupby('date')['total'].sum()
        if len(daily_sales) > 1:
            trend = np.polyfit(range(len(daily_sales)), daily_sales.values, 1)[0]
            if trend > 0:
                insights.append("📈 **Tendencia positiva**: Las ventas muestran una tendencia alcista en el período seleccionado.")
            else:
                insights.append("📉 **Tendencia negativa**: Las ventas muestran una tendencia a la baja en el período seleccionado.")
    
    # 2. Insight de categoría líder
    category_revenue = sales_df.groupby('category')['total'].sum()
    if not category_revenue.empty:
        top_category = category_revenue.idxmax()
        top_revenue = category_revenue.max()
        total_revenue = category_revenue.sum()
        percentage = (top_revenue / total_revenue * 100)
        
        insights.append(f"🏆 **Categoría líder**: '{top_category}' representa el {percentage:.1f}% del revenue total.")
    
    # 3. Insight de margen
    total_rev = sales_df['total'].sum()
    total_prof = sales_df['profit'].sum()
    if total_rev > 0:
        overall_margin = (total_prof / total_rev * 100)
        if overall_margin > 55:
            insights.append("💰 **Alto margen**: El margen promedio es excelente (>55%).")
        elif overall_margin < 45:
            insights.append("⚠️ **Margen bajo**: Considerar optimizar precios o costos.")
    
    # 4. Insight de estacionalidad semanal
    if 'day_of_week' in sales_df.columns:
        weekday_sales = sales_df.groupby('day_of_week')['total'].sum()
        if not weekday_sales.empty:
            days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            weekday_sales = weekday_sales.reindex(days_order, fill_value=0)
            
            best_day = weekday_sales.idxmax()
            worst_day = weekday_sales.idxmin()
            
            insights.append(f"📅 **Patrón semanal**: Mejor día: {best_day}, Peor día: {worst_day}.")
    
    # 5. Insight de productos
    if not products_df.empty and 'margin_pct' in products_df.columns:
        high_margin_products = products_df[products_df['margin_pct'] > 60]
        low_margin_products = products_df[products_df['margin_pct'] < 40]
        
        if len(high_margin_products) > 0:
            insights.append(f"✅ **Oportunidad**: {len(high_margin_products)} productos con margen >60%.")
        if len(low_margin_products) > 0:
            insights.append(f"🔍 **Revisión necesaria**: {len(low_margin_products)} productos con margen <40%.")
    
    return insights if insights else ["Los datos son consistentes. No se detectaron anomalías significativas."]

# Mostrar insights
insights = generate_insights(sales_filtered, products)

for insight in insights:
    st.info(insight)

# ========== PIE DE PÁGINA ==========
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9em;'>
    <p>📊 <strong>Business Intelligence Dashboard</strong> | Generado automáticamente con Python</p>
    <p>👨‍🔬 <em>PhD Data Engineer | Automated Business Insights</em></p>
    <p>🔄 Datos actualizados en tiempo real | Filtros interactivos | Insights automáticos</p>
</div>
""", unsafe_allow_html=True)

# Información del dataset
with st.expander("ℹ️ Información Técnica del Dataset"):
    st.write(f"**Período de datos:** {sales['date'].min().date()} a {sales['date'].max().date()}")
    st.write(f"**Total de registros:** {len(sales):,} ventas")
    st.write(f"**Total de productos:** {len(products):,}")
    st.write(f"**Última actualización:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    st.code("""
# Para ejecutar este dashboard:
# streamlit run dashboards/sales_dashboard.py

# Estructura de datos:
# - sales.csv: Ventas diarias con revenue, profit, categorías
# - products.csv: Catálogo de productos con precios y costos
    """)

