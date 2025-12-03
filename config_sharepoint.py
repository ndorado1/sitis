#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuración para SharePoint - Multi-Sede
Este archivo contiene la configuración para acceder a los archivos CSV desde SharePoint
soportando múltiples sedes con catálogo de actividades compartido
"""

# ============= CONFIGURACIÓN DE SHAREPOINT =============

# URL del sitio de SharePoint
SHAREPOINT_SITE_URL = "https://mamadominga.sharepoint.com/sites/IntranetHMD"

# Ruta base donde están las carpetas de las sedes
SHAREPOINT_BASE_PATH = "/Analisis de Datos"

# ============= CONFIGURACIÓN DE SEDES =============

# Definición de sedes disponibles
# Cada sede tiene un ID único y una carpeta en SharePoint
SEDES = {
    'PRINCIPAL': {
        'nombre': 'Sede Principal',
        'carpeta': 'BD_SITIS',
        'descripcion': 'Hospital Madre Dominga - Sede Principal'
    },
    'PIENDAMO': {
        'nombre': 'Sede Piéndamo',
        'carpeta': 'BD_SITIS_PIENDAMO',
        'descripcion': 'Hospital Madre Dominga - Piéndamo (Consolidado Vieja + Final)'
    },
    'SILVIA': {
        'nombre': 'Sede Silvia',
        'carpeta': 'BD_SITIS_SILVIA',
        'descripcion': 'Hospital Madre Dominga - Silvia (Consolidado Vieja + Nueva)'
    },
}

# Carpeta donde está el catálogo de actividades compartido
SHAREPOINT_CATALOGO_PATH = "/Analisis de Datos/BD_SITIS"  # Mantener en la carpeta actual

# Nombres de los archivos en SharePoint (específicos por sede)
ARCHIVOS_CSV_SEDE = {
    'DAT_PER': 'DAT_PER.csv',
    'HISTORICO_PYP': 'HISTORICO_PYP.csv',
    'CAB_FAC': 'CAB_FAC.csv',
}

# Nombres de archivos compartidos (catálogo único)
ARCHIVOS_CSV_COMPARTIDOS = {
    'ACTXPROG': 'ACTXPROG.csv',
    'ACTXPROG_FILTRADO': 'ACTXPROG_filtrado.csv'
}

# Todos los archivos juntos (para compatibilidad)
ARCHIVOS_CSV = {
    **ARCHIVOS_CSV_SEDE,
    **ARCHIVOS_CSV_COMPARTIDOS
}

# ============= AUTENTICACIÓN =============

# Opción 1: Autenticación con usuario y contraseña
# NOTA: NO subir este archivo a GitHub con credenciales reales
SHAREPOINT_USERNAME = ""  # Tu email corporativo
SHAREPOINT_PASSWORD = ""  # Tu contraseña (mejor usar variables de entorno)

# Opción 2: Usar variables de entorno (Recomendado para producción)
import os
SHAREPOINT_USERNAME = os.getenv('SHAREPOINT_USER', '')
SHAREPOINT_PASSWORD = os.getenv('SHAREPOINT_PASS', '')

# Opción 3: Cliente ID y Secret (Para apps registradas en Azure AD)
SHAREPOINT_CLIENT_ID = os.getenv('SHAREPOINT_CLIENT_ID', '')
SHAREPOINT_CLIENT_SECRET = os.getenv('SHAREPOINT_CLIENT_SECRET', '')
SHAREPOINT_TENANT_ID = os.getenv('SHAREPOINT_TENANT_ID', '')

# ============= MODO DE OPERACIÓN =============

# Si True, intenta leer desde SharePoint. Si False, lee archivos locales
USE_SHAREPOINT = True  # Activado para usar SharePoint

# Modo de carga de sedes (para control en producción)
# 'ALL' = Cargar todas las sedes | 'PRINCIPAL' = Solo sede principal
MODO_CARGA_SEDES = os.getenv('MODO_CARGA_SEDES', 'PRINCIPAL')  # Por defecto solo principal

# Cache local de archivos (para mejorar rendimiento)
CACHE_LOCAL = True
CACHE_DIRECTORY = './cache_sharepoint'

