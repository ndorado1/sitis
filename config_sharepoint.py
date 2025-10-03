#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuración para SharePoint
Este archivo contiene la configuración para acceder a los archivos CSV desde SharePoint
"""

# ============= CONFIGURACIÓN DE SHAREPOINT =============

# URL del sitio de SharePoint
SHAREPOINT_SITE_URL = "https://tu-organizacion.sharepoint.com/sites/tu-sitio"

# Ruta de la carpeta donde están los archivos CSV
SHAREPOINT_FOLDER_PATH = "/Documentos Compartidos/SITIS/datos"

# Nombres de los archivos en SharePoint
ARCHIVOS_CSV = {
    'DAT_PER': 'DAT_PER.csv',
    'HISTORICO_PYP': 'HISTORICO_PYP.csv',
    'CAB_FAC': 'CAB_FAC.csv',
    'ACTXPROG': 'ACTXPROG.csv'
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
USE_SHAREPOINT = False  # Cambiar a True cuando esté configurado

# Cache local de archivos (para mejorar rendimiento)
CACHE_LOCAL = True
CACHE_DIRECTORY = './cache_sharepoint'

