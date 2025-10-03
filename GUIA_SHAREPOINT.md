# 📘 Guía de Configuración de SharePoint

Esta guía te ayudará a configurar la aplicación para leer los archivos CSV desde SharePoint.

## 🎯 Ventajas de usar SharePoint

✅ **Seguridad**: Control de acceso corporativo  
✅ **No ocupa espacio en GitHub**: Los archivos grandes quedan en SharePoint  
✅ **Versionamiento**: Historial de cambios de archivos  
✅ **Auditoría**: Registro de quién accede a los datos  
✅ **Centralizado**: Un solo lugar para todos los datos

---

## 📋 Requisitos Previos

1. Acceso a SharePoint de tu organización
2. Permisos de lectura en la carpeta con los archivos CSV
3. Python 3.10 instalado
4. Dependencias instaladas: `pip install Office365-REST-Python-Client`

---

## 🔧 Paso 1: Subir Archivos a SharePoint

1. **Crear una carpeta en SharePoint** (ej: `SITIS/datos`)
2. **Subir los archivos CSV**:
   - `DAT_PER.csv`
   - `HISTORICO_PYP.csv`
   - `CAB_FAC.csv`
   - `ACTXPROG.csv` (opcional, ya está filtrado en el repo)

3. **Configurar permisos**:
   - Solo usuarios autorizados deben tener acceso
   - Permisos de lectura son suficientes

---

## ⚙️ Paso 2: Configurar la Aplicación

### Opción A: Configuración Básica (Usuario y Contraseña)

1. **Editar `config_sharepoint.py`**:

```python
# URL de tu sitio de SharePoint
SHAREPOINT_SITE_URL = "https://tu-organizacion.sharepoint.com/sites/SITIS"

# Ruta donde están los archivos
SHAREPOINT_FOLDER_PATH = "/Documentos Compartidos/SITIS/datos"

# Habilitar SharePoint
USE_SHAREPOINT = True
```

2. **Configurar credenciales** (variables de entorno - RECOMENDADO):

```bash
# En tu terminal o .bashrc / .zshrc
export SHAREPOINT_USER="tu-email@organizacion.com"
export SHAREPOINT_PASS="tu-contraseña"
```

### Opción B: Usando Azure AD App (Más Seguro)

Si tu organización usa Azure AD, puedes registrar una aplicación:

1. **Registrar app en Azure AD**: https://portal.azure.com
2. **Obtener credenciales**:
   - Client ID
   - Client Secret
   - Tenant ID

3. **Configurar en `config_sharepoint.py`**:

```python
SHAREPOINT_CLIENT_ID = "tu-client-id"
SHAREPOINT_CLIENT_SECRET = "tu-client-secret"
SHAREPOINT_TENANT_ID = "tu-tenant-id"
```

---

## 🚀 Paso 3: Usar la Aplicación

### Modo SharePoint (Recomendado para producción)

```bash
# Activar modo SharePoint
export USE_SHAREPOINT=True

# Ejecutar la aplicación
streamlit run app.py
```

### Modo Local (Para desarrollo/testing)

```bash
# Los archivos CSV deben estar en el directorio local
streamlit run app.py
```

### Modo Híbrido (Con Cache)

La aplicación puede usar cache local para mejorar el rendimiento:

```python
# En config_sharepoint.py
CACHE_LOCAL = True
CACHE_DIRECTORY = './cache_sharepoint'
```

**Ventajas del cache**:
- Descarga archivos una vez
- Siguientes ejecuciones son más rápidas
- Funciona offline después de la primera carga

---

## 🔐 Seguridad

### ⚠️ NUNCA hagas esto:

❌ Subir credenciales al repositorio  
❌ Compartir el archivo `config_sharepoint_local.py`  
❌ Usar contraseñas en texto plano en el código

### ✅ Mejores Prácticas:

✅ Usar variables de entorno  
✅ Usar Azure AD con permisos mínimos  
✅ Rotar credenciales periódicamente  
✅ Usar autenticación multifactor  
✅ Mantener el `.gitignore` actualizado

---

## 🐛 Solución de Problemas

### Error: "Office365-REST-Python-Client no está instalado"

```bash
pip install Office365-REST-Python-Client
```

### Error: "Acceso denegado"

- Verifica que tienes permisos en SharePoint
- Confirma que la URL y ruta son correctas
- Revisa que las credenciales sean válidas

### Error: "Archivo no encontrado"

- Verifica que los nombres de archivo en `config_sharepoint.py` coincidan exactamente
- Confirma la ruta de la carpeta en SharePoint
- Usa rutas relativas al sitio (empiezan con `/`)

### Los archivos tardan mucho en cargar

- Habilita el cache local: `CACHE_LOCAL = True`
- Los archivos se descargarán una vez y se reutilizarán

---

## 📊 Ejemplo de Estructura en SharePoint

```
https://tu-org.sharepoint.com/sites/SITIS
│
└── Documentos Compartidos/
    └── SITIS/
        └── datos/
            ├── DAT_PER.csv (13 MB)
            ├── HISTORICO_PYP.csv (40 MB)
            ├── CAB_FAC.csv (561 MB)
            └── ACTXPROG.csv (203 KB)
```

---

## 🔄 Actualizar Archivos

Cuando actualices los archivos CSV en SharePoint:

1. **Si usas cache**: Elimina la carpeta `cache_sharepoint/`
2. **Reinicia la aplicación**: Los nuevos archivos se descargarán

```bash
# Limpiar cache
rm -rf cache_sharepoint/

# Reiniciar app
streamlit run app.py
```

---

## 📞 Soporte

Si tienes problemas:

1. Verifica los logs de la aplicación
2. Confirma acceso a SharePoint desde el navegador
3. Revisa los permisos de la carpeta
4. Contacta al administrador de SharePoint de tu organización

---

## 🎓 Recursos Adicionales

- [Office365-REST-Python-Client Docs](https://github.com/vgrem/Office365-REST-Python-Client)
- [SharePoint REST API](https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/get-to-know-the-sharepoint-rest-service)
- [Azure AD App Registration](https://learn.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app)

