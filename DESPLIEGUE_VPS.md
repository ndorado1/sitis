# 🚀 Guía de Despliegue en VPS con Docker

Esta guía te lleva paso a paso para desplegar la aplicación SITIS en tu propio VPS.

---

## 📋 Requisitos del VPS

### Mínimo Recomendado:
- **RAM**: 2 GB (para 1 sede) / 4 GB (para 3 sedes)
- **CPU**: 2 cores
- **Disco**: 20 GB SSD
- **SO**: Ubuntu 20.04/22.04 LTS (recomendado)
- **Costo**: $10-20/mes

### Proveedores Recomendados:
| Proveedor | Plan | RAM | Precio | Link |
|-----------|------|-----|--------|------|
| **DigitalOcean** | Basic | 2 GB | $12/mes | digitalocean.com |
| **Linode** | Nanode | 2 GB | $12/mes | linode.com |
| **Vultr** | Cloud Compute | 2 GB | $12/mes | vultr.com |
| **AWS EC2** | t3.small | 2 GB | ~$15/mes | aws.amazon.com |
| **Hetzner** | CX21 | 4 GB | €5.83/mes | hetzner.com |

---

## 🔧 Paso 1: Preparar el VPS

### 1.1 Conectarse al VPS

```bash
ssh root@tu-ip-vps
# o
ssh usuario@tu-ip-vps
```

### 1.2 Actualizar el Sistema

```bash
sudo apt update && sudo apt upgrade -y
```

### 1.3 Instalar Docker

```bash
# Instalar dependencias
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Agregar repositorio oficial de Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Verificar instalación
docker --version
```

### 1.4 Instalar Docker Compose

```bash
# Descargar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Dar permisos de ejecución
sudo chmod +x /usr/local/bin/docker-compose

# Verificar instalación
docker-compose --version
```

### 1.5 Configurar Usuario (Opcional pero Recomendado)

```bash
# Agregar usuario al grupo docker
sudo usermod -aG docker $USER

# Aplicar cambios (re-login)
newgrp docker
```

---

## 📦 Paso 2: Clonar el Repositorio

```bash
# Instalar git si no está instalado
sudo apt install -y git

# Clonar el repositorio
git clone https://github.com/ndorado1/sitis.git
cd sitis

# Verificar archivos
ls -la
```

---

## 🔐 Paso 3: Configurar Credenciales

### 3.1 Crear Archivo .env

```bash
# Copiar ejemplo
cp env.example .env

# Editar con nano (o vim)
nano .env
```

### 3.2 Configurar Credenciales

Reemplaza los valores de ejemplo con tus credenciales reales de Azure AD:

```env
SHAREPOINT_CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
SHAREPOINT_CLIENT_SECRET=tu_client_secret_aqui
SHAREPOINT_TENANT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

Ver `PERMISOS_AZURE_AD.md` para obtener estas credenciales.

Guardar: `Ctrl + O`, luego `Enter`, luego `Ctrl + X`

---

## 🚀 Paso 4: Desplegar la Aplicación

### Opción A: Usando el Script de Despliegue (Recomendado)

```bash
# Dar permisos de ejecución
chmod +x deploy.sh

# Ejecutar script
./deploy.sh
```

Selecciona opción `1` (Construir y desplegar)

### Opción B: Comandos Manuales

```bash
# Construir imagen
docker-compose build

# Iniciar contenedor
docker-compose up -d

# Ver logs
docker-compose logs -f
```

---

## ✅ Paso 5: Verificar Despliegue

### 5.1 Verificar Estado del Contenedor

```bash
docker-compose ps
```

Deberías ver algo como:
```
NAME              STATUS          PORTS
sitis-streamlit   Up 2 minutes    0.0.0.0:8501->8501/tcp
```

### 5.2 Ver Logs en Tiempo Real

```bash
docker-compose logs -f
```

Busca mensajes como:
```
✅ Datos consolidados de 3 sede(s): Sede Principal, Sede Piéndamo, Sede Silvia
```

### 5.3 Acceder a la Aplicación

Abre en tu navegador:
```
http://IP-DE-TU-VPS:8501
```

Por ejemplo:
```
http://165.232.100.50:8501
```

---

## 🌐 Paso 6: Configurar Dominio (Opcional)

### 6.1 Configurar DNS

En tu proveedor de dominio (ej: GoDaddy, Namecheap):
1. Crear registro A apuntando a la IP de tu VPS
2. Ejemplo: `sitis.tudominio.com` → `165.232.100.50`

### 6.2 Instalar Nginx como Proxy Inverso

```bash
# Instalar Nginx
sudo apt install -y nginx

# Configurar sitio
sudo nano /etc/nginx/sites-available/sitis
```

Contenido:
```nginx
server {
    listen 80;
    server_name sitis.tudominio.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Activar sitio
sudo ln -s /etc/nginx/sites-available/sitis /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 6.3 Instalar Certificado SSL (HTTPS)

```bash
# Instalar Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtener certificado
sudo certbot --nginx -d sitis.tudominio.com

# Renovación automática ya está configurada
```

Ahora accede con HTTPS:
```
https://sitis.tudominio.com
```

---

## 🔄 Actualizar la Aplicación

### Opción A: Con Script

```bash
cd sitis
git pull origin main
./deploy.sh
# Selecciona opción 1 (Reconstruir)
```

### Opción B: Manual

```bash
cd sitis
git pull origin main
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## 🛠️ Comandos Útiles

### Ver Estado
```bash
docker-compose ps
docker stats sitis-streamlit
```

### Ver Logs
```bash
# Logs en tiempo real
docker-compose logs -f

# Últimas 100 líneas
docker-compose logs --tail=100

# Logs de un período específico
docker-compose logs --since 30m
```

### Reiniciar
```bash
docker-compose restart
```

### Detener
```bash
docker-compose down
```

### Limpiar Todo
```bash
docker-compose down -v
docker system prune -a --volumes
```

### Entrar al Contenedor
```bash
docker exec -it sitis-streamlit bash
```

---

## 🔒 Seguridad Adicional

### 1. Configurar Firewall

```bash
# Instalar UFW
sudo apt install -y ufw

# Permitir SSH (¡IMPORTANTE!)
sudo ufw allow 22/tcp

# Permitir puerto de la aplicación
sudo ufw allow 8501/tcp

# Si usas Nginx
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Activar firewall
sudo ufw enable

# Ver estado
sudo ufw status
```

### 2. Configurar Auto-reinicio

El contenedor ya tiene `restart: unless-stopped` configurado en docker-compose.yml, así que se reiniciará automáticamente si falla o si se reinicia el VPS.

### 3. Monitoreo

```bash
# Instalar htop para monitorear recursos
sudo apt install -y htop

# Ejecutar
htop
```

---

## 🐛 Troubleshooting

### Problema: Contenedor no inicia

```bash
# Ver logs completos
docker-compose logs

# Verificar credenciales
cat .env

# Reconstruir desde cero
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Problema: Sin memoria suficiente

```bash
# Ver uso de memoria
free -h

# Si necesitas más memoria, considera:
# 1. Upgrade de VPS
# 2. Configurar swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### Problema: Puerto 8501 bloqueado

```bash
# Verificar si el puerto está en uso
sudo netstat -tulpn | grep 8501

# Si hay otro proceso, matarlo o cambiar puerto
# Para cambiar puerto, edita docker-compose.yml:
# ports:
#   - "8080:8501"  # Cambia 8080 por el puerto que prefieras
```

### Problema: No se puede conectar desde fuera

```bash
# Verificar que el contenedor escucha en todas las interfaces
docker-compose logs | grep "0.0.0.0"

# Verificar firewall
sudo ufw status

# Verificar si el VPS tiene firewall en el panel de control
# (DigitalOcean, AWS Security Groups, etc.)
```

---

## 📊 Monitoreo de Performance

### Instalar Portainer (GUI para Docker)

```bash
docker volume create portainer_data

docker run -d -p 9000:9000 \
  --name=portainer \
  --restart=always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data \
  portainer/portainer-ce:latest
```

Accede en: `http://IP-VPS:9000`

---

## 💰 Costos Estimados

| Componente | Costo Mensual |
|------------|---------------|
| VPS (2GB RAM) | $12 |
| Dominio (opcional) | $10-15/año |
| **Total** | **~$12-14/mes** |

Mucho más económico que Streamlit Teams ($250/mes)

---

## ✅ Checklist Final

- [ ] VPS creado y accesible vía SSH
- [ ] Docker y Docker Compose instalados
- [ ] Repositorio clonado
- [ ] Archivo .env configurado con credenciales
- [ ] Aplicación desplegada con docker-compose
- [ ] Aplicación accesible en http://IP:8501
- [ ] (Opcional) Dominio configurado
- [ ] (Opcional) SSL/HTTPS configurado
- [ ] Firewall configurado
- [ ] Auto-reinicio funcionando

---

## 📞 Soporte

Si tienes problemas:
1. Revisa los logs: `docker-compose logs`
2. Verifica credenciales en `.env`
3. Consulta troubleshooting arriba
4. Revisa documentación de Docker

---

**🎉 ¡Listo! Tu aplicación SITIS está ejecutándose en tu VPS con todas las sedes funcionando correctamente.**

