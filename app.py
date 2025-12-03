#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Consulta de Atenciones de Pacientes - SITIS
Aplicación Streamlit para consultar historico de atenciones
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Logging de inicio para debugging
print("="*70)
print("🚀 Iniciando aplicación SITIS...")
print("="*70)

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import re
import os

print("✅ Módulos básicos importados")

from sharepoint_loader import sharepoint_loader
print("✅ SharePoint loader importado")

import config_sharepoint as config
print(f"✅ Config importado - Modo: {config.MODO_CARGA_SEDES}")
print(f"   Sedes configuradas: {list(config.SEDES.keys())}")
print("="*70)

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

# Función para cargar datos con caché (compartidos - catálogo único)
@st.cache_data
def cargar_actividades():
    """Carga el catálogo de actividades filtradas (compartido entre todas las sedes)"""
    df = sharepoint_loader.load_csv('ACTXPROG_FILTRADO', sede_id=None, encoding='utf-8')
    # Normalizar descripciones
    df['DES_ACTXPROG'] = df['DES_ACTXPROG'].apply(normalizar_texto)
    return df

# Funciones para cargar datos consolidados de todas las sedes
@st.cache_data
def cargar_datos_pacientes_consolidado():
    """Carga y consolida datos de pacientes de TODAS las sedes"""
    dfs = []
    
    # Determinar sedes a cargar según configuración
    sedes_a_cargar = config.SEDES
    if config.MODO_CARGA_SEDES == 'PRINCIPAL':
        st.info("ℹ️ Cargando solo Sede Principal (configurable con MODO_CARGA_SEDES=ALL)")
        sedes_a_cargar = {k: v for k, v in config.SEDES.items() if k == 'PRINCIPAL'}
    
    for sede_id, sede_info in sedes_a_cargar.items():
        try:
            print(f"\n📥 Cargando pacientes de {sede_info['nombre']}...")
            df = sharepoint_loader.load_csv('DAT_PER', encoding='utf-8', sede_id=sede_id)
            
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
            
            # Agregar columna identificadora de sede
            df['SEDE'] = sede_info['nombre']
            df['SEDE_ID'] = sede_id
            
            dfs.append(df)
            print(f"   ✅ {len(df):,} pacientes cargados")
            
        except Exception as e:
            print(f"   ⚠️ Error cargando {sede_info['nombre']}: {e}")
            continue
    
    if not dfs:
        raise Exception("No se pudo cargar datos de ninguna sede")
    
    # Consolidar todos los DataFrames
    df_consolidado = pd.concat(dfs, ignore_index=True)
    print(f"\n✅ Total consolidado: {len(df_consolidado):,} pacientes de {len(dfs)} sede(s)")
    
    return df_consolidado

@st.cache_data
def cargar_historico_pyp_consolidado():
    """Carga y consolida histórico de PyP de TODAS las sedes"""
    dfs = []
    
    # Determinar sedes a cargar según configuración
    sedes_a_cargar = config.SEDES
    if config.MODO_CARGA_SEDES == 'PRINCIPAL':
        sedes_a_cargar = {k: v for k, v in config.SEDES.items() if k == 'PRINCIPAL'}
    
    for sede_id, sede_info in sedes_a_cargar.items():
        try:
            print(f"\n📥 Cargando histórico de {sede_info['nombre']}...")
            df = sharepoint_loader.load_csv('HISTORICO_PYP', encoding='utf-8', sede_id=sede_id)
            
            # Agregar columna identificadora de sede
            df['SEDE'] = sede_info['nombre']
            df['SEDE_ID'] = sede_id
            
            dfs.append(df)
            print(f"   ✅ {len(df):,} registros cargados")
            
        except Exception as e:
            print(f"   ⚠️ Error cargando {sede_info['nombre']}: {e}")
            continue
    
    if not dfs:
        raise Exception("No se pudo cargar datos de ninguna sede")
    
    # Consolidar todos los DataFrames
    df_consolidado = pd.concat(dfs, ignore_index=True)
    print(f"\n✅ Total consolidado: {len(df_consolidado):,} registros de {len(dfs)} sede(s)")
    
    return df_consolidado

@st.cache_data
def cargar_cab_fac_consolidado():
    """Carga y consolida facturas (cabecera) de TODAS las sedes"""
    dfs = []
    
    # Determinar sedes a cargar según configuración
    sedes_a_cargar = config.SEDES
    if config.MODO_CARGA_SEDES == 'PRINCIPAL':
        sedes_a_cargar = {k: v for k, v in config.SEDES.items() if k == 'PRINCIPAL'}
    
    for sede_id, sede_info in sedes_a_cargar.items():
        try:
            print(f"\n📥 Cargando facturas de {sede_info['nombre']}...")
            df = sharepoint_loader.load_csv('CAB_FAC', encoding='utf-8', sede_id=sede_id, usecols=['IDCAB_FAC', 'FAC_FEC'])
            
            # Agregar columna identificadora de sede
            df['SEDE'] = sede_info['nombre']
            df['SEDE_ID'] = sede_id
            
            dfs.append(df)
            print(f"   ✅ {len(df):,} facturas cargadas")
            
        except Exception as e:
            print(f"   ⚠️ Error cargando {sede_info['nombre']}: {e}")
            continue
    
    if not dfs:
        raise Exception("No se pudo cargar datos de ninguna sede")
    
    # Consolidar todos los DataFrames
    df_consolidado = pd.concat(dfs, ignore_index=True)
    print(f"\n✅ Total consolidado: {len(df_consolidado):,} facturas de {len(dfs)} sede(s)")
    
    return df_consolidado

def buscar_paciente_por_documento(documento, df_pacientes):
    """Busca un paciente por su documento de identidad"""
    resultado = df_pacientes[df_pacientes['IDE_PAC'] == str(documento)]
    if not resultado.empty:
        return resultado.iloc[0]
    return None

def buscar_atenciones_paciente(id_paciente, df_historico, df_cab_fac, df_actividades):
    """Busca todas las atenciones de un paciente en TODAS las sedes"""
    # Obtener lista de códigos de actividades válidas
    codigos_validos = df_actividades['ID_ACTXPROG'].tolist()
    
    # Filtrar atenciones del paciente SOLO con actividades mapeadas
    atenciones = df_historico[
        (df_historico['ID_PACIENTE'] == id_paciente) & 
        (df_historico['ID_ACTPYP'].isin(codigos_validos))
    ].copy()
    
    if atenciones.empty:
        return pd.DataFrame()
    
    # Obtener fechas de las facturas (matcheando también por SEDE_ID para evitar cruces)
    atenciones = atenciones.merge(
        df_cab_fac[['IDCAB_FAC', 'FAC_FEC', 'SEDE', 'SEDE_ID']], 
        on=['IDCAB_FAC', 'SEDE_ID'], 
        how='left',
        suffixes=('', '_FAC')
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
    
    # Seleccionar y ordenar columnas (incluyendo SEDE)
    columnas_mostrar = [
        'SEDE',
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
    """Busca todos los pacientes que han recibido una actividad específica en TODAS las sedes"""
    # Verificar que la actividad esté en el catálogo válido
    if id_actividad not in df_actividades['ID_ACTXPROG'].values:
        return pd.DataFrame()
    
    # Filtrar por actividad
    atenciones = df_historico[df_historico['ID_ACTPYP'] == id_actividad].copy()
    
    if atenciones.empty:
        return pd.DataFrame()
    
    # Obtener fechas de las facturas (matcheando también por SEDE_ID)
    atenciones = atenciones.merge(
        df_cab_fac[['IDCAB_FAC', 'FAC_FEC', 'SEDE', 'SEDE_ID']], 
        on=['IDCAB_FAC', 'SEDE_ID'], 
        how='left',
        suffixes=('', '_FAC')
    )
    
    # Agregar datos del paciente (matcheando por ID_PACIENTE y SEDE_ID)
    atenciones = atenciones.merge(
        df_pacientes[['ID_PACIENTE', 'IDE_PAC', 'COD_TID', 'NOMBRE_COMPLETO', 'SEX_PAC', 'SEDE_ID']], 
        on=['ID_PACIENTE', 'SEDE_ID'], 
        how='left'
    )
    
    # Usar FAC_FEC como fecha principal
    atenciones['FECHA_ATENCION'] = atenciones['FAC_FEC'].fillna(atenciones['FECHA'])
    
    # Seleccionar columnas (incluyendo SEDE)
    columnas_mostrar = [
        'SEDE',
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
st.caption("📊 Vista consolidada de todas las sedes")
st.markdown("---")

# Debug info (solo si hay problemas)
with st.expander("ℹ️ Información del sistema", expanded=False):
    st.write(f"**Modo de carga**: {config.MODO_CARGA_SEDES}")
    st.write(f"**SharePoint**: {'✅ Habilitado' if config.USE_SHAREPOINT else '❌ Deshabilitado'}")
    st.write(f"**Sedes configuradas**: {len(config.SEDES)}")
    for sede_id, info in config.SEDES.items():
        st.write(f"  - {sede_id}: {info['nombre']}")

# Cargar datos consolidados de TODAS las sedes (o solo Principal según configuración)
with st.spinner('Cargando datos de todas las sedes...'):
    try:
        # Catálogo compartido
        df_actividades = cargar_actividades()
        
        # Datos consolidados de todas las sedes
        df_pacientes = cargar_datos_pacientes_consolidado()
        df_historico = cargar_historico_pyp_consolidado()
        df_cab_fac = cargar_cab_fac_consolidado()
        
        # Mostrar información de sedes cargadas
        sedes_cargadas = df_pacientes['SEDE'].unique()
        st.success(f"✅ Datos consolidados de {len(sedes_cargadas)} sede(s): {', '.join(sedes_cargadas)}")
        
        # Mostrar estadísticas rápidas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Pacientes", f"{len(df_pacientes):,}")
        with col2:
            st.metric("Total Atenciones", f"{len(df_historico):,}")
        with col3:
            st.metric("Total Facturas", f"{len(df_cab_fac):,}")
        
    except Exception as e:
        st.error(f"❌ Error al cargar datos: {str(e)}")
        st.info("💡 Tip: Verifica que las sedes estén configuradas correctamente en config_sharepoint.py")
        
        # Mostrar más detalles del error para debugging
        import traceback
        with st.expander("🐛 Detalles técnicos del error"):
            st.code(traceback.format_exc())
        
        # Mostrar configuración actual
        with st.expander("⚙️ Configuración actual"):
            st.write(f"- USE_SHAREPOINT: {config.USE_SHAREPOINT}")
            st.write(f"- MODO_CARGA_SEDES: {config.MODO_CARGA_SEDES}")
            st.write(f"- Sedes configuradas: {list(config.SEDES.keys())}")
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
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Sede", paciente['SEDE'])
                with col2:
                    st.metric("Tipo Documento", paciente['COD_TID'])
                with col3:
                    st.metric("Documento", paciente['IDE_PAC'])
                with col4:
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
                                'SEDE': 'Sede',
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
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total de Atenciones", len(atenciones_filtradas))
                        with col2:
                            actividades_unicas = atenciones_filtradas['ID_ACTPYP'].nunique()
                            st.metric("Actividades Diferentes", actividades_unicas)
                        with col3:
                            sedes_atendido = atenciones_filtradas['SEDE'].nunique()
                            st.metric("Sedes de Atención", sedes_atendido)
                        
                        # Desglose por sede si hay atenciones en múltiples sedes
                        if sedes_atendido > 1:
                            st.markdown("#### 📊 Atenciones por Sede")
                            sede_stats = atenciones_filtradas.groupby('SEDE').agg({
                                'ID_ACTPYP': 'count'
                            }).rename(columns={'ID_ACTPYP': 'Total Atenciones'}).reset_index()
                            st.dataframe(sede_stats, use_container_width=True, hide_index=True)
                        
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
                    'SEDE': 'Sede',
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
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total de Registros", len(pacientes_actividad))
                with col2:
                    pacientes_unicos = pacientes_actividad['IDE_PAC'].nunique()
                    st.metric("Pacientes Únicos", pacientes_unicos)
                with col3:
                    sedes_con_actividad = pacientes_actividad['SEDE'].nunique()
                    st.metric("Sedes", sedes_con_actividad)
                
                # Desglose por sede
                if sedes_con_actividad > 1:
                    st.markdown("#### 📊 Desglose por Sede")
                    sede_stats = pacientes_actividad.groupby('SEDE').agg({
                        'IDE_PAC': 'count'
                    }).rename(columns={'IDE_PAC': 'Total Registros'}).reset_index()
                    st.dataframe(sede_stats, use_container_width=True, hide_index=True)
                
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

