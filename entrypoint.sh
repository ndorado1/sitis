#!/bin/bash
# Entrypoint para el contenedor Docker con validaciones y debugging

set -e  # Exit on error

echo "=========================================="
echo "🏥 Iniciando Sistema SITIS"
echo "=========================================="
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 1. Verificar Python
log_info "Verificando Python..."
python --version
log_success "Python OK"
echo ""

# 2. Verificar módulos instalados
log_info "Verificando módulos de Python..."
python -c "import streamlit; print(f'  - Streamlit: {streamlit.__version__}')"
python -c "import pandas; print(f'  - Pandas: {pandas.__version__}')"
python -c "import msal; print(f'  - MSAL: {msal.__version__}')"
python -c "import requests; print(f'  - Requests: {requests.__version__}')"
log_success "Módulos OK"
echo ""

# 3. Verificar archivos necesarios
log_info "Verificando archivos de la aplicación..."
if [ ! -f "app.py" ]; then
    log_error "No se encuentra app.py"
    exit 1
fi
if [ ! -f "sharepoint_loader.py" ]; then
    log_error "No se encuentra sharepoint_loader.py"
    exit 1
fi
if [ ! -f "config_sharepoint.py" ]; then
    log_error "No se encuentra config_sharepoint.py"
    exit 1
fi
if [ ! -f "ACTXPROG_filtrado.csv" ]; then
    log_error "No se encuentra ACTXPROG_filtrado.csv"
    exit 1
fi
log_success "Archivos OK"
echo ""

# 4. Verificar variables de entorno
log_info "Verificando variables de entorno..."
if [ -z "$SHAREPOINT_CLIENT_ID" ]; then
    log_error "SHAREPOINT_CLIENT_ID no configurado"
    echo "Configura las variables de entorno en Easypanel"
    exit 1
fi
if [ -z "$SHAREPOINT_CLIENT_SECRET" ]; then
    log_error "SHAREPOINT_CLIENT_SECRET no configurado"
    exit 1
fi
if [ -z "$SHAREPOINT_TENANT_ID" ]; then
    log_error "SHAREPOINT_TENANT_ID no configurado"
    exit 1
fi

echo "  - SHAREPOINT_CLIENT_ID: ${SHAREPOINT_CLIENT_ID:0:8}...${SHAREPOINT_CLIENT_ID: -4}"
echo "  - SHAREPOINT_CLIENT_SECRET: ********"
echo "  - SHAREPOINT_TENANT_ID: ${SHAREPOINT_TENANT_ID:0:8}...${SHAREPOINT_TENANT_ID: -4}"
echo "  - MODO_CARGA_SEDES: ${MODO_CARGA_SEDES:-PRINCIPAL}"
log_success "Variables de entorno OK"
echo ""

# 5. Crear directorios necesarios
log_info "Creando directorios..."
mkdir -p cache_sharepoint
mkdir -p .streamlit
log_success "Directorios OK"
echo ""

# 6. Mostrar información del sistema
log_info "Información del sistema:"
echo "  - Hostname: $(hostname)"
echo "  - Usuario: $(whoami)"
echo "  - Directorio: $(pwd)"
echo "  - Espacio disponible: $(df -h . | tail -1 | awk '{print $4}')"
echo ""

# 7. Test rápido de conectividad (opcional)
log_info "Verificando conectividad a internet..."
if curl -s --max-time 5 https://login.microsoftonline.com > /dev/null; then
    log_success "Conectividad OK"
else
    log_warning "Problemas de conectividad - puede afectar SharePoint"
fi
echo ""

# 8. Iniciar Streamlit
log_info "Iniciando Streamlit..."
echo "=========================================="
echo ""

# Ejecutar Streamlit con logs detallados
exec streamlit run app.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --browser.gatherUsageStats=false \
    --logger.level=info \
    2>&1 | tee /tmp/streamlit.log

