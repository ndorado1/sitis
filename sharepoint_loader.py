#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo para cargar archivos CSV desde SharePoint
Requiere: pip install Office365-REST-Python-Client
"""

import pandas as pd
import os
from io import BytesIO
import streamlit as st

try:
    from office365.sharepoint.client_context import ClientContext
    from office365.runtime.auth.user_credential import UserCredential
    from office365.runtime.auth.client_credential import ClientCredential
    SHAREPOINT_AVAILABLE = True
except ImportError:
    SHAREPOINT_AVAILABLE = False
    print("⚠️ Office365-REST-Python-Client no está instalado. Usando archivos locales.")

import config_sharepoint as config


class SharePointLoader:
    """Clase para cargar archivos desde SharePoint"""
    
    def __init__(self):
        self.use_sharepoint = config.USE_SHAREPOINT and SHAREPOINT_AVAILABLE
        self.ctx = None
        
        if self.use_sharepoint:
            self._authenticate()
    
    def _authenticate(self):
        """Autenticar con SharePoint usando Azure AD App"""
        try:
            # Autenticación con Azure AD usando Client Credentials
            if config.SHAREPOINT_CLIENT_ID and config.SHAREPOINT_CLIENT_SECRET and config.SHAREPOINT_TENANT_ID:
                print("🔐 Autenticando con Azure AD (App Registration)...")
                credentials = ClientCredential(
                    config.SHAREPOINT_CLIENT_ID,
                    config.SHAREPOINT_CLIENT_SECRET
                )
                self.ctx = ClientContext(config.SHAREPOINT_SITE_URL).with_credentials(credentials)
                print("✅ Conectado a SharePoint con Azure AD")
            
            # Fallback: usuario y contraseña (menos común en producción)
            elif config.SHAREPOINT_USERNAME and config.SHAREPOINT_PASSWORD:
                print("🔐 Autenticando con usuario y contraseña...")
                credentials = UserCredential(
                    config.SHAREPOINT_USERNAME,
                    config.SHAREPOINT_PASSWORD
                )
                self.ctx = ClientContext(config.SHAREPOINT_SITE_URL).with_credentials(credentials)
                print("✅ Conectado a SharePoint con credenciales de usuario")
            
            else:
                print("⚠️ No hay credenciales configuradas. Usando archivos locales.")
                self.use_sharepoint = False
                
        except Exception as e:
            print(f"❌ Error al conectar con SharePoint: {e}")
            print(f"    Detalles: {str(e)}")
            self.use_sharepoint = False
    
    def _download_file_from_sharepoint(self, file_name):
        """Descargar un archivo desde SharePoint"""
        if not self.use_sharepoint or not self.ctx:
            return None
        
        try:
            # Construir la ruta completa del archivo
            file_url = f"{config.SHAREPOINT_FOLDER_PATH}/{file_name}"
            
            # Descargar el archivo
            response = self.ctx.web.get_file_by_server_relative_url(file_url).download()
            self.ctx.execute_query()
            
            return BytesIO(response.content)
        
        except Exception as e:
            print(f"❌ Error al descargar {file_name}: {e}")
            return None
    
    def _save_to_cache(self, file_name, content):
        """Guardar archivo en cache local"""
        if config.CACHE_LOCAL:
            cache_dir = config.CACHE_DIRECTORY
            os.makedirs(cache_dir, exist_ok=True)
            
            cache_path = os.path.join(cache_dir, file_name)
            with open(cache_path, 'wb') as f:
                f.write(content.getvalue())
    
    def _load_from_cache(self, file_name):
        """Cargar archivo desde cache local"""
        if config.CACHE_LOCAL:
            cache_path = os.path.join(config.CACHE_DIRECTORY, file_name)
            if os.path.exists(cache_path):
                return cache_path
        return None
    
    def load_csv(self, csv_key, encoding='utf-8', **kwargs):
        """
        Cargar un archivo CSV desde SharePoint o local
        
        Args:
            csv_key: Clave del archivo en config.ARCHIVOS_CSV
            encoding: Encoding del archivo
            **kwargs: Argumentos adicionales para pd.read_csv
        
        Returns:
            DataFrame de pandas
        """
        file_name = config.ARCHIVOS_CSV.get(csv_key)
        
        if not file_name:
            raise ValueError(f"Archivo no configurado: {csv_key}")
        
        # Intentar cargar desde SharePoint
        if self.use_sharepoint:
            print(f"📥 Descargando {file_name} desde SharePoint...")
            
            file_content = self._download_file_from_sharepoint(file_name)
            
            if file_content:
                # Guardar en cache
                self._save_to_cache(file_name, file_content)
                
                # Leer CSV
                return pd.read_csv(file_content, encoding=encoding, **kwargs)
        
        # Fallback: intentar cargar desde cache
        cache_path = self._load_from_cache(file_name)
        if cache_path:
            print(f"📂 Cargando {file_name} desde cache...")
            return pd.read_csv(cache_path, encoding=encoding, **kwargs)
        
        # Fallback final: archivo local
        print(f"📁 Cargando {file_name} desde archivo local...")
        return pd.read_csv(file_name, encoding=encoding, **kwargs)


# Instancia global del loader
sharepoint_loader = SharePointLoader()


# Funciones helper para usar en app.py
def cargar_csv_sharepoint(csv_key, encoding='utf-8', **kwargs):
    """
    Función helper para cargar CSV compatible con el código actual
    """
    return sharepoint_loader.load_csv(csv_key, encoding=encoding, **kwargs)

