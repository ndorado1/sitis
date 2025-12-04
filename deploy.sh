#!/bin/bash
# Script de despliegue para aplicación SITIS en Docker

set -e  # Exit on error

echo "🚀 Despliegue de Aplicación SITIS con Docker"
echo "============================================"
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar que estamos en el directorio correcto
if [ ! -f "app.py" ]; then
    echo -e "${RED}❌ Error: No se encuentra app.py${NC}"
    echo "Por favor ejecuta este script desde el directorio del proyecto"
    exit 1
fi

# Verificar si Docker está instalado
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker no está instalado${NC}"
    echo "Instala Docker primero: https://docs.docker.com/get-docker/"
    exit 1
fi

# Verificar si Docker Compose está instalado
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose no está instalado${NC}"
    echo "Instala Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# Verificar archivo .env
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  No se encuentra archivo .env${NC}"
    echo "Creando desde env.example..."
    
    if [ -f "env.example" ]; then
        cp env.example .env
        echo -e "${GREEN}✅ Archivo .env creado${NC}"
        echo ""
        echo -e "${YELLOW}📝 IMPORTANTE: Edita .env y configura tus credenciales antes de continuar${NC}"
        echo "Usa: nano .env  o  vim .env"
        echo ""
        read -p "¿Ya configuraste las credenciales en .env? (s/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[SsYy]$ ]]; then
            echo "Por favor configura .env y vuelve a ejecutar el script"
            exit 1
        fi
    else
        echo -e "${RED}❌ No se encuentra env.example${NC}"
        exit 1
    fi
fi

# Cargar variables de entorno
source .env

# Verificar que las credenciales estén configuradas
if [ "$SHAREPOINT_CLIENT_ID" = "tu-client-id-aqui" ] || [ -z "$SHAREPOINT_CLIENT_ID" ]; then
    echo -e "${RED}❌ Error: Credenciales no configuradas en .env${NC}"
    echo "Edita el archivo .env y configura las credenciales correctas"
    exit 1
fi

echo -e "${GREEN}✅ Credenciales configuradas${NC}"
echo ""

# Menú de opciones
echo "Selecciona una opción:"
echo "1) Construir y desplegar (primera vez o actualización)"
echo "2) Iniciar contenedor existente"
echo "3) Detener contenedor"
echo "4) Ver logs"
echo "5) Reconstruir desde cero (limpia cache)"
echo "6) Estado del contenedor"
echo "7) Salir"
echo ""
read -p "Opción: " option

case $option in
    1)
        echo ""
        echo "🔨 Construyendo imagen Docker..."
        docker-compose build --no-cache
        
        echo ""
        echo "🚀 Iniciando contenedor..."
        docker-compose up -d
        
        echo ""
        echo -e "${GREEN}✅ Aplicación desplegada exitosamente${NC}"
        echo ""
        echo "📊 Accede a la aplicación en:"
        echo "   http://localhost:8501"
        echo "   http://$(hostname -I | awk '{print $1}'):8501"
        echo ""
        echo "📝 Ver logs: docker-compose logs -f"
        ;;
        
    2)
        echo ""
        echo "▶️  Iniciando contenedor..."
        docker-compose up -d
        echo -e "${GREEN}✅ Contenedor iniciado${NC}"
        ;;
        
    3)
        echo ""
        echo "⏸️  Deteniendo contenedor..."
        docker-compose down
        echo -e "${GREEN}✅ Contenedor detenido${NC}"
        ;;
        
    4)
        echo ""
        echo "📝 Mostrando logs (Ctrl+C para salir)..."
        docker-compose logs -f
        ;;
        
    5)
        echo ""
        echo "🧹 Limpiando cache y reconstruyendo..."
        docker-compose down -v
        rm -rf cache_sharepoint/*
        docker-compose build --no-cache
        docker-compose up -d
        echo -e "${GREEN}✅ Reconstrucción completa exitosa${NC}"
        ;;
        
    6)
        echo ""
        echo "📊 Estado del contenedor:"
        docker-compose ps
        echo ""
        echo "💾 Uso de recursos:"
        docker stats --no-stream sitis-streamlit || echo "Contenedor no está ejecutándose"
        ;;
        
    7)
        echo "👋 Saliendo..."
        exit 0
        ;;
        
    *)
        echo -e "${RED}❌ Opción inválida${NC}"
        exit 1
        ;;
esac

echo ""
echo "✨ Listo!"


