# 🚀 Configuración para Streamlit Cloud

Esta guía te ayudará a desplegar la aplicación SITIS en Streamlit Cloud con acceso seguro a SharePoint.

---

## 📋 Requisitos Previos

1. Cuenta en [Streamlit Cloud](https://share.streamlit.io)
2. Repositorio GitHub con la aplicación (ya tienes: `https://github.com/ndorado1/sitis`)
3. Credenciales de Azure AD para SharePoint

---

## 🔐 Configurar Secrets en Streamlit Cloud

### Paso 1: Desplegar la App

1. Ve a [https://share.streamlit.io](https://share.streamlit.io)
2. Click en **"New app"**
3. Selecciona:
   - **Repository**: `ndorado1/sitis`
   - **Branch**: `main`
   - **Main file path**: `app.py`
4. Click en **"Deploy"**

### Paso 2: Configurar Variables de Entorno (Secrets)

1. En tu app desplegada, click en **"Settings"** (⚙️ arriba a la derecha)
2. Ve a la sección **"Secrets"**
3. Pega la siguiente configuración:

```toml
# Azure AD Application Credentials para SharePoint
# IMPORTANTE: Reemplaza con tus credenciales reales
SHAREPOINT_CLIENT_ID = "tu-client-id-aqui"
SHAREPOINT_CLIENT_SECRET = "tu-client-secret-aqui"
SHAREPOINT_TENANT_ID = "tu-tenant-id-aqui"
```

**NOTA:** Las credenciales reales las encuentras en el documento de configuración seguro del proyecto.

4. Click en **"Save"**
5. La aplicación se reiniciará automáticamente

### Paso 3: Verificar Conexión

1. Espera a que la app se reinicie
2. Observa los logs en Streamlit Cloud
3. Deberías ver: `✅ Conectado a SharePoint con Azure AD`

---

## 📁 Archivos en SharePoint

Asegúrate de que estos archivos estén en SharePoint en la ruta correcta:

**Ruta**: `/Documentos compartidos/Analisis de Datos/BD_SITIS`

Archivos necesarios:
- `DAT_PER.csv`
- `HISTORICO_PYP.csv`
- `CAB_FAC.csv`
- `ACTXPROG_filtrado.csv`

---

## 🔍 Solución de Problemas

### Error: "No hay credenciales configuradas"

- Verifica que los secrets estén correctamente configurados
- Asegúrate de usar el formato TOML correcto (con comillas)
- Reinicia la app manualmente desde Settings → Reboot app

### Error: "Acceso denegado a SharePoint"

- Verifica que la App de Azure tenga permisos en SharePoint
- Confirma que las credenciales sean correctas
- Contacta al administrador de Azure AD

### Error: "Archivo no encontrado"

- Verifica que los archivos estén en la carpeta correcta de SharePoint
- Confirma los nombres de archivo (case-sensitive)
- Revisa la ruta configurada en `config_sharepoint.py`

### La app carga muy lento

- Es normal en la primera carga (archivos grandes)
- Streamlit Cloud tiene límites de memoria (puede ser un problema con CAB_FAC.csv de 561MB)
- Considera optimizar el tamaño de los archivos si es necesario

---

## ⚙️ Configuración Avanzada

### Variables de Entorno Adicionales

Si necesitas configurar más opciones, puedes agregar:

```toml
# Opcionales
USE_SHAREPOINT = true
CACHE_LOCAL = false  # No usar cache local en cloud
```

### Acceso mediante Streamlit Secrets en Código

El código ya está configurado para usar `os.getenv()` que automáticamente lee los secrets de Streamlit Cloud.

---

## 🔒 Seguridad

✅ **Buenas prácticas aplicadas:**
- Credenciales en Secrets (no en el código)
- Secrets no se muestran en logs
- Repositorio público sin credenciales
- Azure AD con permisos mínimos

⚠️ **IMPORTANTE:**
- NUNCA compartas los secrets públicamente
- Rota las credenciales periódicamente
- Solo usuarios autorizados deben tener acceso a la app de Streamlit

---

## 📊 Límites de Streamlit Cloud

| Recurso | Límite Free Tier |
|---------|------------------|
| RAM | 1 GB |
| CPU | Shared |
| Ancho de banda | Ilimitado |
| Apps privadas | 1 |
| Apps públicas | Ilimitadas |

**Nota**: Si la app excede 1GB de RAM, considera:
1. Reducir tamaño de archivos CSV
2. Cargar solo columnas necesarias (ya implementado para CAB_FAC)
3. Usar muestreo de datos si es aceptable
4. Upgrade a plan de pago

---

## 🔄 Actualizar la Aplicación

Cuando hagas cambios en GitHub:

1. **Push a la rama main**: Los cambios se despliegan automáticamente
2. **La app se reinicia**: Automáticamente en 1-2 minutos
3. **Secrets persisten**: No necesitas reconfigurarlos

---

## 📞 Recursos Adicionales

- [Documentación de Streamlit Cloud](https://docs.streamlit.io/streamlit-community-cloud)
- [Secrets Management](https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app/connect-to-data-sources/secrets-management)
- [Azure AD Permissions](https://learn.microsoft.com/en-us/sharepoint/dev/solution-guidance/security-apponly-azuread)

---

## ✅ Checklist de Despliegue

- [ ] Repositorio en GitHub actualizado
- [ ] App creada en Streamlit Cloud  
- [ ] Secrets configurados correctamente
- [ ] Archivos CSV subidos a SharePoint
- [ ] Permisos de Azure AD configurados
- [ ] App reiniciada y funcionando
- [ ] Prueba de búsqueda por paciente exitosa
- [ ] Prueba de búsqueda por actividad exitosa

---

## 🎯 URL de Tu App

Una vez desplegada, tu app estará disponible en:

`https://[tu-app-name].streamlit.app`

Puedes compartir esta URL con usuarios autorizados.

---

¿Necesitas ayuda? Contacta al administrador del proyecto o consulta la documentación de Streamlit Cloud.

