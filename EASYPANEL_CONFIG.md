# Configuración de Easypanel para SITIS

## 🚀 Guía Rápida de Deployment

### 1. Variables de Entorno Requeridas

En el panel de Easypanel, configurar estas variables:

```
SHAREPOINT_CLIENT_ID=tu-client-id-aqui
SHAREPOINT_CLIENT_SECRET=tu-client-secret-aqui
SHAREPOINT_TENANT_ID=tu-tenant-id-aqui
MODO_CARGA_SEDES=PRINCIPAL
```

**Nota**: Los valores reales están en el archivo local `CREDENCIALES_STREAMLIT.txt` (no incluido en el repo).

### 2. Configuración de Red

**IMPORTANTE**: Asegúrate de que:

- **Puerto expuesto**: `8501`
- **Protocolo**: HTTP (no HTTPS internamente)
- **Health check path**: `/_stcore/health`
- **Health check timeout**: Al menos 180 segundos para la primera carga

### 3. Configuración del Dominio/Proxy

Si usas un proxy inverso o dominio personalizado:

```nginx
# Configuración de nginx para Streamlit
location / {
    proxy_pass http://localhost:8501;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_read_timeout 86400;
}
```

### 4. Recursos Mínimos Recomendados

Para `MODO_CARGA_SEDES=PRINCIPAL`:
- **RAM**: 2 GB mínimo (recomendado 4 GB)
- **CPU**: 1 core mínimo
- **Disco**: 1 GB para cache

Para `MODO_CARGA_SEDES=ALL`:
- **RAM**: 8 GB mínimo
- **CPU**: 2 cores mínimo
- **Disco**: 2 GB para cache

### 5. Verificación del Deployment

#### Paso 1: Ver logs
```bash
docker logs -f <container_name>
```

Deberías ver:
```
🎉 CARGA COMPLETADA: 1 sede(s)
Server started on port 8501
```

#### Paso 2: Test de conectividad local
Desde el servidor VPS:
```bash
curl http://localhost:8501/_stcore/health
```

Debería responder: `{"status": "ok"}`

#### Paso 3: Test del WebSocket
```bash
curl -i -N -H "Connection: Upgrade" \
     -H "Upgrade: websocket" \
     http://localhost:8501/_stcore/stream
```

### 6. Troubleshooting

#### Problema: "Service not reachable"

**Causa probable**: Puerto no expuesto correctamente

**Solución**: 
1. En Easypanel, ir a "Networking" o "Ports"
2. Exponer puerto `8501`
3. Mapear a puerto público (ej: 80 o 443)

#### Problema: Aplicación lenta o se congela

**Causa**: Falta de memoria

**Solución**:
1. Verificar uso de memoria: `docker stats`
2. Si supera 2GB, aumentar límite en `docker-compose.yml`
3. O cambiar a `MODO_CARGA_SEDES=PRINCIPAL`

#### Problema: WebSocket disconnecting

**Causa**: Proxy inverso mal configurado

**Solución**: Agregar headers de WebSocket (ver sección 3)

### 7. Acceso desde Navegador

Una vez deployado, acceder a:
```
http://<tu-dominio-o-ip>:8501
```

O si configuraste proxy inverso:
```
http://<tu-dominio>
```

### 8. Comandos Útiles

```bash
# Ver logs en tiempo real
docker logs -f sitis-app

# Reiniciar aplicación
docker-compose restart

# Limpiar cache
docker-compose down && docker-compose up -d

# Ver uso de recursos
docker stats sitis-app

# Acceder al contenedor
docker exec -it sitis-app /bin/bash
```

### 9. Configuración de Easypanel Específica

En el panel de Easypanel:

1. **Service Type**: Seleccionar "App"
2. **Source**: GitHub
3. **Branch**: `main`
4. **Build Method**: Dockerfile
5. **Port**: 8501
6. **Auto Deploy**: Activado (opcional)

### 10. Health Check en Easypanel

Si Easypanel permite configurar health check:

- **Path**: `/_stcore/health`
- **Port**: 8501
- **Initial delay**: 180 segundos
- **Interval**: 30 segundos
- **Timeout**: 10 segundos
- **Retries**: 5

---

## 📊 Monitoreo

### Métricas a observar:
- Tiempo de carga inicial: ~40-60 segundos
- Memoria en uso: ~1.5-2 GB (modo PRINCIPAL)
- CPU: Pico inicial al cargar, luego bajo
- Conexiones WebSocket: 1 por usuario activo

---

## 🔐 Seguridad

1. **Nunca** commitear credenciales en GitHub
2. Usar variables de entorno en Easypanel
3. Configurar HTTPS en el proxy inverso
4. Limitar acceso por IP si es necesario
5. Rotar secretos regularmente

---

## 📞 Soporte

Si nada de esto funciona:
1. Copiar logs completos desde "🚀 Iniciando aplicación SITIS..."
2. Verificar que puerto 8501 esté accesible
3. Revisar configuración de firewall/seguridad del VPS

