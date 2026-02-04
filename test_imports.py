#!/usr/bin/env python3
"""
Test para verificar que todas las librerías están disponibles.
"""
import sys

print("Python version:", sys.version)
print("\nProbando importaciones...")

libs = [
    ("numpy", "np"),
    ("pandas", "pd"),
    ("scipy", "sp"),
    ("sklearn", "sklearn"),
    ("matplotlib", "plt"),
    ("streamlit", "st"),
    ("plotly", "ply"),
    ("faker", "faker")
]

for lib_name, short_name in libs:
    try:
        if lib_name == "matplotlib":
            import matplotlib
            matplotlib.use('Agg')  # Para no requerir display
        exec(f"import {lib_name} as {short_name}")
        version = eval(f"{short_name}.__version__")
        print(f"✅ {lib_name:20} {version}")
    except ImportError as e:
        print(f"❌ {lib_name:20} NO DISPONIBLE: {e}")
    except AttributeError:
        print(f"✅ {lib_name:20} (sin versión)")

print("\n🎯 Si ves pandas y numpy ✅, estamos listos para codificar!")
