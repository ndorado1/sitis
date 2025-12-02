# 🏢 Guía de Configuración Multi-Sede

Esta guía explica cómo funciona el sistema multi-sede y cómo configurar nuevas sedes.

## 📋 Índice

1. [Arquitectura](#arquitectura)
2. [Estructura de Archivos](#estructura-de-archivos)
3. [Agregar Nueva Sede](#agregar-nueva-sede)
4. [Sistema de Cache](#sistema-de-cache)
5. [Solución de Problemas](#solución-de-problemas)

---

## 🏗️ Arquitectura

### Concepto Principal

El sistema maneja múltiples sedes con un **catálogo de actividades compartido**:

```
📊 Datos Compartidos (Todas las Sedes)
   └── ACTXPROG_filtrado.csv  ← Catálogo único de 99 actividades

📍 Datos por Sede (Específicos de cada sede)
   ├── DAT_PER.csv            ← Pacientes de la sede
   ├── HISTORICO_PYP.csv      ← Atenciones de la sede  
   └── CAB_FAC.csv            ← Facturas de la sede
```

### Ventajas

✅ **Mantenimiento Simplificado**: Un solo catálogo para todas las sedes
✅ **Escalabilidad**: Agregar/quitar sedes sin cambiar código
✅ **Aislamiento de Datos**: Cada sede tiene sus propios datos de pacientes
✅ **Cache Inteligente**: Datos cacheados por sede para mejor rendimiento
✅ **Búsquedas Independientes**: Las búsquedas son específicas por sede

---

## 📁 Estructura de Archivos en SharePoint

### Organización Recomendada

```
📁 Analisis de Datos/
│
├── 📁 BD_SITIS/                      # Sede Principal
│   ├── 📄 ACTXPROG_filtrado.csv     # ← Catálogo compartido
│   ├── 📄 ACTXPROG.csv              # ← Catálogo completo (opcional)
│   ├── 📄 DAT_PER.csv
│   ├── 📄 HISTORICO_PYP.csv
│   └── 📄 CAB_FAC.csv
│
├── 📁 BD_SITIS_NORTE/                # Sede Norte (ejemplo)
│   ├── 📄 DAT_PER.csv
│   ├── 📄 HISTORICO_PYP.csv
│   └── 📄 CAB_FAC.csv
│
└── 📁 BD_SITIS_SUR/                  # Sede Sur (ejemplo)
    ├── 📄 DAT_PER.csv
    ├── 📄 HISTORICO_PYP.csv
    └── 📄 CAB_FAC.csv
```

### Notas Importantes

1. **Catálogo Único**: `ACTXPROG_filtrado.csv` debe estar solo en `BD_SITIS`
2. **Nombres de Archivos**: Los archivos por sede deben tener los mismos nombres
3. **Estructura Consistente**: Todas las carpetas de sedes deben tener la misma estructura de columnas

---

## ➕ Agregar Nueva Sede

### Paso 1: Preparar Archivos en SharePoint

1. Crea una nueva carpeta en SharePoint:
   ```
   /Analisis de Datos/BD_SITIS_NUEVA_SEDE/
   ```

2. Sube los archivos requeridos:
   - `DAT_PER.csv`
   - `HISTORICO_PYP.csv`
   - `CAB_FAC.csv`

3. **No subas** `ACTXPROG_filtrado.csv` (se usa el compartido)

### Paso 2: Actualizar Configuración

Edita el archivo `config_sharepoint.py`:

```python
SEDES = {
    'PRINCIPAL': {
        'nombre': 'Sede Principal',
        'carpeta': 'BD_SITIS',
        'descripcion': 'Hospital Madre Dominga - Sede Principal'
    },
    'NORTE': {  # ← Agregar nueva sede aquí
        'nombre': 'Sede Norte',
        'carpeta': 'BD_SITIS_NORTE',
        'descripcion': 'Hospital Madre Dominga - Sede Norte'
    },
    # Agregar más sedes según sea necesario...
}
```

### Paso 3: Verificar

1. Ejecuta la aplicación
2. Verifica que la nueva sede aparezca en el selector
3. Selecciona la sede y busca un paciente de prueba
4. Confirma que los datos se cargan correctamente

### Paso 4: Limpiar Cache (si es necesario)

Si hay problemas al cargar datos de la nueva sede:

```bash
rm -rf cache_sharepoint/NOMBRE_SEDE/
```

---

## 💾 Sistema de Cache

### Estructura de Cache

```
cache_sharepoint/
├── ACTXPROG_filtrado.csv      # Compartido
├── PRINCIPAL/                  # Cache de Sede Principal
│   ├── DAT_PER.csv
│   ├── HISTORICO_PYP.csv
│   └── CAB_FAC.csv
├── NORTE/                      # Cache de Sede Norte
│   ├── DAT_PER.csv
│   ├── HISTORICO_PYP.csv
│   └── CAB_FAC.csv
└── SUR/                        # Cache de Sede Sur
    ├── DAT_PER.csv
    ├── HISTORICO_PYP.csv
    └── CAB_FAC.csv
```

### Ventajas del Cache por Sede

- **Rendimiento**: Cada sede tiene su propio cache
- **Actualizaciones Independientes**: Puedes limpiar el cache de una sede sin afectar otras
- **Fallback Inteligente**: Si SharePoint falla, usa el cache local

### Limpiar Cache

```bash
# Limpiar todo el cache
rm -rf cache_sharepoint/

# Limpiar cache de una sede específica
rm -rf cache_sharepoint/PRINCIPAL/

# Limpiar cache del catálogo compartido
rm cache_sharepoint/ACTXPROG_filtrado.csv
```

---

## 🔍 Solución de Problemas

### Error: "Sede no encontrada"

**Causa**: La sede no está configurada en `config_sharepoint.py`

**Solución**: 
1. Verifica que el ID de la sede esté en el diccionario `SEDES`
2. Verifica que la carpeta en SharePoint exista

### Error: "Archivo no encontrado en SharePoint"

**Causa**: La carpeta o archivos no existen en SharePoint

**Solución**:
1. Verifica la estructura de carpetas en SharePoint
2. Verifica que los nombres de archivo coincidan exactamente
3. Verifica los permisos de acceso a SharePoint

### Los datos no se actualizan

**Causa**: Los datos están en cache

**Solución**:
```bash
# Limpiar cache de la sede específica
rm -rf cache_sharepoint/NOMBRE_SEDE/

# O reiniciar Streamlit con Ctrl+C y volver a ejecutar
streamlit run app.py
```

### Error: "401 Unauthorized"

**Causa**: Credenciales de Azure AD incorrectas o permisos insuficientes

**Solución**:
1. Verifica las variables de entorno:
   ```bash
   echo $SHAREPOINT_CLIENT_ID
   echo $SHAREPOINT_TENANT_ID
   # NO mostrar el secret por seguridad
   ```
2. Verifica permisos en Azure AD (ver `PERMISOS_AZURE_AD.md`)
3. Verifica que el usuario tenga acceso a todas las carpetas de sedes

---

## 📊 Ejemplo Completo

### Caso de Uso: Agregar "Sede Centro"

#### 1. SharePoint

```
/Analisis de Datos/BD_SITIS_CENTRO/
  ├── DAT_PER.csv          (200 MB)
  ├── HISTORICO_PYP.csv    (500 MB)
  └── CAB_FAC.csv          (2 GB)
```

#### 2. Configuración

```python
# config_sharepoint.py
SEDES = {
    'PRINCIPAL': {
        'nombre': 'Sede Principal',
        'carpeta': 'BD_SITIS',
        'descripcion': 'Hospital Madre Dominga - Sede Principal'
    },
    'CENTRO': {  # ← Nueva sede
        'nombre': 'Sede Centro',
        'carpeta': 'BD_SITIS_CENTRO',
        'descripcion': 'Hospital Madre Dominga - Sede Centro'
    },
}
```

#### 3. Resultado en la UI

```
┌─────────────────────────────────────┐
│ 📍 Seleccione la Sede               │
│ ┌─────────────────────────────────┐ │
│ │ Sede Centro                   ▼ │ │ ← Aparece automáticamente
│ └─────────────────────────────────┘ │
│ ℹ️ Hospital Madre Dominga - Centro  │
└─────────────────────────────────────┘
```

---

## 🎯 Mejores Prácticas

### ✅ DO (Hacer)

- Mantener la misma estructura de columnas en todas las sedes
- Usar IDs descriptivos en mayúsculas (`PRINCIPAL`, `NORTE`, `SUR`)
- Documentar cada sede con descripción clara
- Probar la configuración antes de desplegar en producción
- Mantener backups de los archivos importantes

### ❌ DON'T (No Hacer)

- No duplicar `ACTXPROG_filtrado.csv` en cada sede
- No usar espacios en los IDs de sede (usar `SEDE_NORTE`, no `Sede Norte`)
- No cambiar la estructura de columnas entre sedes
- No eliminar sedes sin respaldar los datos
- No hardcodear IDs de sede en el código

---

## 📚 Recursos Adicionales

- **Configuración SharePoint**: Ver `config_sharepoint.py`
- **Permisos Azure AD**: Ver `PERMISOS_AZURE_AD.md`
- **Integración SharePoint**: Ver `RESUMEN_SHAREPOINT.md`
- **Código del Loader**: Ver `sharepoint_loader.py`
- **Aplicación Principal**: Ver `app.py`

---

**🏥 Hospital Madre Dominga - Sistema SITIS**

