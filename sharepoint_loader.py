#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SharePoint SQLite Loader
Descarga y gestiona la base de datos SQLite desde SharePoint
"""

import requests
import os
import sqlite3
import time
from pathlib import Path
from msal import ConfidentialClientApplication
import config_sharepoint as config

class SharePointSQLiteLoader:
    """Clase para descargar y gestionar SQLite desde SharePoint"""
    
    def __init__(self):
        """Inicializa el loader con autenticación de Azure AD"""
        self.access_token = None
        self.site_id = None
        self.drive_id = None
        
        # Crear directorio de cache si no existe
        if config.CACHE_LOCAL:
            os.makedirs(config.CACHE_DIRECTORY, exist_ok=True)
        
        if config.USE_SHAREPOINT:
            print("🔐 Autenticando con SharePoint (Azure AD)...")
            self._authenticate()
            self._get_site_and_drive_ids()
            print("✅ Conectado a SharePoint")
    
    def _authenticate(self):
        """Autentica usando Azure AD con Client ID y Secret"""
        try:
            authority = f"https://login.microsoftonline.com/{config.SHAREPOINT_TENANT_ID}"
            scope = ["https://graph.microsoft.com/.default"]
            
            app = ConfidentialClientApplication(
                config.SHAREPOINT_CLIENT_ID,
                authority=authority,
                client_credential=config.SHAREPOINT_CLIENT_SECRET
            )
            
            result = app.acquire_token_for_client(scopes=scope)
            
            if "access_token" in result:
                self.access_token = result['access_token']
                print("   ✅ Token de acceso obtenido")
            else:
                error_msg = result.get('error_description', 'Error desconocido')
                raise Exception(f"Error obteniendo token: {error_msg}")
                
        except Exception as e:
            print(f"   ❌ Error en autenticación: {e}")
            raise
    
    def _get_site_and_drive_ids(self):
        """Obtiene los IDs del sitio y drive de SharePoint"""
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            # Obtener Site ID
            hostname = config.SHAREPOINT_SITE_URL.replace('https://', '').split('/')[0]
            site_path = '/'.join(config.SHAREPOINT_SITE_URL.replace('https://', '').split('/')[1:])
            
            site_url = f"https://graph.microsoft.com/v1.0/sites/{hostname}:/{site_path}"
            response = requests.get(site_url, headers=headers)
            response.raise_for_status()
            self.site_id = response.json()['id']
            
            # Obtener Drive ID
            drive_url = f"https://graph.microsoft.com/v1.0/sites/{self.site_id}/drive"
            response = requests.get(drive_url, headers=headers)
            response.raise_for_status()
            self.drive_id = response.json()['id']
            
            print(f"   ✅ Site y Drive IDs obtenidos")
            
        except Exception as e:
            print(f"   ❌ Error obteniendo IDs: {e}")
            raise
    
    def _download_file_from_sharepoint(self, file_path, local_path):
        """Descarga un archivo desde SharePoint usando Microsoft Graph API"""
        try:
            print(f"📥 Descargando desde SharePoint: {file_path}")
            
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            
            # URL del archivo en el drive
            file_url = f"https://graph.microsoft.com/v1.0/drives/{self.drive_id}/root:{file_path}:/content"
            
            # Descargar con streaming para archivos grandes
            response = requests.get(file_url, headers=headers, stream=True)
            response.raise_for_status()
            
            # Guardar archivo localmente con barra de progreso
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            chunk_size = 8192
            
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"   📊 Progreso: {progress:.1f}% ({downloaded/(1024*1024):.1f}MB/{total_size/(1024*1024):.1f}MB)", end='\r')
            
            print(f"\n   ✅ Descarga completada: {os.path.getsize(local_path)/(1024*1024):.2f} MB")
            return True
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"   ❌ Archivo no encontrado en SharePoint: {file_path}")
            else:
                print(f"   ❌ Error HTTP: {e}")
            raise
        except Exception as e:
            print(f"   ❌ Error descargando archivo: {e}")
            raise
    
    def _is_cache_valid(self):
        """Verifica si el cache local es válido"""
        if not config.CACHE_LOCAL:
            return False
        
        if not os.path.exists(config.CACHE_DB_PATH):
            return False
        
        # Verificar edad del archivo
        file_age = time.time() - os.path.getmtime(config.CACHE_DB_PATH)
        
        if file_age > config.CACHE_MAX_AGE:
            print(f"⏰ Cache expirado (edad: {file_age/3600:.1f} horas)")
            return False
        
        print(f"✅ Usando cache local (edad: {file_age/3600:.1f} horas)")
        return True
    
    def get_sqlite_connection(self):
        """Obtiene una conexión a la base de datos SQLite
        
        Returns:
            sqlite3.Connection: Conexión a la base de datos
        """
        db_path = config.CACHE_DB_PATH
        
        # Si no usa SharePoint, intentar usar archivo local
        if not config.USE_SHAREPOINT:
            local_db = config.ARCHIVO_SQLITE
            if os.path.exists(local_db):
                print(f"📁 Usando base de datos local: {local_db}")
                return sqlite3.connect(local_db)
            else:
                raise FileNotFoundError(f"No se encuentra la base de datos local: {local_db}")
        
        # Verificar si el cache es válido
        if self._is_cache_valid():
            print(f"💾 Conectando a cache local: {db_path}")
            return sqlite3.connect(db_path)
        
        # Descargar desde SharePoint
        print("🌐 Descargando base de datos desde SharePoint...")
        try:
            self._download_file_from_sharepoint(
                config.SHAREPOINT_DB_PATH,
                db_path
            )
            print(f"✅ Base de datos descargada y lista")
            return sqlite3.connect(db_path)
            
        except Exception as e:
            print(f"❌ Error descargando desde SharePoint: {e}")
            
            # Si falla la descarga pero existe un cache viejo, usarlo
            if os.path.exists(db_path):
                print(f"⚠️  Usando cache antiguo como fallback")
                return sqlite3.connect(db_path)
            
            raise Exception(f"No se pudo descargar la base de datos y no hay cache disponible: {e}")
    
    def clear_cache(self):
        """Elimina el cache local para forzar una nueva descarga"""
        if os.path.exists(config.CACHE_DB_PATH):
            os.remove(config.CACHE_DB_PATH)
            print("🗑️  Cache eliminado")
            return True
        return False

# Instancia global del loader
_loader = None

def get_loader():
    """Obtiene la instancia global del loader (singleton)"""
    global _loader
    if _loader is None:
        _loader = SharePointSQLiteLoader()
    return _loader

def get_sqlite_connection():
    """Función de conveniencia para obtener conexión SQLite"""
    loader = get_loader()
    return loader.get_sqlite_connection()

def clear_cache():
    """Función de conveniencia para limpiar el cache"""
    loader = get_loader()
    return loader.clear_cache()
