#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para subir sitis_consolidado.db a SharePoint
"""

import requests
import os
from msal import ConfidentialClientApplication
import config_sharepoint as config

DB_FILE = 'sitis_consolidado.db'

print("="*70)
print("📤 SUBIR BASE DE DATOS A SHAREPOINT")
print("="*70)

# Verificar que existe el archivo
if not os.path.exists(DB_FILE):
    print(f"❌ Error: No se encuentra el archivo {DB_FILE}")
    print("   Ejecuta primero: python convertir_excel_a_sqlite.py")
    exit(1)

db_size = os.path.getsize(DB_FILE) / (1024 * 1024)
print(f"\n📁 Archivo: {DB_FILE}")
print(f"💾 Tamaño: {db_size:.2f} MB")

# Autenticar
print(f"\n🔐 Autenticando con Azure AD...")
try:
    authority = f"https://login.microsoftonline.com/{config.SHAREPOINT_TENANT_ID}"
    scope = ["https://graph.microsoft.com/.default"]
    
    app = ConfidentialClientApplication(
        config.SHAREPOINT_CLIENT_ID,
        authority=authority,
        client_credential=config.SHAREPOINT_CLIENT_SECRET
    )
    
    result = app.acquire_token_for_client(scopes=scope)
    
    if "access_token" not in result:
        error_msg = result.get('error_description', 'Error desconocido')
        raise Exception(f"Error obteniendo token: {error_msg}")
    
    access_token = result['access_token']
    print("   ✅ Token de acceso obtenido")
    
except Exception as e:
    print(f"   ❌ Error en autenticación: {e}")
    exit(1)

# Obtener Site y Drive IDs
print(f"\n🌐 Conectando a SharePoint...")
try:
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Obtener Site ID
    hostname = config.SHAREPOINT_SITE_URL.replace('https://', '').split('/')[0]
    site_path = '/'.join(config.SHAREPOINT_SITE_URL.replace('https://', '').split('/')[1:])
    
    site_url = f"https://graph.microsoft.com/v1.0/sites/{hostname}:/{site_path}"
    response = requests.get(site_url, headers=headers)
    response.raise_for_status()
    site_id = response.json()['id']
    
    # Obtener Drive ID
    drive_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive"
    response = requests.get(drive_url, headers=headers)
    response.raise_for_status()
    drive_id = response.json()['id']
    
    print(f"   ✅ Conectado a SharePoint")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# Subir archivo
print(f"\n📤 Subiendo archivo a SharePoint...")
print(f"   Ruta destino: {config.SHAREPOINT_DB_PATH}")

try:
    # Para archivos grandes, usar upload session
    if db_size > 4:  # Si es mayor a 4 MB, usar sesión
        print("   📊 Archivo grande, usando sesión de carga...")
        
        # Crear upload session
        upload_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:{config.SHAREPOINT_DB_PATH}:/createUploadSession"
        
        response = requests.post(upload_url, headers=headers)
        response.raise_for_status()
        upload_session = response.json()
        upload_url = upload_session['uploadUrl']
        
        # Subir en chunks de 10 MB
        chunk_size = 10 * 1024 * 1024
        file_size = os.path.getsize(DB_FILE)
        
        with open(DB_FILE, 'rb') as f:
            bytes_uploaded = 0
            
            while bytes_uploaded < file_size:
                chunk_data = f.read(chunk_size)
                chunk_length = len(chunk_data)
                
                content_range = f"bytes {bytes_uploaded}-{bytes_uploaded + chunk_length - 1}/{file_size}"
                
                chunk_headers = {
                    'Content-Length': str(chunk_length),
                    'Content-Range': content_range
                }
                
                response = requests.put(upload_url, headers=chunk_headers, data=chunk_data)
                response.raise_for_status()
                
                bytes_uploaded += chunk_length
                progress = (bytes_uploaded / file_size) * 100
                print(f"   📊 Progreso: {progress:.1f}% ({bytes_uploaded/(1024*1024):.1f}MB/{file_size/(1024*1024):.1f}MB)")
        
    else:
        # Para archivos pequeños, subir directamente
        upload_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:{config.SHAREPOINT_DB_PATH}:/content"
        
        with open(DB_FILE, 'rb') as f:
            file_data = f.read()
        
        headers_upload = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/octet-stream'
        }
        
        response = requests.put(upload_url, headers=headers_upload, data=file_data)
        response.raise_for_status()
    
    print(f"   ✅ Archivo subido exitosamente")
    
except Exception as e:
    print(f"   ❌ Error subiendo archivo: {e}")
    print(f"\n💡 Alternativa: Sube el archivo manualmente:")
    print(f"   1. Ve a: {config.SHAREPOINT_SITE_URL}")
    print(f"   2. Navega a: Analisis de Datos")
    print(f"   3. Sube: {DB_FILE}")
    exit(1)

print(f"\n✅ ¡Proceso completado!")
print(f"\n🚀 Siguiente paso:")
print(f"   1. Commit y push de los cambios de código")
print(f"   2. Redeploy en Easypanel")
print(f"   3. Verificar que la app funcione correctamente")
print("="*70)

