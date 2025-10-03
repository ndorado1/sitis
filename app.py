#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Consulta de Atenciones de Pacientes - SITIS
Aplicación Streamlit para consultar historico de atenciones
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import re

# Función para normalizar textos con caracteres especiales
def normalizar_texto(texto):
    """Corrige caracteres mal codificados en español"""
    if pd.isna(texto) or texto == '':
        return texto
    
    texto = str(texto)
    
    # Reemplazos literales de patrones específicos más comunes
    # El patrón más común es "ï¿½" que representa caracteres con tilde
    reemplazos_literales = [
        ('ATENCIï¿½N', 'ATENCION'),
        ('APLICACIï¿½N', 'APLICACION'),
        ('FLï¿½OR', 'FLUOR'),
        ('Aï¿½OS', 'AÑOS'),
        ('Aï¿½O', 'AÑO'),
        ('NIï¿½OS', 'NIÑOS'),
        ('NIï¿½O', 'NIÑO'),
        ('ODONTOLOGï¿½A', 'ODONTOLOGIA'),
        ('Mï¿½DICO', 'MEDICO'),
        ('ENFERMERï¿½A', 'ENFERMERIA'),
        ('BIOLï¿½GICO', 'BIOLOGICO'),
        ('QUï¿½MICO', 'QUIMICO'),
        ('Fï¿½SICO', 'FISICO'),
        ('CLï¿½NICO', 'CLINICO'),
        ('Bï¿½SICO', 'BASICO'),
        ('EVALUACIï¿½N', 'EVALUACION'),
        ('VACUNACIï¿½N', 'VACUNACION'),
        ('NUTRICIï¿½N', 'NUTRICION'),
        ('PREVENCIï¿½N', 'PREVENCION'),
        ('PROMOCIï¿½N', 'PROMOCION'),
        ('GESTACIï¿½N', 'GESTACION'),
        ('NUTRICIï¿½N', 'NUTRICION'),
        ('ORIENTACIï¿½N', 'ORIENTACION'),
    ]
    
    for mal, bien in reemplazos_literales:
        texto = texto.replace(mal, bien)
    
    # Reemplazar el caracter problemático individual
    texto = texto.replace('ï¿½', 'O')
    texto = texto.replace('\ufffd', 'n')
    
    return texto

# Configuración de la página
st.set_page_config(
    page_title="Consulta de Atenciones SITIS",
    page_icon="🏥",
    layout="wide"
)

# Función para cargar datos con caché
@st.cache_data
def cargar_actividades():
    """Carga el catálogo de actividades filtradas"""
    df = pd.read_csv('ACTXPROG_filtrado.csv', encoding='utf-8')
    # Normalizar descripciones
    df['DES_ACTXPROG'] = df['DES_ACTXPROG'].apply(normalizar_texto)
    return df

@st.cache_data
def cargar_datos_pacientes():
    """Carga los datos de pacientes"""
    df = pd.read_csv('DAT_PER.csv', encoding='utf-8')
    # Convertir IDE_PAC a string para búsqueda
    df['IDE_PAC'] = df['IDE_PAC'].astype(str)
    
    # Normalizar nombres
    df['NM1_PAC'] = df['NM1_PAC'].apply(normalizar_texto)
    df['NM2_PAC'] = df['NM2_PAC'].apply(normalizar_texto)
    df['AP1_PAC'] = df['AP1_PAC'].apply(normalizar_texto)
    df['AP2_PAC'] = df['AP2_PAC'].apply(normalizar_texto)
    
    # Concatenar nombre completo
    df['NOMBRE_COMPLETO'] = (
        df['NM1_PAC'].fillna('').astype(str) + ' ' +
        df['NM2_PAC'].fillna('').astype(str) + ' ' +
        df['AP1_PAC'].fillna('').astype(str) + ' ' +
        df['AP2_PAC'].fillna('').astype(str)
    ).str.strip().str.replace(r'\s+', ' ', regex=True)
    
    return df

@st.cache_data
def cargar_historico_pyp():
    """Carga el histórico de PyP"""
    df = pd.read_csv('HISTORICO_PYP.csv', encoding='utf-8')
    return df

@st.cache_data
def cargar_cab_fac():
    """Carga las facturas (cabecera)"""
    # Cargar solo las columnas necesarias para optimizar memoria
    df = pd.read_csv('CAB_FAC.csv', usecols=['IDCAB_FAC', 'FAC_FEC'], encoding='utf-8')
    return df

def buscar_paciente_por_documento(documento, df_pacientes):
    """Busca un paciente por su documento de identidad"""
    resultado = df_pacientes[df_pacientes['IDE_PAC'] == str(documento)]
    if not resultado.empty:
        return resultado.iloc[0]
    return None

def buscar_atenciones_paciente(id_paciente, df_historico, df_cab_fac, df_actividades):
    """Busca todas las atenciones de un paciente"""
    # Obtener lista de códigos de actividades válidas
    codigos_validos = df_actividades['ID_ACTXPROG'].tolist()
    
    # Filtrar atenciones del paciente SOLO con actividades mapeadas
    atenciones = df_historico[
        (df_historico['ID_PACIENTE'] == id_paciente) & 
        (df_historico['ID_ACTPYP'].isin(codigos_validos))
    ].copy()
    
    if atenciones.empty:
        return pd.DataFrame()
    
    # Obtener fechas de las facturas
    atenciones = atenciones.merge(
        df_cab_fac[['IDCAB_FAC', 'FAC_FEC']], 
        on='IDCAB_FAC', 
        how='left'
    )
    
    # Agregar descripción de actividades
    atenciones = atenciones.merge(
        df_actividades[['ID_ACTXPROG', 'DES_ACTXPROG']], 
        left_on='ID_ACTPYP', 
        right_on='ID_ACTXPROG', 
        how='inner'
    )
    
    # Usar FAC_FEC como fecha principal, si no existe usar FECHA del histórico
    atenciones['FECHA_ATENCION'] = atenciones['FAC_FEC'].fillna(atenciones['FECHA'])
    
    # Seleccionar y ordenar columnas
    columnas_mostrar = [
        'ID_ACTPYP', 
        'DES_ACTXPROG', 
        'FECHA_ATENCION', 
        'IDCAB_FAC'
    ]
    
    atenciones_final = atenciones[columnas_mostrar].copy()
    
    # Ordenar por fecha descendente
    atenciones_final = atenciones_final.sort_values('FECHA_ATENCION', ascending=False)
    
    return atenciones_final

def buscar_pacientes_por_actividad(id_actividad, df_historico, df_pacientes, df_cab_fac, df_actividades):
    """Busca todos los pacientes que han recibido una actividad específica"""
    # Verificar que la actividad esté en el catálogo válido
    if id_actividad not in df_actividades['ID_ACTXPROG'].values:
        return pd.DataFrame()
    
    # Filtrar por actividad
    atenciones = df_historico[df_historico['ID_ACTPYP'] == id_actividad].copy()
    
    if atenciones.empty:
        return pd.DataFrame()
    
    # Obtener fechas de las facturas
    atenciones = atenciones.merge(
        df_cab_fac[['IDCAB_FAC', 'FAC_FEC']], 
        on='IDCAB_FAC', 
        how='left'
    )
    
    # Agregar datos del paciente
    atenciones = atenciones.merge(
        df_pacientes[['ID_PACIENTE', 'IDE_PAC', 'COD_TID', 'NOMBRE_COMPLETO', 'SEX_PAC']], 
        on='ID_PACIENTE', 
        how='left'
    )
    
    # Usar FAC_FEC como fecha principal
    atenciones['FECHA_ATENCION'] = atenciones['FAC_FEC'].fillna(atenciones['FECHA'])
    
    # Seleccionar columnas
    columnas_mostrar = [
        'IDE_PAC',
        'COD_TID',
        'NOMBRE_COMPLETO',
        'SEX_PAC',
        'FECHA_ATENCION',
        'IDCAB_FAC'
    ]
    
    atenciones_final = atenciones[columnas_mostrar].copy()
    
    # Ordenar por fecha descendente
    atenciones_final = atenciones_final.sort_values('FECHA_ATENCION', ascending=False)
    
    return atenciones_final

# ============= INTERFAZ PRINCIPAL =============

st.title("🏥 Sistema de Consulta de Atenciones SITIS")
st.markdown("---")

# Cargar datos
with st.spinner('Cargando datos...'):
    try:
        df_actividades = cargar_actividades()
        df_pacientes = cargar_datos_pacientes()
        df_historico = cargar_historico_pyp()
        df_cab_fac = cargar_cab_fac()
        st.success(f"✅ Datos cargados correctamente")
    except Exception as e:
        st.error(f"❌ Error al cargar datos: {str(e)}")
        st.stop()

# Tabs para diferentes tipos de búsqueda
tab1, tab2 = st.tabs(["🔍 Buscar por Paciente", "📊 Buscar por Actividad"])

# ============= TAB 1: BÚSQUEDA POR PACIENTE =============
with tab1:
    st.header("Búsqueda por Documento de Paciente")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        documento_buscar = st.text_input(
            "Ingrese el número de documento del paciente:",
            placeholder="Ej: 1105381788"
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
            paciente = buscar_paciente_por_documento(documento_buscar, df_pacientes)
            
            if paciente is not None:
                # Mostrar información del paciente
                st.success("✅ Paciente encontrado")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Tipo Documento", paciente['COD_TID'])
                with col2:
                    st.metric("Documento", paciente['IDE_PAC'])
                with col3:
                    st.metric("Sexo", paciente['SEX_PAC'])
                
                st.subheader(f"📋 Paciente: {paciente['NOMBRE_COMPLETO']}")
                
                # Buscar atenciones
                with st.spinner('Buscando atenciones...'):
                    atenciones = buscar_atenciones_paciente(
                        paciente['ID_PACIENTE'], 
                        df_historico, 
                        df_cab_fac,
                        df_actividades
                    )
                    
                    if not atenciones.empty:
                        st.subheader(f"🩺 Historial de Atenciones ({len(atenciones)} registros)")
                        
                        # Filtro de actividades
                        st.markdown("### 🔍 Filtrar Actividades")
                        
                        # Crear lista de actividades únicas con su descripción
                        actividades_paciente = atenciones[['ID_ACTPYP', 'DES_ACTXPROG']].drop_duplicates()
                        actividades_opciones = ['Todas las actividades'] + [
                            f"{row['ID_ACTPYP']} - {row['DES_ACTXPROG']}" 
                            for _, row in actividades_paciente.iterrows()
                        ]
                        
                        filtro_actividad = st.selectbox(
                            "Filtrar por actividad específica:",
                            options=actividades_opciones,
                            key="filtro_actividad_paciente"
                        )
                        
                        # Aplicar filtro si se selecciona una actividad específica
                        atenciones_filtradas = atenciones.copy()
                        if filtro_actividad != 'Todas las actividades':
                            codigo_actividad = int(filtro_actividad.split(' - ')[0])
                            
                            # Filtrar por la actividad seleccionada
                            atenciones_filtradas = atenciones[atenciones['ID_ACTPYP'] == codigo_actividad].copy()
                            
                            if len(atenciones_filtradas) > 0:
                                st.info(f"📊 Mostrando {len(atenciones_filtradas)} registro(s) de la actividad seleccionada")
                            else:
                                st.warning("⚠️ No se encontraron registros para esta actividad")
                        
                        # Renombrar columnas para mejor presentación
                        if not atenciones_filtradas.empty:
                            atenciones_display = atenciones_filtradas.rename(columns={
                                'ID_ACTPYP': 'Código Actividad',
                                'DES_ACTXPROG': 'Descripción Actividad',
                                'FECHA_ATENCION': 'Fecha Atención',
                                'IDCAB_FAC': 'ID Factura'
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
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Total de Atenciones", len(atenciones_filtradas))
                        with col2:
                            actividades_unicas = atenciones_filtradas['ID_ACTPYP'].nunique()
                            st.metric("Actividades Diferentes", actividades_unicas)
                        
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
    
    # Selector de actividad
    actividades_dict = dict(zip(
        df_actividades['ID_ACTXPROG'].astype(str) + " - " + df_actividades['DES_ACTXPROG'],
        df_actividades['ID_ACTXPROG']
    ))
    
    actividad_seleccionada = st.selectbox(
        "Seleccione una actividad:",
        options=list(actividades_dict.keys()),
        index=0
    )
    
    if st.button("🔍 Buscar Pacientes", type="primary"):
        id_actividad = actividades_dict[actividad_seleccionada]
        
        with st.spinner('Buscando pacientes con esta actividad...'):
            pacientes_actividad = buscar_pacientes_por_actividad(
                id_actividad,
                df_historico,
                df_pacientes,
                df_cab_fac,
                df_actividades
            )
            
            if not pacientes_actividad.empty:
                st.success(f"✅ Se encontraron {len(pacientes_actividad)} atenciones")
                
                st.subheader(f"📊 Actividad: {actividad_seleccionada}")
                
                # Renombrar columnas
                pacientes_display = pacientes_actividad.rename(columns={
                    'IDE_PAC': 'Documento',
                    'COD_TID': 'Tipo Doc',
                    'NOMBRE_COMPLETO': 'Nombre Paciente',
                    'SEX_PAC': 'Sexo',
                    'FECHA_ATENCION': 'Fecha Atención',
                    'IDCAB_FAC': 'ID Factura'
                })
                
                # Mostrar tabla
                st.dataframe(
                    pacientes_display,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Estadísticas
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total de Registros", len(pacientes_actividad))
                with col2:
                    pacientes_unicos = pacientes_actividad['IDE_PAC'].nunique()
                    st.metric("Pacientes Únicos", pacientes_unicos)
                
                # Botón de descarga
                csv = pacientes_display.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Descargar CSV",
                    data=csv,
                    file_name=f"pacientes_actividad_{id_actividad}.csv",
                    mime="text/csv",
                )
            else:
                st.warning("⚠️ No se encontraron pacientes con esta actividad")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        Sistema de Consolidación SITIS | Desarrollado con Streamlit
    </div>
    """,
    unsafe_allow_html=True
)

