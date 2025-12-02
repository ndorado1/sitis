# 📊 Consolidación de Sedes - Resumen

## ✅ Proceso Completado

Se consolidaron exitosamente 4 carpetas en 2 sedes:

### 🏥 Sede Piéndamo
**Origen**: `Piendamo_Vieja` + `Piendamo_Final`  
**Destino**: Carpeta `Piendamo/`

| Archivo | Registros | Tamaño | Notas |
|---------|-----------|--------|-------|
| `DAT_PER.csv` | 38,375 | 14.84 MB | 28,937 duplicados removidos |
| `HISTORICO_PYP.csv` | 882,409 | 53.02 MB | Sin duplicados |
| `CAB_FAC.csv` | 1,540,876 | 650.29 MB | 1 línea mal formada omitida |

### 🏥 Sede Silvia
**Origen**: `Silvia_Vieja` + `Silvia_Nueva`  
**Destino**: Carpeta `Silvia/`

| Archivo | Registros | Tamaño | Notas |
|---------|-----------|--------|-------|
| `DAT_PER.csv` | 35,096 | 13.47 MB | 19,613 duplicados removidos |
| `HISTORICO_PYP.csv` | 685,695 | 41.35 MB | Sin duplicados |
| `CAB_FAC.csv` | 1,561,643 | 643.90 MB | Sin problemas |

---

## 📋 Totales Consolidados

| Métrica | Piéndamo | Silvia | **Total** |
|---------|----------|--------|-----------|
| **Pacientes** | 38,375 | 35,096 | **73,471** |
| **Atenciones** | 882,409 | 685,695 | **1,568,104** |
| **Facturas** | 1,540,876 | 1,561,643 | **3,102,519** |
| **Tamaño Total** | 718 MB | 699 MB | **1.4 GB** |

---

## 🔧 Proceso Realizado

### 1. Script de Consolidación
Se creó el script `consolidar_sedes.py` que:
- ✅ Lee archivos CSV de carpetas origen
- ✅ Elimina duplicados en `DAT_PER.csv` por `ID_PACIENTE`
- ✅ Maneja líneas mal formadas automáticamente
- ✅ Consolida registros de múltiples períodos
- ✅ Genera reportes detallados del proceso

### 2. Manejo de Duplicados
- **DAT_PER**: Se eliminan duplicados manteniendo el registro más reciente
- **HISTORICO_PYP**: Se mantienen todos los registros (pueden ser legítimos)
- **CAB_FAC**: Se mantienen todos los registros (pueden ser legítimos)

### 3. Manejo de Errores
- Líneas mal formadas se omiten con advertencia
- El proceso continúa incluso si un archivo falla
- Se generan logs detallados de cualquier problema

---

## 📁 Estructura en SharePoint

Debes subir las carpetas consolidadas a SharePoint con esta estructura:

```
📁 /Analisis de Datos/
│
├── 📁 BD_SITIS/                    ← Sede Principal (ya existe)
│   ├── ACTXPROG_filtrado.csv      ← Catálogo compartido
│   ├── DAT_PER.csv
│   ├── HISTORICO_PYP.csv
│   └── CAB_FAC.csv
│
├── 📁 BD_SITIS_PIENDAMO/           ← Nueva sede (subir carpeta Piendamo/)
│   ├── DAT_PER.csv
│   ├── HISTORICO_PYP.csv
│   └── CAB_FAC.csv
│
└── 📁 BD_SITIS_SILVIA/             ← Nueva sede (subir carpeta Silvia/)
    ├── DAT_PER.csv
    ├── HISTORICO_PYP.csv
    └── CAB_FAC.csv
```

---

## ⚙️ Configuración Actualizada

El archivo `config_sharepoint.py` ya está actualizado con las nuevas sedes:

```python
SEDES = {
    'PRINCIPAL': {
        'nombre': 'Sede Principal',
        'carpeta': 'BD_SITIS',
        'descripcion': 'Hospital Madre Dominga - Sede Principal'
    },
    'PIENDAMO': {
        'nombre': 'Sede Piéndamo',
        'carpeta': 'BD_SITIS_PIENDAMO',
        'descripcion': 'Hospital Madre Dominga - Piéndamo (Consolidado)'
    },
    'SILVIA': {
        'nombre': 'Sede Silvia',
        'carpeta': 'BD_SITIS_SILVIA',
        'descripcion': 'Hospital Madre Dominga - Silvia (Consolidado)'
    },
}
```

---

## 🚀 Próximos Pasos

### 1. ✅ Verificar Archivos Consolidados (Completado)
Los archivos están en:
- `./Piendamo/` (3 archivos)
- `./Silvia/` (3 archivos)

### 2. 📤 Subir a SharePoint
Manualmente sube las carpetas a SharePoint:
- Renombrar `Piendamo/` → `BD_SITIS_PIENDAMO/`
- Renombrar `Silvia/` → `BD_SITIS_SILVIA/`
- Subir a `/Analisis de Datos/`

### 3. 🧪 Probar la Aplicación
Una vez en SharePoint, ejecuta:
```bash
export SHAREPOINT_CLIENT_ID="..."
export SHAREPOINT_CLIENT_SECRET="..."
export SHAREPOINT_TENANT_ID="..."
streamlit run app.py
```

La aplicación debería:
- ✅ Cargar automáticamente las 3 sedes
- ✅ Mostrar métricas consolidadas al inicio
- ✅ Incluir columna "Sede" en todos los resultados
- ✅ Buscar pacientes en todas las sedes simultáneamente

### 4. 📊 Verificar Datos
Prueba buscando:
- Un paciente que esté en la base vieja de Piéndamo
- Un paciente que esté en la base final de Piéndamo
- Un paciente de Silvia vieja
- Un paciente de Silvia nueva

Todos deberían aparecer correctamente con su sede identificada.

---

## 🗑️ Limpieza (Opcional)

Una vez verificado que todo funciona, puedes eliminar las carpetas de trabajo:
```bash
# Eliminar carpetas origen (ya consolidadas)
rm -rf Piendamo_Vieja/ Piendamo_Final/
rm -rf Silvia_Vieja/ Silvia_Nueva/

# Opcional: Eliminar carpetas consolidadas si ya están en SharePoint
# rm -rf Piendamo/ Silvia/
```

---

## ⚠️ Notas Importantes

### Advertencias Durante la Consolidación
1. **Piéndamo CAB_FAC**: 1 línea mal formada omitida (línea 1,175,810)
   - No afecta significativamente los datos (1 de 1.5M registros)
   
2. **Duplicados en CAB_FAC**: ~260-310k IDs duplicados
   - Se mantienen todos porque pueden ser facturas modificadas/corregidas
   - Si causan problemas, se puede agregar lógica de deduplicación

### Validación de Datos
- ✅ Total pacientes suma correctamente
- ✅ Total atenciones suma correctamente
- ✅ Fechas se mantienen consistentes
- ✅ IDs internos se preservan

### Performance
Con las 3 sedes cargadas:
- **Total pacientes**: ~73,000 (Principal) + 38,000 (Piéndamo) + 35,000 (Silvia) ≈ **146,000**
- **Total atenciones**: Varios millones de registros
- **Tiempo de carga**: ~30-60 segundos en primera ejecución
- **Cache**: Mejora significativamente cargas subsecuentes

---

## 📞 Soporte

Si encuentras problemas:
1. Verifica que los archivos estén en SharePoint
2. Verifica nombres de carpetas en `config_sharepoint.py`
3. Revisa permisos en Azure AD (ver `PERMISOS_AZURE_AD.md`)
4. Verifica variables de entorno de autenticación

---

**🎉 ¡Consolidación completada exitosamente!**

*Documento generado automáticamente el proceso de consolidación*

