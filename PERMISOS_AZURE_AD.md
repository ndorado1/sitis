# 🔐 Configurar Permisos de Azure AD para SharePoint

## ❌ Problema Actual: Error 401 Unauthorized

Tu aplicación se conecta exitosamente a SharePoint, pero recibe un error **401 Unauthorized** al intentar descargar archivos.

**Esto significa que la App de Azure AD necesita permisos adicionales.**

---

## ✅ Solución: Configurar Permisos en Azure Portal

### Paso 1: Ir a Azure Portal

1. Ve a [https://portal.azure.com](https://portal.azure.com)
2. Inicia sesión con tu cuenta de Mama Dominga
3. Busca "App registrations" o "Registros de aplicaciones"
4. Encuentra tu app: **ID: `9adb57f4-7018-4dc3-96c7-e8532d083a2c`**

### Paso 2: Agregar Permisos de SharePoint

1. En tu app, ve a **"API permissions"** (Permisos de API)
2. Click en **"Add a permission"** (Agregar un permiso)
3. Selecciona **"SharePoint"**
4. Selecciona **"Application permissions"** (NO Delegated)
5. Busca y agrega estos permisos:

#### Permisos Necesarios:
- ✅ **Sites.Read.All** - Leer todos los sitios
- ✅ **Sites.Selected** - Acceder a sitios específicos (alternativa más segura)

**O** (más permisivo pero funciona seguro):
- ✅ **Sites.FullControl.All** - Control total (solo si los otros no funcionan)

### Paso 3: Otorgar Consentimiento de Administrador

1. Después de agregar los permisos, click en **"Grant admin consent for [tu organización]"**
2. Confirma con **"Yes"**
3. Verás un checkmark verde ✅ en cada permiso

### Paso 4: (Alternativa) Dar Permisos Directamente al Sitio

Si no puedes agregar permisos globales, puedes dar acceso al sitio específico:

1. Ve a tu sitio de SharePoint: `https://mamadominga.sharepoint.com/sites/IntranetHMD`
2. Settings ⚙️ → Site permissions → Advanced permissions settings
3. Agregar la app usando su **Client ID**: `9adb57f4-7018-4dc3-96c7-e8532d083a2c`
4. Darle permisos de **Lectura** (Read) o **Contribución** (Contribute)

---

## 🔧 Verificar Configuración Actual

### Verificar Permisos Actuales:

1. Azure Portal → Tu App → API permissions
2. Deberías ver algo como:

```
API / Permissions name                Type          Status
──────────────────────────────────────────────────────────
Microsoft Graph
  User.Read                          Delegated     ✅ Granted
  
SharePoint
  Sites.Read.All                     Application   ✅ Granted
```

### Verificar Acceso al Sitio:

Puedes probar el acceso manualmente:

1. Ve a: `https://mamadominga.sharepoint.com/sites/IntranetHMD/Documentos compartidos/Analisis de Datos/BD_SITIS`
2. Verifica que los archivos CSV estén ahí
3. Intenta descargar uno manualmente para confirmar acceso

---

## 🔄 Después de Configurar Permisos

1. **No necesitas regenerar credenciales** - El Client ID y Secret siguen siendo los mismos
2. **Reinicia tu aplicación Streamlit** - Los nuevos permisos se aplicarán
3. **Prueba la conexión** - Deberías ver:
   ```
   ✅ ACTXPROG_filtrado.csv descargado exitosamente desde SharePoint
   ```

---

## 📋 Checklist de Permisos

- [ ] App registrada en Azure AD
- [ ] Permisos de SharePoint agregados (Sites.Read.All o Sites.Selected)
- [ ] Consentimiento de administrador otorgado (checkmark verde)
- [ ] Archivos CSV están en SharePoint en la ruta correcta
- [ ] La app tiene acceso al sitio específico
- [ ] Aplicación reiniciada después de cambios

---

## 🆘 Si Aún No Funciona

### Revisar URL del Archivo:

La aplicación ahora muestra la ruta completa. Busca en los logs:
```
📍 Ruta completa: /sites/IntranetHMD/Documentos compartidos/Analisis de Datos/BD_SITIS/DAT_PER.csv
```

Verifica que esta ruta coincida exactamente con la ubicación real en SharePoint.

### Errores Comunes:

1. **Espacios en la ruta**: "Documentos compartidos" debe tener el espacio
2. **Mayúsculas/minúsculas**: Deben coincidir exactamente
3. **Permisos insuficientes**: Necesitas ser administrador para otorgar consentimiento
4. **Sitio privado**: El sitio debe permitir acceso a apps

### Contactar al Administrador:

Si no tienes permisos de administrador en Azure AD:

**Pide al administrador de TI que:**
1. Agregue los permisos de SharePoint a tu app
2. Otorgue el consentimiento de administrador
3. O agregue la app directamente al sitio de SharePoint

---

## 📞 Información para el Administrador

**App Details:**
- App Name: [Tu nombre de app]
- Application (client) ID: `9adb57f4-7018-4dc3-96c7-e8532d083a2c`
- Tenant ID: `e3863c71-f8df-45c3-9edc-655652e3d002`

**Permisos necesarios:**
- SharePoint → Application → Sites.Read.All
- Consentimiento de administrador requerido

**Sitio a acceder:**
- URL: `https://mamadominga.sharepoint.com/sites/IntranetHMD`
- Carpeta: `/Documentos compartidos/Analisis de Datos/BD_SITIS`
- Tipo de acceso: Solo lectura (Read)

---

## 🔒 Seguridad

Los permisos solicitados son:
- ✅ **Solo lectura** - La app NO puede modificar o eliminar archivos
- ✅ **Específicos al sitio** - Solo acceso a IntranetHMD
- ✅ **Auditables** - Todos los accesos quedan registrados en Azure AD

---

## 📚 Referencias

- [Azure AD App Permissions](https://learn.microsoft.com/en-us/azure/active-directory/develop/v2-permissions-and-consent)
- [SharePoint App-Only Access](https://learn.microsoft.com/en-us/sharepoint/dev/solution-guidance/security-apponly-azuread)
- [Grant Admin Consent](https://learn.microsoft.com/en-us/azure/active-directory/manage-apps/grant-admin-consent)

