# Dockerfile para aplicación SITIS con Streamlit
# Optimizado para producción

FROM python:3.10-slim

# Metadata
LABEL maintainer="Hospital Madre Dominga"
LABEL description="Sistema de Consulta de Atenciones SITIS"

# Configurar variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY environment.yml requirements.txt* ./

# Crear requirements.txt desde environment.yml si no existe
RUN if [ ! -f requirements.txt ]; then \
    echo "streamlit>=1.28.0" > requirements.txt && \
    echo "pandas>=2.0.0" >> requirements.txt && \
    echo "numpy>=1.24.0" >> requirements.txt && \
    echo "msal>=1.24.0" >> requirements.txt && \
    echo "requests>=2.31.0" >> requirements.txt; \
    fi

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY app.py .
COPY sharepoint_loader.py .
COPY config_sharepoint.py .
COPY ACTXPROG_filtrado.csv .
COPY entrypoint.sh .

# Crear directorios necesarios
RUN mkdir -p cache_sharepoint .streamlit

# Configurar Streamlit
RUN echo '\
[server]\n\
headless = true\n\
enableCORS = false\n\
enableXsrfProtection = false\n\
port = 8501\n\
\n\
[browser]\n\
gatherUsageStats = false\n\
\n\
[theme]\n\
primaryColor = "#1f77b4"\n\
backgroundColor = "#ffffff"\n\
secondaryBackgroundColor = "#f0f2f6"\n\
textColor = "#262730"\n\
' > .streamlit/config.toml

# Exponer puerto
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Dar permisos al entrypoint
RUN chmod +x entrypoint.sh

# Usuario no-root para seguridad
RUN useradd -m -u 1000 streamlit && \
    chown -R streamlit:streamlit /app
USER streamlit

# Usar entrypoint para validaciones y debugging
ENTRYPOINT ["/app/entrypoint.sh"]

