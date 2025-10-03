# Archivos CSV Requeridos

Este proyecto requiere los siguientes archivos CSV que **NO** están incluidos en el repositorio por su tamaño:

## 📋 Archivos Necesarios

Coloca estos archivos en el directorio raíz del proyecto:

1. **`DAT_PER.csv`** (13 MB)
   - Contiene los datos de pacientes
   - Campos: ID_PACIENTE, IDE_PAC, COD_TID, NM1_PAC, NM2_PAC, AP1_PAC, AP2_PAC, SEX_PAC, etc.

2. **`HISTORICO_PYP.csv`** (40 MB)
   - Contiene el histórico de atenciones PyP
   - Campos: ID_HISTORICOPYP, ID_PACIENTE, ID_ACTPYP, FECHA, IDCAB_FAC, etc.

3. **`CAB_FAC.csv`** (561 MB)
   - Contiene las cabeceras de facturas
   - Campos: IDCAB_FAC, FAC_FEC, etc.

4. **`ACTXPROG.csv`** (203 KB)
   - Catálogo completo de actividades
   - Campos: ID_ACTXPROG, DES_ACTXPROG, etc.
   - **Nota**: El archivo `ACTXPROG_filtrado.csv` (incluido en el repo) contiene solo las 99 actividades mapeadas

## 📁 Estructura Esperada

```
Consolidacion SITIS/
├── app.py
├── environment.yml
├── README.md
├── ACTXPROG_filtrado.csv    ✅ Incluido en el repo
├── DAT_PER.csv               ❌ Agregar manualmente
├── HISTORICO_PYP.csv         ❌ Agregar manualmente
├── CAB_FAC.csv               ❌ Agregar manualmente
└── ACTXPROG.csv              ❌ Agregar manualmente (opcional)
```

## ⚠️ Importante

Sin estos archivos CSV, la aplicación **NO** funcionará. Asegúrate de colocarlos en el directorio del proyecto antes de ejecutar `streamlit run app.py`.

## 🔐 Seguridad

Estos archivos contienen datos sensibles de pacientes. **NUNCA** los subas a repositorios públicos ni los compartas sin autorización.

