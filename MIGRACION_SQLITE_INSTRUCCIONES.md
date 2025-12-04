# 🚀 Instrucciones de Deployment - Migración a SQLite

## ✅ Estado Actual

La migración está **COMPLETA** y lista para deployment:

- ✅ Base de datos generada: `sitis_consolidado.db` (124 MB)
- ✅ Código actualizado y pusheado a GitHub
- ✅ Tests locales pasados exitosamente
- ✅ Caso de prueba validado (25690751 con datos 2024-2025)

---

## 📋 Pasos para Deployment

### 1️⃣ **Subir Base de Datos a SharePoint**

Tienes 2 opciones:

#### **Opción A: Subida Manual (Recomendado - Más Rápido)**

1. Ve a: https://mamadominga.sharepoint.com/sites/IntranetHMD
2. Navega a: **Documentos compartidos → Analisis de Datos**
3. Arrastra y suelta el archivo `sitis_consolidado.db` (124 MB)
4. Espera a que termine la subida (puede tardar 2-5 minutos dependiendo de tu conexión)

#### **Opción B: Script Automático**

```bash
cd "/Users/personal/HMD/Consolidacion SITIS"
export SHAREPOINT_CLIENT_ID="<tu-client-id>"
export SHAREPOINT_CLIENT_SECRET="<tu-client-secret>"
export SHAREPOINT_TENANT_ID="<tu-tenant-id>"
python3 subir_db_sharepoint.py
```

**Nota:** Las credenciales reales están en `CREDENCIALES_STREAMLIT.txt` (archivo local, no en GitHub)

---

### 2️⃣ **Redeploy en Easypanel**

1. Ve a tu aplicación en Easypanel
2. Click en **"Redeploy"** o **"Rebuild"**
3. Espera 2-3 minutos mientras:
   - Descarga el código nuevo de GitHub
   - Instala las dependencias actualizadas
   - Construye la imagen Docker

---

### 3️⃣ **Verificación Post-Deployment**

Una vez que la app esté corriendo:

#### **Test 1: Acceso Básico**
- Abre la URL de tu app
- Verifica que cargue sin errores
- Debería ver: "✅ Base de datos cargada correctamente"

#### **Test 2: Caso de Prueba - LILIANA TUNUBALA TOMBE**
1. Ve a la tab **"🔍 Buscar por Paciente"**
2. Ingresa documento: `25690751`
3. Click **"🔍 Buscar"**

**Resultados Esperados:**
- ✅ Nombre: **LILIANA TUNUBALA TOMBE** (no JOSE ANTONIO)
- ✅ Última atención: **2025-07-23** (o posterior)
- ✅ Ver atenciones de 2024 y 2025 en la lista
- ✅ Total de atenciones: ~14 registros

#### **Test 3: Búsqueda por Actividad**
1. Ve a la tab **"📊 Buscar por Actividad"**
2. Selecciona cualquier actividad
3. Click **"🔍 Buscar Pacientes"**
4. Deberías ver una lista de pacientes con fechas recientes (2025)

---

## 🎯 Cambios Principales

### **Arquitectura Anterior:**
```
SharePoint
├── BD_SITIS/ (Sede Principal)
│   ├── DAT_PER.csv
│   ├── HISTORICO_PYP.csv
│   ├── CAB_FAC.csv
│   └── ACTXPROG_filtrado.csv
├── BD_SITIS_PIENDAMO/
│   └── ... (3 archivos)
└── BD_SITIS_SILVIA/
    └── ... (3 archivos)

Total: 9 archivos CSV (~600 MB)
Problema: Datos desactualizados (solo hasta 2023)
```

### **Arquitectura Nueva:**
```
SharePoint
└── Analisis de Datos/
    └── sitis_consolidado.db (124 MB)

Total: 1 archivo SQLite
Ventaja: Datos actualizados hasta 2025-07-31
```

---

## 📊 Estadísticas de la Base de Datos

- **Total de atenciones**: 314,234
- **Pacientes únicos**: 18,993
- **Actividades diferentes**: 373
- **Período**: 2020-01-01 a 2025-07-31
- **Tamaño**: 124.09 MB
- **Performance**: 
  - Búsqueda por documento: < 1 ms
  - Búsqueda por actividad: < 120 ms
  - Estadísticas generales: < 2 ms

---

## 🔧 Troubleshooting

### **Problema: "❌ Error al cargar la base de datos"**

**Solución:**
1. Verifica que `sitis_consolidado.db` esté en SharePoint:
   - Ruta: `/Analisis de Datos/sitis_consolidado.db`
2. En la app, click en **"ℹ️ Información del sistema"**
3. Click en **"🔄 Actualizar Base de Datos"** para limpiar cache
4. Si persiste, revisa los logs de Easypanel

### **Problema: "No aparecen datos de 2025"**

**Solución:**
1. Verifica que subiste el archivo `sitis_consolidado.db` correcto
2. Verifica el tamaño del archivo en SharePoint (debe ser ~124 MB)
3. En la app, limpia el cache con el botón "🔄 Actualizar Base de Datos"

### **Problema: "La app está muy lenta"**

**Causas posibles:**
1. Primera carga (descargando 124 MB desde SharePoint)
   - Espera 2-3 minutos en la primera carga
2. Cache expirado (se recarga cada 24 horas)
   - Normal, solo la primera consulta del día es lenta

---

## 🎉 Beneficios de la Migración

### **Antes:**
- ❌ 9 archivos CSV separados
- ❌ Datos solo hasta 2023
- ❌ IDs duplicados entre sedes
- ❌ Búsquedas lentas en CSV grandes
- ❌ Arquitectura compleja

### **Ahora:**
- ✅ 1 archivo SQLite consolidado
- ✅ Datos actualizados hasta 2025-07-31
- ✅ IDs únicos regenerados
- ✅ Búsquedas optimizadas con índices SQL
- ✅ Arquitectura simple y mantenible
- ✅ 80% menos tamaño (124 MB vs 600 MB)

---

## 📝 Notas Importantes

1. **Archivo Excel Original:**
   - `consolidado_sitis.xlsx` NO debe subirse a GitHub (ignorado en .gitignore)
   - Mantenlo localmente como backup

2. **Base de Datos:**
   - `sitis_consolidado.db` NO debe subirse a GitHub (ignorado en .gitignore)
   - Solo debe estar en SharePoint

3. **Actualizaciones Futuras:**
   - Si necesitas actualizar datos (improbable, sistema deprecated)
   - Solo ejecuta `python convertir_excel_a_sqlite.py` con nuevo Excel
   - Y vuelve a subir el `sitis_consolidado.db` a SharePoint

4. **Cache:**
   - La app cachea el archivo SQLite localmente
   - Se actualiza automáticamente cada 24 horas
   - Puedes forzar actualización con el botón en la UI

---

## 🆘 Soporte

Si tienes problemas durante el deployment, verifica:

1. **Logs de Easypanel**: Revisar si hay errores durante el build/startup
2. **SharePoint**: Verificar que el archivo esté subido correctamente
3. **GitHub**: Verificar que el último commit (15a0560) esté en main
4. **Credenciales**: Verificar que las variables de entorno estén configuradas en Easypanel

---

**¡Todo listo para el deployment! 🚀**

