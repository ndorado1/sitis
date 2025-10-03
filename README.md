# Sistema de Consulta de Atenciones SITIS

Aplicación web desarrollada con Streamlit para consultar el historial de atenciones de pacientes del sistema SITIS.

## 📋 Características

- **Búsqueda por Paciente**: Consulta el historial completo de atenciones de un paciente usando su número de documento
- **Búsqueda por Actividad**: Encuentra todos los pacientes que han recibido una actividad específica
- **Exportación de datos**: Descarga los resultados en formato CSV
- **Interfaz intuitiva**: Diseño moderno y fácil de usar

## 🚀 Instalación

### Opción 1: Usar Conda (Recomendado)

1. Crear el entorno Conda con las dependencias:
```bash
conda env create -f environment.yml
```

2. Activar el entorno:
```bash
conda activate sitis-app
```

### Opción 2: Usar pip

```bash
pip install streamlit pandas numpy
```

## ▶️ Ejecución

1. Asegúrate de estar en el directorio del proyecto donde se encuentran los archivos CSV

2. Activa el entorno Conda (si lo usas):
```bash
conda activate sitis-app
```

3. Ejecuta la aplicación:
```bash
streamlit run app.py
```

4. La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

## 📊 Archivos Requeridos

La aplicación necesita los siguientes archivos CSV en el mismo directorio:

- `ACTXPROG_filtrado.csv` - Catálogo de actividades
- `DAT_PER.csv` - Datos de pacientes
- `HISTORICO_PYP.csv` - Histórico de atenciones
- `CAB_FAC.csv` - Cabecera de facturas

## 🔍 Uso

### Búsqueda por Paciente

1. Ingresa el número de documento del paciente
2. Haz clic en "Buscar"
3. Visualiza la información del paciente y su historial de atenciones
4. Descarga los resultados si lo necesitas

### Búsqueda por Actividad

1. Selecciona una actividad del menú desplegable
2. Haz clic en "Buscar Pacientes"
3. Visualiza todos los pacientes que han recibido esa actividad
4. Descarga los resultados si lo necesitas

## 📈 Información Mostrada

### Para búsqueda por paciente:
- ID Interno del paciente
- Tipo de documento
- Sexo
- Nombre
- Historial completo de atenciones con fechas
- Estadísticas de atenciones

### Para búsqueda por actividad:
- Lista de pacientes
- Documentos y datos personales
- Fechas de atención
- Estadísticas agregadas

## 🛠️ Tecnologías

- Python 3.10
- Streamlit 1.28+
- Pandas 2.0+
- NumPy 1.24+

## 📝 Notas

- La primera carga puede tardar unos segundos debido al tamaño de los archivos CSV
- Los datos se cachean automáticamente para mejorar el rendimiento
- El archivo CAB_FAC.csv solo carga las columnas necesarias para optimizar la memoria

