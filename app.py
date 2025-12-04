#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Consulta de Atenciones SITIS
Aplicación Streamlit para consultar atenciones médicas desde base de datos SQLite consolidada
"""

import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import config_sharepoint as config
import sharepoint_loader
import traceback

print("🚀 Iniciando aplicación SITIS...")

# ============= CONFIGURACIÓN DE STREAMLIT =============
st.set_page_config(
    page_title="Sistema SITIS - Consulta de Atenciones",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inicializar session_state
if 'busqueda_activa' not in st.session_state:
    st.session_state['busqueda_activa'] = False
if 'documento_buscado' not in st.session_state:
    st.session_state['documento_buscado'] = None

# ============= FUNCIONES DE CARGA DE DATOS =============

@st.cache_resource
def get_db_connection():
    """Obtiene conexión a la base de datos SQLite desde SharePoint"""
    try:
        print("\n📊 Obteniendo conexión a base de datos...")
        conn = sharepoint_loader.get_sqlite_connection()
        print("✅ Conexión establecida")
        return conn
    except Exception as e:
        print(f"❌ Error obteniendo conexión: {e}")
        raise

def calcular_edad(fecha_nacimiento):
    """Calcula la edad a partir de la fecha de nacimiento"""
    if not fecha_nacimiento or pd.isna(fecha_nacimiento):
        return None
    try:
        nacimiento = pd.to_datetime(fecha_nacimiento)
        hoy = datetime.now()
        edad = hoy.year - nacimiento.year
        if (hoy.month, hoy.day) < (nacimiento.month, nacimiento.day):
            edad -= 1
        return edad
    except:
        return None

# ============= FUNCIONES DE BÚSQUEDA =============

def buscar_paciente_por_documento(documento):
    """Busca un paciente por su documento de identidad"""
    conn = get_db_connection()
    
    query = """
        SELECT DISTINCT 
            identificacion,
            tipo_documento,
            nombre_completo,
            sexo,
            fecha_nacimiento,
            edad,
            telefono,
            direccion,
            eps
        FROM atenciones 
        WHERE identificacion = ?
        LIMIT 1
    """
    
    df = pd.read_sql(query, conn, params=[str(documento)])
    
    if not df.empty:
        return df.iloc[0]
    return None

def buscar_atenciones_paciente(documento):
    """Busca todas las atenciones de un paciente"""
    conn = get_db_connection()
    
    query = """
        SELECT 
            fecha_atencion,
            actividad,
            descripcion,
            nro_factura
        FROM atenciones
        WHERE identificacion = ?
        ORDER BY fecha_atencion DESC
    """
    
    df = pd.read_sql(query, conn, params=[str(documento)])
    return df

def buscar_actividades_unicas():
    """Obtiene lista de actividades únicas para el selector"""
    conn = get_db_connection()
    
    query = """
        SELECT DISTINCT actividad
        FROM atenciones
        WHERE actividad IS NOT NULL AND actividad != ''
        ORDER BY actividad
    """
    
    df = pd.read_sql(query, conn)
    return df['actividad'].tolist()

def buscar_pacientes_por_actividad(actividad):
    """Busca todos los pacientes que han recibido una actividad específica"""
    conn = get_db_connection()
    
    query = """
        SELECT 
            identificacion,
            tipo_documento,
            nombre_completo,
            sexo,
            fecha_atencion,
            nro_factura
        FROM atenciones
        WHERE actividad = ?
        ORDER BY fecha_atencion DESC
    """
    
    df = pd.read_sql(query, conn, params=[actividad])
    return df

def obtener_estadisticas_generales():
    """Obtiene estadísticas generales de la base de datos"""
    conn = get_db_connection()
    
    # Total de atenciones
    query_total = "SELECT COUNT(*) as total FROM atenciones"
    total = pd.read_sql(query_total, conn).iloc[0]['total']
    
    # Pacientes únicos
    query_pacientes = "SELECT COUNT(DISTINCT identificacion) as pacientes FROM atenciones"
    pacientes = pd.read_sql(query_pacientes, conn).iloc[0]['pacientes']
    
    # Actividades únicas
    query_actividades = "SELECT COUNT(DISTINCT actividad) as actividades FROM atenciones"
    actividades = pd.read_sql(query_actividades, conn).iloc[0]['actividades']
    
    # Rango de fechas
    query_fechas = "SELECT MIN(fecha_atencion) as min_fecha, MAX(fecha_atencion) as max_fecha FROM atenciones"
    fechas = pd.read_sql(query_fechas, conn).iloc[0]
    
    return {
        'total_atenciones': total,
        'pacientes_unicos': pacientes,
        'actividades_unicas': actividades,
        'fecha_inicio': fechas['min_fecha'],
        'fecha_fin': fechas['max_fecha']
    }

# ============= INTERFAZ PRINCIPAL =============

st.title("🏥 Sistema de Consulta de Atenciones SITIS")
st.caption("📊 Base de datos consolidada 2020-2025")
st.markdown("---")

# Información del sistema
with st.expander("ℹ️ Información del sistema", expanded=False):
    try:
        stats = obtener_estadisticas_generales()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de Atenciones", f"{stats['total_atenciones']:,}")
        with col2:
            st.metric("Pacientes Únicos", f"{stats['pacientes_unicos']:,}")
        with col3:
            st.metric("Actividades Diferentes", f"{stats['actividades_unicas']:,}")
        
        st.write(f"**Período de datos**: {stats['fecha_inicio']} a {stats['fecha_fin']}")
        st.write(f"**Fuente**: Base de datos SQLite consolidada")
        st.write(f"**Modo**: {'SharePoint' if config.USE_SHAREPOINT else 'Local'}")
        
        # Botón para limpiar cache
        if st.button("🔄 Actualizar Base de Datos"):
            sharepoint_loader.clear_cache()
            st.cache_resource.clear()
            st.success("✅ Cache limpiado. La app se recargará con datos actualizados.")
            st.rerun()
    except Exception as e:
        st.error(f"❌ Error obteniendo estadísticas: {str(e)}")

# Cargar datos
try:
    with st.spinner('Cargando base de datos...'):
        conn = get_db_connection()
        st.success("✅ Base de datos cargada correctamente")
except Exception as e:
    st.error(f"❌ Error al cargar la base de datos: {str(e)}")
    with st.expander("🐛 Detalles técnicos del error"):
        st.code(traceback.format_exc())
    with st.expander("⚙️ Configuración actual"):
        st.write(f"- USE_SHAREPOINT: {config.USE_SHAREPOINT}")
        st.write(f"- ARCHIVO_SQLITE: {config.ARCHIVO_SQLITE}")
        st.write(f"- SHAREPOINT_DB_PATH: {config.SHAREPOINT_DB_PATH}")
        st.write(f"- Client ID configurado: {'✅ Sí' if config.SHAREPOINT_CLIENT_ID else '❌ No'}")
    st.stop()

st.markdown("---")

# Tabs para diferentes tipos de búsqueda
tab1, tab2 = st.tabs(["🔍 Buscar por Paciente", "📊 Buscar por Actividad"])

# ============= TAB 1: BÚSQUEDA POR PACIENTE =============
with tab1:
    st.header("Búsqueda por Documento de Paciente")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        documento_buscar = st.text_input(
            "Ingrese el número de documento del paciente:",
            placeholder="Ej: 25690751"
        )
    
    with col2:
        st.write("")
        st.write("")
        buscar_btn = st.button("🔍 Buscar", type="primary", use_container_width=True)
    
    # Mantener el estado de la búsqueda en session_state
    if buscar_btn and documento_buscar:
        st.session_state['documento_buscado'] = documento_buscar
        st.session_state['busqueda_activa'] = True
    
    # Realizar la búsqueda si hay una búsqueda activa
    if st.session_state.get('busqueda_activa', False) and st.session_state.get('documento_buscado'):
        documento_buscar = st.session_state['documento_buscado']
        
        # Botón para nueva búsqueda
        if st.button("🔄 Nueva Búsqueda", key="nueva_busqueda"):
            st.session_state['busqueda_activa'] = False
            st.session_state['documento_buscado'] = None
            st.rerun()
        
        st.markdown("---")
        
        with st.spinner('Buscando paciente...'):
            paciente = buscar_paciente_por_documento(documento_buscar)
            
            if paciente is not None:
                # Mostrar información del paciente
                st.success("✅ Paciente encontrado")
                
                # Calcular edad si no está disponible
                edad_mostrar = paciente['edad']
                if pd.isna(edad_mostrar) and not pd.isna(paciente['fecha_nacimiento']):
                    edad_mostrar = calcular_edad(paciente['fecha_nacimiento'])
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Tipo Documento", paciente['tipo_documento'] if not pd.isna(paciente['tipo_documento']) else 'N/A')
                with col2:
                    st.metric("Documento", paciente['identificacion'])
                with col3:
                    st.metric("Edad", f"{int(edad_mostrar)} años" if not pd.isna(edad_mostrar) else 'N/A')
                with col4:
                    st.metric("Sexo", paciente['sexo'] if not pd.isna(paciente['sexo']) else 'N/A')
                
                st.subheader(f"📋 Paciente: {paciente['nombre_completo']}")
                
                # Información adicional
                if not pd.isna(paciente['eps']):
                    st.write(f"**EPS**: {paciente['eps']}")
                if not pd.isna(paciente['telefono']):
                    st.write(f"**Teléfono**: {paciente['telefono']}")
                if not pd.isna(paciente['direccion']):
                    st.write(f"**Dirección**: {paciente['direccion']}")
                
                # Buscar atenciones
                with st.spinner('Buscando atenciones...'):
                    atenciones = buscar_atenciones_paciente(documento_buscar)
                    
                    if not atenciones.empty:
                        st.subheader(f"🩺 Historial de Atenciones ({len(atenciones)} registros)")
                        
                        # Filtro de actividades
                        st.markdown("### 🔍 Filtrar Actividades")
                        
                        # Crear lista de actividades únicas
                        actividades_paciente = atenciones['actividad'].unique()
                        actividades_opciones = ['Todas las actividades'] + sorted(actividades_paciente.tolist())
                        
                        filtro_actividad = st.selectbox(
                            "Filtrar por actividad específica:",
                            options=actividades_opciones,
                            key="filtro_actividad_paciente"
                        )
                        
                        # Aplicar filtro si se selecciona una actividad específica
                        atenciones_filtradas = atenciones.copy()
                        if filtro_actividad != 'Todas las actividades':
                            atenciones_filtradas = atenciones[atenciones['actividad'] == filtro_actividad].copy()
                            
                            if len(atenciones_filtradas) > 0:
                                st.info(f"📊 Mostrando {len(atenciones_filtradas)} registro(s) de la actividad seleccionada")
                            else:
                                st.warning("⚠️ No se encontraron registros para esta actividad")
                        
                        # Renombrar columnas para mejor presentación
                        if not atenciones_filtradas.empty:
                            atenciones_display = atenciones_filtradas.rename(columns={
                                'fecha_atencion': 'Fecha Atención',
                                'actividad': 'Actividad',
                                'descripcion': 'Descripción',
                                'nro_factura': 'No. Factura'
                            })
                            
                            # Mostrar tabla
                            st.dataframe(
                                atenciones_display,
                                use_container_width=True,
                                hide_index=True
                            )
                        else:
                            st.warning("⚠️ No se encontraron registros para esta actividad")
                        
                        # Estadísticas
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total de Atenciones", len(atenciones_filtradas))
                        with col2:
                            actividades_unicas = atenciones_filtradas['actividad'].nunique()
                            st.metric("Actividades Diferentes", actividades_unicas)
                        with col3:
                            # Rango de fechas
                            if len(atenciones_filtradas) > 0:
                                fecha_min = atenciones_filtradas['fecha_atencion'].min()
                                fecha_max = atenciones_filtradas['fecha_atencion'].max()
                                st.metric("Período", f"{fecha_min} a {fecha_max}")
                        
                        # Botón de descarga
                        csv = atenciones_display.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📥 Descargar CSV",
                            data=csv,
                            file_name=f"atenciones_paciente_{documento_buscar}.csv",
                            mime="text/csv",
                        )
                    else:
                        st.warning("⚠️ No se encontraron atenciones para este paciente")
            else:
                st.error("❌ No se encontró ningún paciente con ese documento")
                st.session_state['busqueda_activa'] = False

# ============= TAB 2: BÚSQUEDA POR ACTIVIDAD =============
with tab2:
    st.header("Búsqueda por Actividad")
    
    # Cargar lista de actividades
    with st.spinner('Cargando lista de actividades...'):
        try:
            actividades_lista = buscar_actividades_unicas()
            
            actividad_seleccionada = st.selectbox(
                "Seleccione una actividad:",
                options=actividades_lista,
                index=0
            )
            
            if st.button("🔍 Buscar Pacientes", type="primary"):
                with st.spinner('Buscando pacientes con esta actividad...'):
                    pacientes_actividad = buscar_pacientes_por_actividad(actividad_seleccionada)
                    
                    if not pacientes_actividad.empty:
                        st.success(f"✅ Se encontraron {len(pacientes_actividad)} atenciones")
                        
                        st.subheader(f"📊 Actividad: {actividad_seleccionada}")
                        
                        # Renombrar columnas
                        pacientes_display = pacientes_actividad.rename(columns={
                            'identificacion': 'Documento',
                            'tipo_documento': 'Tipo Doc',
                            'nombre_completo': 'Nombre Paciente',
                            'sexo': 'Sexo',
                            'fecha_atencion': 'Fecha Atención',
                            'nro_factura': 'No. Factura'
                        })
                        
                        # Mostrar tabla
                        st.dataframe(
                            pacientes_display,
                            use_container_width=True,
                            hide_index=True
                        )
                        
                        # Estadísticas
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total de Registros", len(pacientes_actividad))
                        with col2:
                            pacientes_unicos = pacientes_actividad['identificacion'].nunique()
                            st.metric("Pacientes Únicos", pacientes_unicos)
                        with col3:
                            # Rango de fechas
                            fecha_min = pacientes_actividad['fecha_atencion'].min()
                            fecha_max = pacientes_actividad['fecha_atencion'].max()
                            st.metric("Período", f"{fecha_min} a {fecha_max}")
                        
                        # Botón de descarga
                        csv = pacientes_display.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📥 Descargar CSV",
                            data=csv,
                            file_name=f"pacientes_actividad_{actividad_seleccionada[:30]}.csv",
                            mime="text/csv",
                        )
                    else:
                        st.warning("⚠️ No se encontraron pacientes con esta actividad")
        except Exception as e:
            st.error(f"❌ Error cargando actividades: {str(e)}")
            with st.expander("🐛 Detalles del error"):
                st.code(traceback.format_exc())

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        Sistema de Consolidación SITIS | Datos 2020-2025 | Desarrollado con Streamlit
    </div>
    """,
    unsafe_allow_html=True
)
