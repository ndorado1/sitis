#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo para cargar archivos CSV desde SharePoint usando Microsoft Graph API
Requiere: pip install msal requests pandas
"""

import pandas as pd
import os
import requests
from io import BytesIO
import streamlit as st

try:
    from msal import ConfidentialClientApplication
    SHAREPOINT_AVAILABLE = True
except ImportError:
    SHAREPOINT_AVAILABLE = False
    print("⚠️ MSAL no está instalado. Usando archivos locales.")

import config_sharepoint as config


class SharePointLoader:
    """Clase para cargar archivos desde SharePoint usando Microsoft Graph API"""
    
    def __init__(self):
        self.use_sharepoint = config.USE_SHAREPOINT and SHAREPOINT_AVAILABLE
        self.access_token = None
        self.site_id = None
        self.drive_id = None
        
        if self.use_sharepoint:
            self._authenticate()
            if self.access_token:
                self._get_site_and_drive_info()
    
    def _authenticate(self):
        """Autenticar con Microsoft Graph usando MSAL"""
        try:
            if config.SHAREPOINT_CLIENT_ID and config.SHAREPOINT_CLIENT_SECRET and config.SHAREPOINT_TENANT_ID:
                print("🔐 Autenticando con Microsoft Graph (MSAL)...")
                
                # Configurar la autoridad y scope
                authority = f'https://login.microsoftonline.com/{config.SHAREPOINT_TENANT_ID}'
                scope = ['https://graph.microsoft.com/.default']
                
                # Crear aplicación confidencial
                app = ConfidentialClientApplication(
                    config.SHAREPOINT_CLIENT_ID,
                    authority=authority,
                    client_credential=config.SHAREPOINT_CLIENT_SECRET
                )
                
                # Adquirir token
                result = app.acquire_token_for_client(scopes=scope)
                
                if "access_token" in result:
                    self.access_token = result['access_token']
                    print("✅ Token de acceso obtenido exitosamente")
                else:
                    error = result.get("error_description", result.get("error", "Error desconocido"))
                    print(f"❌ Error al obtener token: {error}")
                    self.use_sharepoint = False
            else:
                print("⚠️ No hay credenciales configuradas. Usando archivos locales.")
                self.use_sharepoint = False
                
        except Exception as e:
            print(f"❌ Error al conectar con Microsoft Graph: {e}")
            print(f"    Detalles: {str(e)}")
            self.use_sharepoint = False
    
    def _get_site_and_drive_info(self):
        """Obtener el site_id y drive_id del sitio de SharePoint"""
        try:
            # Extraer el hostname y site path de la URL
            # https://mamadominga.sharepoint.com/sites/IntranetHMD
            parts = config.SHAREPOINT_SITE_URL.replace('https://', '').split('/')
            hostname = parts[0]  # mamadominga.sharepoint.com
            site_path = '/'.join(parts[1:])  # sites/IntranetHMD
            
            print(f"📍 Obteniendo información del sitio: {hostname}:/{site_path}")
            
            # Obtener información del sitio
            headers = {'Authorization': f'Bearer {self.access_token}'}
            site_url = f"https://graph.microsoft.com/v1.0/sites/{hostname}:/{site_path}"
            
            response = requests.get(site_url, headers=headers)
            response.raise_for_status()
            
            site_data = response.json()
            self.site_id = site_data['id']
            
            print(f"✅ Site ID obtenido: {self.site_id}")
            
            # Obtener el drive principal del sitio
            drive_url = f"https://graph.microsoft.com/v1.0/sites/{self.site_id}/drive"
            response = requests.get(drive_url, headers=headers)
            response.raise_for_status()
            
            drive_data = response.json()
            self.drive_id = drive_data['id']
            
            print(f"✅ Drive ID obtenido: {self.drive_id}")
            
        except Exception as e:
            print(f"❌ Error al obtener información del sitio/drive: {e}")
            self.use_sharepoint = False
    
    def _list_root_folders(self):
        """Listar carpetas en la raíz del drive para debugging"""
        try:
            headers = {'Authorization': f'Bearer {self.access_token}'}
            list_url = f"https://graph.microsoft.com/v1.0/sites/{self.site_id}/drives/{self.drive_id}/root/children"
            
            response = requests.get(list_url, headers=headers)
            response.raise_for_status()
            
            items = response.json().get('value', [])
            print("\n📂 Carpetas/archivos en la raíz del drive:")
            for item in items:
                item_type = "📁" if item.get('folder') else "📄"
                print(f"   {item_type} {item['name']}")
            print()
            
        except Exception as e:
            print(f"⚠️ No se pudo listar carpetas: {e}")
    
    def _download_file_from_sharepoint(self, file_name, sede_id=None):
        """Descargar un archivo desde SharePoint usando Microsoft Graph API con streaming
        
        Args:
            file_name: Nombre del archivo a descargar
            sede_id: ID de la sede (None para archivos compartidos como catálogo)
        """
        if not self.use_sharepoint or not self.access_token or not self.site_id or not self.drive_id:
            return None
        
        try:
            # Determinar la ruta según si es archivo compartido o por sede
            if file_name in config.ARCHIVOS_CSV_COMPARTIDOS.values():
                # Archivos compartidos (catálogo): usar ruta del catálogo
                folder_path = config.SHAREPOINT_CATALOGO_PATH.strip('/')
            elif sede_id and sede_id in config.SEDES:
                # Archivos por sede: usar carpeta de la sede
                sede_carpeta = config.SEDES[sede_id]['carpeta']
                folder_path = f"{config.SHAREPOINT_BASE_PATH}/{sede_carpeta}".strip('/')
            else:
                # Fallback: usar primera sede disponible
                primera_sede = list(config.SEDES.keys())[0]
                sede_carpeta = config.SEDES[primera_sede]['carpeta']
                folder_path = f"{config.SHAREPOINT_BASE_PATH}/{sede_carpeta}".strip('/')
            
            file_path = f"{folder_path}/{file_name}"
            
            print(f"📡 Streaming: {file_path}")
            
            # Construir la URL de Graph API
            headers = {'Authorization': f'Bearer {self.access_token}'}
            file_url = f"https://graph.microsoft.com/v1.0/sites/{self.site_id}/drives/{self.drive_id}/root:/{file_path}:/content"
            
            # Descargar el archivo con streaming (no carga todo en memoria)
            response = requests.get(file_url, headers=headers, stream=True)
            response.raise_for_status()
            
            # Crear BytesIO y escribir en chunks para evitar cargar todo en memoria
            file_content = BytesIO()
            chunk_size = 8192  # 8KB chunks
            total_bytes = 0
            
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    file_content.write(chunk)
                    total_bytes += len(chunk)
            
            # Volver al inicio para que pandas pueda leerlo
            file_content.seek(0)
            
            # Convertir bytes a MB para mejor legibilidad
            size_mb = total_bytes / (1024 * 1024)
            print(f"✅ {file_name} leído exitosamente ({size_mb:.2f} MB)")
            
            return file_content
        
        except requests.exceptions.HTTPError as e:
            print(f"❌ Error HTTP al leer {file_name}: {e.response.status_code}")
            print(f"    Respuesta: {e.response.text[:200]}")
            return None
        except Exception as e:
            print(f"❌ Error al leer {file_name}: {e}")
            return None
    
    def _save_to_cache(self, file_name, content, sede_id=None):
        """Guardar archivo en cache local
        
        Args:
            file_name: Nombre del archivo
            content: Contenido del archivo (BytesIO)
            sede_id: ID de la sede (None para archivos compartidos)
        """
        if config.CACHE_LOCAL:
            cache_dir = config.CACHE_DIRECTORY
            
            # Crear subdirectorio por sede si es necesario
            if sede_id and file_name not in config.ARCHIVOS_CSV_COMPARTIDOS.values():
                cache_dir = os.path.join(cache_dir, sede_id)
            
            os.makedirs(cache_dir, exist_ok=True)
            
            cache_path = os.path.join(cache_dir, file_name)
            with open(cache_path, 'wb') as f:
                f.write(content.getvalue())
    
    def _load_from_cache(self, file_name, sede_id=None):
        """Cargar archivo desde cache local
        
        Args:
            file_name: Nombre del archivo
            sede_id: ID de la sede (None para archivos compartidos)
        """
        if config.CACHE_LOCAL:
            # Buscar en subdirectorio de sede si aplica
            if sede_id and file_name not in config.ARCHIVOS_CSV_COMPARTIDOS.values():
                cache_path = os.path.join(config.CACHE_DIRECTORY, sede_id, file_name)
            else:
                cache_path = os.path.join(config.CACHE_DIRECTORY, file_name)
            
            if os.path.exists(cache_path):
                return cache_path
        return None
    
    def load_csv(self, csv_key, sede_id=None, encoding='utf-8', **kwargs):
        """
        Cargar un archivo CSV desde SharePoint o local
        
        Args:
            csv_key: Clave del archivo en config.ARCHIVOS_CSV
            sede_id: ID de la sede (None para archivos compartidos como catálogo)
            encoding: Encoding del archivo
            **kwargs: Argumentos adicionales para pd.read_csv
        
        Returns:
            DataFrame de pandas
        """
        file_name = config.ARCHIVOS_CSV.get(csv_key)
        
        if not file_name:
            raise ValueError(f"Archivo no configurado: {csv_key}")
        
        # Determinar si es archivo compartido
        es_compartido = file_name in config.ARCHIVOS_CSV_COMPARTIDOS.values()
        sede_label = "compartido" if es_compartido else f"sede {sede_id}"
        
        # Intentar cargar desde SharePoint
        if self.use_sharepoint:
            print(f"📥 Descargando {file_name} desde SharePoint ({sede_label})...")
            
            file_content = self._download_file_from_sharepoint(file_name, sede_id)
            
            if file_content:
                # Guardar en cache
                self._save_to_cache(file_name, file_content, sede_id)
                
                # Leer CSV con low_memory=False para evitar warnings
                return pd.read_csv(file_content, encoding=encoding, low_memory=False, **kwargs)
        
        # Fallback: intentar cargar desde cache
        cache_path = self._load_from_cache(file_name, sede_id)
        if cache_path:
            print(f"📂 Cargando {file_name} desde cache ({sede_label})...")
            return pd.read_csv(cache_path, encoding=encoding, low_memory=False, **kwargs)
        
        # Fallback final: archivo local
        print(f"📁 Cargando {file_name} desde archivo local...")
        return pd.read_csv(file_name, encoding=encoding, low_memory=False, **kwargs)


# Instancia global del loader
sharepoint_loader = SharePointLoader()


# Funciones helper para usar en app.py
def cargar_csv_sharepoint(csv_key, sede_id=None, encoding='utf-8', **kwargs):
    """
    Función helper para cargar CSV compatible con el código actual
    
    Args:
        csv_key: Clave del archivo en config.ARCHIVOS_CSV
        sede_id: ID de la sede (None para archivos compartidos)
        encoding: Encoding del archivo
        **kwargs: Argumentos adicionales para pd.read_csv
    """
    return sharepoint_loader.load_csv(csv_key, sede_id=sede_id, encoding=encoding, **kwargs)

