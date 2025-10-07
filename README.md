# 🏥 Sistema de Consulta de Atenciones SITIS

Aplicación web desarrollada con Streamlit para consultar el historial de atenciones de pacientes del sistema SITIS de Hospital Mama Dominga.

## ✨ Características Principales

- **🔍 Búsqueda por Paciente**: Consulta el historial completo de atenciones usando el número de documento
- **📋 Búsqueda por Actividad**: Encuentra todos los pacientes que han recibido una actividad específica
- **🔄 Filtros Dinámicos**: Filtra las actividades encontradas para un paciente específico
- **📊 Exportación de Datos**: Descarga los resultados en formato CSV
- **☁️ Integración con SharePoint**: Lee archivos directamente desde SharePoint Online
- **💾 Cache Inteligente**: Sistema de caché local para mejor rendimiento
- **🎨 Interfaz Moderna**: Diseño intuitivo y fácil de usar

## 🚀 Instalación

### Opción 1: Usar Conda (Recomendado)

```bash
# 1. Crear el entorno
conda env create -f environment.yml

# 2. Activar el entorno
conda activate sitis-app
```

### Opción 2: Usar pip

```bash
pip install streamlit pandas numpy msal requests
```

## 📦 Dependencias

- **Python** 3.10+
- **Streamlit** 1.28+ - Framework web
- **Pandas** 2.0+ - Procesamiento de datos
- **NumPy** 1.24+ - Operaciones numéricas
- **MSAL** 1.24+ - Autenticación con Microsoft
- **Requests** 2.31+ - Peticiones HTTP

## ⚙️ Configuración

### Variables de Entorno

La aplicación necesita las siguientes variables de entorno para conectarse a SharePoint:

```bash
export SHAREPOINT_CLIENT_ID="[tu-client-id]"
export SHAREPOINT_CLIENT_SECRET="[tu-client-secret]"
export SHAREPOINT_TENANT_ID="[tu-tenant-id]"
```

### Archivos de Configuración

- `config_sharepoint.py` - Configuración de conexión a SharePoint
- `sharepoint_loader.py` - Módulo de carga de archivos desde SharePoint

## ▶️ Ejecución

### Ejecución Local

```bash
# Configurar variables de entorno
export SHAREPOINT_CLIENT_ID="..."
export SHAREPOINT_CLIENT_SECRET="..."
export SHAREPOINT_TENANT_ID="..."

# Ejecutar la aplicación
streamlit run app.py
```

La aplicación se abrirá en `http://localhost:8501`

### Despliegue en Streamlit Cloud

1. Conecta tu repositorio de GitHub
2. Configura los secrets en Settings → Secrets:
   ```toml
   [sharepoint]
   SHAREPOINT_CLIENT_ID = "..."
   SHAREPOINT_CLIENT_SECRET = "..."
   SHAREPOINT_TENANT_ID = "..."
   ```
3. Deploy!

## 📊 Fuentes de Datos

La aplicación lee los siguientes archivos desde SharePoint o localmente:

| Archivo | Descripción | Tamaño |
|---------|-------------|--------|
| `ACTXPROG_filtrado.csv` | Catálogo de actividades filtradas | ~40 KB |
| `DAT_PER.csv` | Datos demográficos de pacientes | ~13 MB |
| `HISTORICO_PYP.csv` | Histórico de atenciones | ~40 MB |
| `CAB_FAC.csv` | Cabecera de facturas con fechas | ~560 MB |

### 🔄 Sistema de Fallback

La aplicación funciona en modo cascada:
1. **SharePoint** - Intenta leer desde SharePoint (si está configurado)
2. **Cache Local** - Si falla, usa archivos del cache (`cache_sharepoint/`)
3. **Archivos Locales** - Si no hay cache, lee archivos del directorio local

## 🔍 Uso de la Aplicación

### Búsqueda por Paciente

1. Ingresa el número de documento (IDE_PAC)
2. Haz clic en **"Buscar"**
3. Visualiza:
   - Datos personales del paciente
   - Historial completo de atenciones
   - Fechas de cada atención
   - Código y descripción de actividades
4. Usa el filtro de actividades para buscar una atención específica
5. Descarga los resultados en CSV si es necesario

### Búsqueda por Actividad

1. Selecciona una actividad del menú desplegable
2. Haz clic en **"Buscar Pacientes"**
3. Visualiza:
   - Lista de todos los pacientes
   - Datos demográficos
   - Fechas de atención
   - Estadísticas agregadas
4. Descarga los resultados en CSV si es necesario

## 📈 Información Mostrada

### Vista de Paciente
- **Datos Personales**: Nombre completo, tipo de documento, sexo
- **ID Interno**: ID_PACIENTE para referencias
- **Historial**: Lista de todas las atenciones recibidas
- **Fechas**: Fecha exacta de cada atención (FAC_FEC)
- **Actividades**: Código y descripción de cada actividad
- **Estadísticas**: Total de atenciones, rango de fechas

### Vista de Actividad
- **Pacientes**: Lista de todos los beneficiarios
- **Documentos**: Tipo y número de identificación
- **Datos Demográficos**: Nombre, sexo
- **Fechas de Atención**: Cuándo recibieron la actividad
- **Estadísticas**: Total de pacientes, distribución por sexo

## 🔐 Seguridad

- ✅ Credenciales almacenadas como variables de entorno
- ✅ No se incluyen secretos en el código fuente
- ✅ Archivos grandes ignorados en `.gitignore`
- ✅ Cache local no se sube al repositorio
- ✅ Autenticación segura con Azure AD

## 🛠️ Tecnologías

- **Backend**: Python 3.10
- **Framework Web**: Streamlit
- **Procesamiento de Datos**: Pandas, NumPy
- **Autenticación**: MSAL (Microsoft Authentication Library)
- **API**: Microsoft Graph API
- **Storage**: SharePoint Online
- **Version Control**: Git / GitHub

## 📝 Notas Técnicas

- La primera carga puede tardar unos segundos debido al tamaño de los archivos
- Los datos se cachean automáticamente usando `@st.cache_data`
- Streaming de archivos grandes para optimizar memoria
- Solo se cargan las columnas necesarias de `CAB_FAC.csv`
- Normalización de texto para caracteres especiales (ñ, acentos)

## 🏗️ Estructura del Proyecto

```
Consolidacion SITIS/
├── app.py                      # Aplicación principal
├── config_sharepoint.py        # Configuración de SharePoint
├── sharepoint_loader.py        # Módulo de carga desde SharePoint
├── environment.yml             # Dependencias Conda
├── .gitignore                 # Archivos ignorados
├── README.md                  # Este archivo
├── ACTXPROG_filtrado.csv      # Catálogo de actividades
└── cache_sharepoint/          # Cache local (auto-generado)
```

## 🤝 Contribuir

Este proyecto es de uso interno para Hospital Mama Dominga. Para modificaciones o mejoras, contacta al equipo de Análisis de Datos.

## 📄 Licencia

Uso interno - Hospital Mama Dominga

---

**Desarrollado con ❤️ para Hospital Mama Dominga**
