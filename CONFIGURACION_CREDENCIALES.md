# 🔐 Configuración de Credenciales para SharePoint

## ⚠️ IMPORTANTE: Seguridad de Credenciales

Las credenciales de Azure AD **NUNCA** deben estar en el código fuente. Este archivo te muestra cómo configurarlas de forma segura.

## 📝 Credenciales del Proyecto

**NOTA**: Las credenciales reales se encuentran en un lugar seguro. Los placeholders en este archivo deben ser reemplazados con los valores reales:

- **Site URL**: `https://mamadominga.sharepoint.com/sites/IntranetHMD`
- **Folder Path**: `/Documentos compartidos/Analisis de Datos/BD_SITIS`
- **Client ID**: Solicitar al administrador
- **Client Secret**: Solicitar al administrador  
- **Tenant ID**: Solicitar al administrador

Si necesitas las credenciales reales, contacta al administrador de Azure AD de Mama Dominga.

---

## 📋 Credenciales Necesarias

Para conectarte a SharePoint de Mama Dominga, necesitas:

- **Client ID**: ID de la aplicación Azure AD
- **Client Secret**: Secret de la aplicación Azure AD  
- **Tenant ID**: ID del tenant de Azure AD

---

## 🔧 Método 1: Variables de Entorno (Recomendado)

### En macOS/Linux:

```bash
# En tu terminal
export SHAREPOINT_CLIENT_ID="tu-client-id-de-azure"
export SHAREPOINT_CLIENT_SECRET="tu-client-secret-de-azure"
export SHAREPOINT_TENANT_ID="tu-tenant-id-de-azure"

# Para hacerlo permanente, agregar al ~/.zshrc o ~/.bashrc
echo 'export SHAREPOINT_CLIENT_ID="tu-client-id-de-azure"' >> ~/.zshrc
echo 'export SHAREPOINT_CLIENT_SECRET="tu-client-secret-de-azure"' >> ~/.zshrc
echo 'export SHAREPOINT_TENANT_ID="tu-tenant-id-de-azure"' >> ~/.zshrc

# Recargar la configuración
source ~/.zshrc
```

### En Windows (PowerShell):

```powershell
$env:SHAREPOINT_CLIENT_ID="tu-client-id-de-azure"
$env:SHAREPOINT_CLIENT_SECRET="tu-client-secret-de-azure"
$env:SHAREPOINT_TENANT_ID="tu-tenant-id-de-azure"
```

### En Windows (CMD):

```cmd
set SHAREPOINT_CLIENT_ID=tu-client-id-de-azure
set SHAREPOINT_CLIENT_SECRET=tu-client-secret-de-azure
set SHAREPOINT_TENANT_ID=tu-tenant-id-de-azure
```

---

## 🔧 Método 2: Archivo .env (Para Desarrollo)

1. **Crear archivo `.env`** en el directorio del proyecto:

```bash
# Crear el archivo
touch .env
```

2. **Editar `.env`** con las credenciales:

```env
SHAREPOINT_CLIENT_ID=tu-client-id-de-azure
SHAREPOINT_CLIENT_SECRET=tu-client-secret-de-azure
SHAREPOINT_TENANT_ID=tu-tenant-id-de-azure
```

3. **Cargar variables** antes de ejecutar la app:

```bash
# Opción A: Cargar manualmente
source .env

# Opción B: Usar python-dotenv (agregar a app.py)
# pip install python-dotenv
# from dotenv import load_dotenv
# load_dotenv()
```

⚠️ **IMPORTANTE**: El archivo `.env` está en `.gitignore` y NO se subirá a GitHub.

---

## 🔧 Método 3: Streamlit Secrets (Para Producción)

Si despliegas en Streamlit Cloud:

1. **Ir a tu app** en https://share.streamlit.io
2. **Settings** → **Secrets**
3. **Agregar**:

```toml
SHAREPOINT_CLIENT_ID = "tu-client-id-de-azure"
SHAREPOINT_CLIENT_SECRET = "tu-client-secret-de-azure"
SHAREPOINT_TENANT_ID = "tu-tenant-id-de-azure"
```

---

## ✅ Verificar Configuración

Ejecuta este comando para verificar que las variables están configuradas:

```bash
# Verificar que las variables estén configuradas
echo $SHAREPOINT_CLIENT_ID
echo $SHAREPOINT_TENANT_ID
# NO muestres el SECRET por seguridad
```

---

## 🚀 Ejecutar la Aplicación

Una vez configuradas las variables de entorno:

```bash
# Activar entorno (si usas Conda)
conda activate sitis-app

# Ejecutar la app
streamlit run app.py
```

La aplicación se conectará automáticamente a SharePoint usando las credenciales configuradas.

---

## 🔒 Mejores Prácticas de Seguridad

✅ **SÍ hacer:**
- Usar variables de entorno
- Usar Streamlit Secrets en producción
- Mantener `.env` en `.gitignore`
- Rotar credenciales periódicamente
- Usar permisos mínimos necesarios

❌ **NO hacer:**
- Hardcodear credenciales en el código
- Subir credenciales a GitHub
- Compartir credenciales en texto plano
- Usar credenciales en repositorios públicos

---

## 🆘 Solución de Problemas

### Error: "No hay credenciales configuradas"

- Verifica que las variables de entorno estén configuradas
- Reinicia el terminal después de configurarlas
- Usa `echo $VARIABLE` para verificar

### Error: "Acceso denegado"

- Verifica que las credenciales sean correctas
- Confirma que la app de Azure tenga permisos en SharePoint
- Contacta al administrador de Azure AD

### Las variables no persisten

- Agrégalas a tu archivo de perfil (~/.zshrc, ~/.bashrc)
- O usa un archivo `.env` con `python-dotenv`

---

## 📞 Contacto

Si necesitas renovar o cambiar las credenciales, contacta al administrador de Azure AD de Mama Dominga.

---

## 🔄 Rotación de Credenciales

Para seguridad, se recomienda rotar el Client Secret cada 6-12 meses:

1. Generar nuevo secret en Azure Portal
2. Actualizar variables de entorno
3. Probar la conexión
4. Revocar el secret antiguo

