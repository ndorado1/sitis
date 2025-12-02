#!/bin/bash
# Script para limpiar el cache de Streamlit y local

echo "🧹 Limpiando cache..."

# Limpiar cache de Streamlit
echo "📁 Limpiando cache de Streamlit..."
rm -rf .streamlit/cache
rm -rf ~/.streamlit/cache

# Limpiar cache local de SharePoint
echo "📁 Limpiando cache de SharePoint..."
rm -rf cache_sharepoint/

# Limpiar pycache
echo "📁 Limpiando __pycache__..."
rm -rf __pycache__/

echo "✅ Cache limpiado!"
echo ""
echo "💡 Ahora ejecuta: streamlit run app.py"

