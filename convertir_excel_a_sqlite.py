#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de conversión: Excel consolidado → SQLite
Convierte consolidado_sitis.xlsx a sitis_consolidado.db para uso en la aplicación
"""

import pandas as pd
import sqlite3
from datetime import datetime
import os

print("="*70)
print("📊 CONVERSIÓN EXCEL → SQLITE")
print("="*70)

# Configuración
EXCEL_FILE = 'consolidado_sitis.xlsx'
DB_FILE = 'sitis_consolidado.db'

# Verificar que existe el archivo Excel
if not os.path.exists(EXCEL_FILE):
    print(f"❌ Error: No se encuentra el archivo {EXCEL_FILE}")
    exit(1)

print(f"\n📁 Archivo de entrada: {EXCEL_FILE}")
print(f"💾 Archivo de salida: {DB_FILE}")

# Eliminar DB anterior si existe
if os.path.exists(DB_FILE):
    print(f"\n🗑️  Eliminando base de datos anterior...")
    os.remove(DB_FILE)

# Crear conexión a SQLite
print(f"\n🔧 Creando base de datos SQLite...")
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Crear tabla
print(f"📋 Creando estructura de tabla...")
cursor.execute('''
    CREATE TABLE IF NOT EXISTS atenciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        identificacion TEXT NOT NULL,
        tipo_documento TEXT,
        nombre_completo TEXT NOT NULL,
        nombre1 TEXT,
        nombre2 TEXT,
        apellido1 TEXT,
        apellido2 TEXT,
        fecha_nacimiento DATE,
        edad INTEGER,
        sexo TEXT,
        fecha_atencion DATE NOT NULL,
        actividad TEXT NOT NULL,
        nro_factura TEXT,
        descripcion TEXT,
        telefono TEXT,
        direccion TEXT,
        eps TEXT
    )
''')

# Leer hojas del Excel
print(f"\n📖 Leyendo hojas del Excel...")
xl = pd.ExcelFile(EXCEL_FILE)
print(f"   Hojas encontradas: {', '.join(xl.sheet_names)}")

total_registros = 0
total_con_actividad = 0
total_insertados = 0

# Procesar cada hoja (año)
for sheet_name in xl.sheet_names:
    print(f"\n📄 Procesando año: {sheet_name}")
    
    # Leer hoja completa
    df = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name)
    total_registros += len(df)
    
    print(f"   📊 Registros totales en hoja: {len(df):,}")
    
    # Filtrar solo registros con actividad
    df_actividades = df[df['ACTIVIDADXPROGRAMA'].notna()].copy()
    total_con_actividad += len(df_actividades)
    
    print(f"   ✅ Registros con actividad: {len(df_actividades):,}")
    
    if len(df_actividades) == 0:
        print(f"   ⚠️  No hay registros con actividad, saltando...")
        continue
    
    # Construir nombre completo
    df_actividades['nombre_completo'] = (
        df_actividades['NOMBRE1'].fillna('').astype(str).str.strip() + ' ' +
        df_actividades['NOMBRE2'].fillna('').astype(str).str.strip() + ' ' +
        df_actividades['APELLIDO1'].fillna('').astype(str).str.strip() + ' ' +
        df_actividades['APELLIDO2'].fillna('').astype(str).str.strip()
    ).str.strip().str.replace(r'\s+', ' ', regex=True)
    
    # Preparar datos para inserción
    registros = []
    for _, row in df_actividades.iterrows():
        try:
            # Convertir fecha de nacimiento
            fecha_nac = None
            if pd.notna(row['FECHANACIMIENTO']):
                try:
                    fecha_nac = pd.to_datetime(row['FECHANACIMIENTO']).strftime('%Y-%m-%d')
                except:
                    pass
            
            # Convertir fecha de atención
            fecha_atencion = None
            if pd.notna(row['F_ENTRADA']):
                try:
                    fecha_atencion = pd.to_datetime(row['F_ENTRADA']).strftime('%Y-%m-%d')
                except:
                    pass
            
            if not fecha_atencion:
                continue  # Saltar si no hay fecha de atención
            
            registro = (
                str(row['IDENTIFICACION']) if pd.notna(row['IDENTIFICACION']) else '',
                str(row['T_IDE_PAC']) if pd.notna(row['T_IDE_PAC']) else '',
                row['nombre_completo'],
                str(row['NOMBRE1']) if pd.notna(row['NOMBRE1']) else '',
                str(row['NOMBRE2']) if pd.notna(row['NOMBRE2']) else '',
                str(row['APELLIDO1']) if pd.notna(row['APELLIDO1']) else '',
                str(row['APELLIDO2']) if pd.notna(row['APELLIDO2']) else '',
                fecha_nac,
                int(row['EDAD']) if pd.notna(row['EDAD']) else None,
                str(row['SEXO']) if pd.notna(row['SEXO']) else '',
                fecha_atencion,
                str(row['ACTIVIDADXPROGRAMA']),
                str(row['NRO_FAC']) if pd.notna(row['NRO_FAC']) else '',
                str(row['DESCRIPCION']) if pd.notna(row['DESCRIPCION']) else '',
                str(row['TELEFONO']) if pd.notna(row['TELEFONO']) else '',
                str(row['DIRECCION']) if pd.notna(row['DIRECCION']) else '',
                str(row['EPS']) if pd.notna(row['EPS']) else ''
            )
            registros.append(registro)
        except Exception as e:
            print(f"   ⚠️  Error procesando registro: {e}")
            continue
    
    # Insertar en lotes
    if registros:
        print(f"   💾 Insertando {len(registros):,} registros...")
        cursor.executemany('''
            INSERT INTO atenciones (
                identificacion, tipo_documento, nombre_completo,
                nombre1, nombre2, apellido1, apellido2,
                fecha_nacimiento, edad, sexo, fecha_atencion,
                actividad, nro_factura, descripcion, telefono, direccion, eps
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', registros)
        conn.commit()
        total_insertados += len(registros)
        print(f"   ✅ Insertados correctamente")

# Crear índices para búsquedas rápidas
print(f"\n🔍 Creando índices para optimizar búsquedas...")
cursor.execute('CREATE INDEX IF NOT EXISTS idx_identificacion ON atenciones(identificacion)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_actividad ON atenciones(actividad)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_fecha_atencion ON atenciones(fecha_atencion)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_nombre_completo ON atenciones(nombre_completo)')
conn.commit()
print(f"   ✅ Índices creados")

# Estadísticas finales
print(f"\n" + "="*70)
print(f"📊 ESTADÍSTICAS FINALES")
print(f"="*70)
print(f"📁 Registros totales en Excel: {total_registros:,}")
print(f"✅ Registros con actividad: {total_con_actividad:,}")
print(f"💾 Registros insertados en SQLite: {total_insertados:,}")

# Verificar conteo en base de datos
cursor.execute('SELECT COUNT(*) FROM atenciones')
count = cursor.fetchone()[0]
print(f"🔢 Registros en base de datos: {count:,}")

# Verificar rango de fechas
cursor.execute('SELECT MIN(fecha_atencion), MAX(fecha_atencion) FROM atenciones')
min_fecha, max_fecha = cursor.fetchone()
print(f"📅 Rango de fechas: {min_fecha} a {max_fecha}")

# Verificar pacientes únicos
cursor.execute('SELECT COUNT(DISTINCT identificacion) FROM atenciones')
pacientes_unicos = cursor.fetchone()[0]
print(f"👥 Pacientes únicos: {pacientes_unicos:,}")

# Tamaño del archivo
db_size = os.path.getsize(DB_FILE) / (1024 * 1024)
print(f"💾 Tamaño de base de datos: {db_size:.2f} MB")

# Cerrar conexión
conn.close()

print(f"\n✅ ¡Conversión completada exitosamente!")
print(f"📁 Archivo generado: {DB_FILE}")
print(f"\n🚀 Siguiente paso: Subir {DB_FILE} a SharePoint")
print(f"   Ruta: /Analisis de Datos/{DB_FILE}")
print("="*70)

