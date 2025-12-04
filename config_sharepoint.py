#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuración para SharePoint - SQLite Consolidado
Este archivo contiene la configuración para acceder a la base de datos SQLite desde SharePoint
"""

import os

# ============= CONFIGURACIÓN DE SHAREPOINT =============

# URL del sitio de SharePoint
SHAREPOINT_SITE_URL = "https://mamadominga.sharepoint.com/sites/IntranetHMD"

# Ruta base donde está la base de datos
SHAREPOINT_BASE_PATH = "/Analisis de Datos"

# ============= CONFIGURACIÓN DE BASE DE DATOS =============

# Nombre del archivo SQLite consolidado
ARCHIVO_SQLITE = 'sitis_consolidado.db'

# Ruta completa en SharePoint
SHAREPOINT_DB_PATH = f"{SHAREPOINT_BASE_PATH}/{ARCHIVO_SQLITE}"

# ============= AUTENTICACIÓN =============

# Autenticación con Azure AD (App Registration)
SHAREPOINT_CLIENT_ID = os.getenv('SHAREPOINT_CLIENT_ID', '')
SHAREPOINT_CLIENT_SECRET = os.getenv('SHAREPOINT_CLIENT_SECRET', '')
SHAREPOINT_TENANT_ID = os.getenv('SHAREPOINT_TENANT_ID', '')

# ============= MODO DE OPERACIÓN =============

# Si True, intenta leer desde SharePoint. Si False, lee archivo local
USE_SHAREPOINT = True

# Cache local de la base de datos (para mejorar rendimiento)
CACHE_LOCAL = True
CACHE_DIRECTORY = './cache_sharepoint'
CACHE_DB_PATH = f"{CACHE_DIRECTORY}/{ARCHIVO_SQLITE}"

# Tiempo de vida del cache en segundos (24 horas = 86400)
# Si el archivo tiene más de este tiempo, se descarga de nuevo
CACHE_MAX_AGE = 86400
