"""
Script para corregir automáticamente el dashboard.
"""
import re

# Leer el archivo original
with open('dashboards/sales_dashboard.py', 'r') as f:
    content = f.read()

# 1. Corregir use_container_width
content = content.replace('use_container_width=True', "width='stretch'")
content = content.replace('use_container_width=False', "width='content'")

# 2. Corregir el error específico del metric
# Buscar la línea problemática y reemplazarla
error_line = "st.metric(f\"{period_option} Pico\", peak_period, delta=f\"${peak_value:,.0f}\")"
fixed_lines = '''
            # Convertir a string si es Timestamp
            if hasattr(peak_period, 'date'):
                peak_display = str(peak_period.date())
            elif hasattr(peak_period, 'strftime'):
                peak_display = peak_period.strftime('%Y-%m-%d')
            else:
                peak_display = str(peak_period)
            
            st.metric(f"{period_option} Pico", peak_display, delta=f"${peak_value:,.0f}")
'''

# Reemplazar
if error_line in content:
    content = content.replace(error_line, fixed_lines)

# Guardar corregido
with open('dashboards/sales_dashboard_fixed.py', 'w') as f:
    f.write(content)

print("✅ Dashboard corregido guardado como: dashboards/sales_dashboard_fixed.py")
print("🎯 Ejecuta: streamlit run dashboards/sales_dashboard_fixed.py")
