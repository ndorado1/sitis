# ⚠️ Limitaciones de Streamlit Cloud

## 🔴 Problema: Límites de Memoria

Streamlit Cloud (plan gratuito) tiene las siguientes limitaciones:
- **RAM**: ~1 GB
- **CPU**: Compartida
- **Timeout**: 10 minutos de inactividad

### 📊 Tamaño de Nuestros Datos

| Sede | Pacientes | Datos | Memoria Estimada |
|------|-----------|-------|------------------|
| **Principal** | ~73,000 | DAT_PER + HISTORICO + CAB_FAC | ~500 MB |
| **Piéndamo** | 67,312 | DAT_PER + HISTORICO + CAB_FAC | ~730 MB |
| **Silvia** | 54,709 | DAT_PER + HISTORICO + CAB_FAC | ~706 MB |
| **TOTAL 3 SEDES** | ~195,000 | Consolidado | **~1.4 GB** ❌ |

**Resultado**: Cargar las 3 sedes **excede** la memoria disponible en Streamlit Cloud.

---

## ✅ Solución Implementada

La aplicación **detecta automáticamente** si está ejecutándose en Streamlit Cloud:

### En Streamlit Cloud:
- ✅ Carga **solo Sede Principal**
- ✅ ~73,000 pacientes
- ✅ ~500 MB de datos
- ✅ Funciona sin problemas de memoria

### En Local o Servidor Propio:
- ✅ Carga **TODAS las sedes** configuradas
- ✅ ~195,000 pacientes
- ✅ ~1.4 GB de datos
- ✅ Vista consolidada completa

---

## 🚀 Opciones para Cargar Todas las Sedes

### Opción 1: Servidor Propio (Recomendado)
Desplegar en un servidor con más memoria:

**AWS EC2 / Azure VM / Google Cloud:**
```bash
# Instancia recomendada: t2.medium o superior
# RAM: 4GB+
# Instalar dependencias
conda env create -f environment.yml
conda activate sitis-app

# Configurar credenciales
export SHAREPOINT_CLIENT_ID="..."
export SHAREPOINT_CLIENT_SECRET="..."
export SHAREPOINT_TENANT_ID="..."

# Ejecutar
streamlit run app.py --server.port 8501
```

**Costo estimado**: $10-20/mes

### Opción 2: Streamlit Cloud Teams/Enterprise
Upgrade a plan pagado con más recursos:
- **Teams**: $250/mes - 8 GB RAM
- **Enterprise**: Contactar ventas - Recursos dedicados

### Opción 3: Docker + Hosting Propio
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["streamlit", "run", "app.py"]
```

Desplegar en:
- **Heroku** (Plan Hobby: $7/mes, 512MB) ⚠️ Aún insuficiente
- **Render** (Starter: $7/mes, 512MB) ⚠️ Aún insuficiente
- **DigitalOcean** (Basic Droplet: $6/mes, 1GB) ⚠️ Justo en el límite
- **DigitalOcean** (Droplet 2GB: $12/mes) ✅ Recomendado

### Opción 4: Reducir Datos
Si necesitas mantener Streamlit Cloud gratuito:

1. **Filtrar por fecha**: Cargar solo últimos 12-24 meses
2. **Sampling**: Cargar muestra representativa
3. **Agregación**: Pre-agregar datos por mes/año

---

## 🔍 Cómo Detecta el Modo

La aplicación busca la variable de entorno `STREAMLIT_SHARING_MODE`:

```python
if 'STREAMLIT_SHARING_MODE' in os.environ:
    # Estamos en Streamlit Cloud
    # Cargar solo Sede Principal
else:
    # Local o servidor propio
    # Cargar todas las sedes
```

---

## 📋 Comparación de Opciones

| Opción | Costo | RAM | Todas las Sedes | Complejidad |
|--------|-------|-----|-----------------|-------------|
| **Streamlit Cloud Free** | Gratis | 1 GB | ❌ Solo Principal | ⭐ Muy Fácil |
| **Servidor Propio (AWS)** | $10-20/mes | 4+ GB | ✅ Sí | ⭐⭐ Fácil |
| **Streamlit Teams** | $250/mes | 8 GB | ✅ Sí | ⭐ Muy Fácil |
| **DigitalOcean Droplet** | $12/mes | 2 GB | ✅ Sí | ⭐⭐⭐ Media |

---

## 💡 Recomendación

**Para desarrollo/pruebas**: 
- ✅ Streamlit Cloud gratis (solo Sede Principal)

**Para producción**:
- ✅ AWS EC2 t2.medium ($15/mes) con **todas las sedes**
- ✅ Memoria suficiente para crecimiento futuro
- ✅ Control completo del entorno

---

## 🐛 Troubleshooting

### Error: "EOF" o "Health check failed"
**Causa**: Sin memoria suficiente  
**Solución**: La app ya está optimizada para Streamlit Cloud (solo carga Sede Principal)

### Error: "Application error"
**Causa**: Variables de entorno no configuradas  
**Solución**: Verificar secrets en Streamlit Cloud:
```toml
SHAREPOINT_CLIENT_ID = "..."
SHAREPOINT_CLIENT_SECRET = "..."
SHAREPOINT_TENANT_ID = "..."
```

### Carga muy lenta
**Causa**: Archivos grandes desde SharePoint  
**Solución**: Primera carga es lenta (~2 min), luego usa cache

---

## 📞 Soporte

Para más información sobre deployment:
- **Streamlit Cloud**: https://docs.streamlit.io/streamlit-community-cloud
- **AWS**: https://aws.amazon.com/ec2/
- **DigitalOcean**: https://www.digitalocean.com/products/droplets

---

**Última actualización**: Diciembre 2024

