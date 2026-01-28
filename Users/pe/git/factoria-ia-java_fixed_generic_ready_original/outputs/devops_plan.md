**Dockerfile**
```dockerfile
# Dockerfile
FROM eclipse-temurin:21-jdk-alpine AS builder

WORKDIR /app

# Copy Maven wrapper and pom.xml
COPY mvnw .
COPY .mvn .mvn
COPY pom.xml .

# Download dependencies
RUN ./mvnw dependency:go-offline -B

# Copy source code
COPY src ./src

# Build the application
RUN ./mvnw clean package -DskipTests

# Runtime stage
FROM eclipse-temurin:21-jre-alpine

WORKDIR /app

# Create non-root user
RUN addgroup -S spring && adduser -S spring -G spring
USER spring:spring

# Copy built artifact from builder stage
COPY --from=builder /app/target/*.jar app.jar

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8080/actuator/health || exit 1

# Run the application
ENTRYPOINT ["java", "-jar", "app.jar"]
```

**docker-compose.yml**
```yaml
# docker-compose.yml
version: '3.8'

services:
  # Main application
  industrial-saas-backend:
    build: .
    container_name: industrial-saas-backend
    ports:
      - "8080:8080"
    environment:
      - SPRING_PROFILES_ACTIVE=docker
      - DB_HOST=postgres-db
      - DB_PORT=5432
      - DB_NAME=industrial_saas
      - DB_USERNAME=saas_user
      - DB_PASSWORD=${DB_PASSWORD:-ChangeMe123!}
      - JAVA_OPTS=-Xmx512m -Xms256m
    depends_on:
      postgres-db:
        condition: service_healthy
    networks:
      - industrial-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:8080/actuator/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # PostgreSQL database
  postgres-db:
    image: postgres:15-alpine
    container_name: postgres-db
    environment:
      - POSTGRES_DB=industrial_saas
      - POSTGRES_USER=saas_user
      - POSTGRES_PASSWORD=${DB_PASSWORD:-ChangeMe123!}
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./init-db:/docker-entrypoint-initdb.d
    networks:
      - industrial-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U saas_user -d industrial_saas"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Adminer for database management (optional)
  adminer:
    image: adminer:latest
    container_name: adminer
    ports:
      - "8081:8080"
    environment:
      - ADMINER_DEFAULT_SERVER=postgres-db
    depends_on:
      - postgres-db
    networks:
      - industrial-network
    restart: unless-stopped

volumes:
  postgres-data:
    driver: local

networks:
  industrial-network:
    driver: bridge
```

**Scripts de arranque**

**start.sh**
```bash
#!/bin/bash
# start.sh - Script principal de arranque del sistema

set -e

echo "========================================="
echo "  Industrial SaaS Backend - Iniciando    "
echo "========================================="

# Cargar variables de entorno
if [ -f .env ]; then
    echo "Cargando variables de entorno desde .env"
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "Archivo .env no encontrado, usando valores por defecto"
fi

# Verificar Docker y Docker Compose
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker no está instalado. Por favor instale Docker primero."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "ERROR: Docker Compose no está instalado. Por favor instale Docker Compose primero."
    exit 1
fi

# Crear directorios necesarios
mkdir -p init-db
mkdir -p logs

# Generar archivo de inicialización de base de datos si no existe
if [ ! -f init-db/01-init.sql ]; then
    cat > init-db/01-init.sql << 'EOF'
-- Script de inicialización de base de datos para Industrial SaaS
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tabla de fábricas
CREATE TABLE IF NOT EXISTS factories (
    factory_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    street VARCHAR(255),
    city VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100),
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de máquinas
CREATE TABLE IF NOT EXISTS machines (
    machine_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    serial_number VARCHAR(100) NOT NULL UNIQUE,
    model VARCHAR(100) NOT NULL,
    installation_date TIMESTAMP NOT NULL,
    operational_status VARCHAR(50) NOT NULL DEFAULT 'IDLE',
    factory_id UUID REFERENCES factories(factory_id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de órdenes de producción
CREATE TABLE IF NOT EXISTS production_orders (
    order_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_code VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    priority VARCHAR(20) NOT NULL DEFAULT 'MEDIUM',
    status VARCHAR(30) NOT NULL DEFAULT 'SCHEDULED',
    factory_id UUID REFERENCES factories(factory_id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Índices para mejor performance
CREATE INDEX idx_machines_factory_id ON machines(factory_id);
CREATE INDEX idx_machines_serial_number ON machines(serial_number);
CREATE INDEX idx_production_orders_factory_id ON production_orders(factory_id);
CREATE INDEX idx_production_orders_status ON production_orders(status);
CREATE INDEX idx_production_orders_priority ON production_orders(priority);

-- Datos iniciales de prueba (opcional)
INSERT INTO factories (factory_id, name, street, city, postal_code, country, status) 
VALUES 
    ('11111111-1111-1111-1111-111111111111', 'Fábrica Principal', 'Calle Industria 123', 'Madrid', '28013', 'España', 'ACTIVE'),
    ('22222222-2222-2222-2222-222222222222', 'Planta Norte', 'Avenida Tecnología 456', 'Barcelona', '08001', 'España', 'ACTIVE')
ON CONFLICT (factory_id) DO NOTHING;

INSERT INTO machines (machine_id, serial_number, model, installation_date, operational_status, factory_id)
VALUES 
    ('33333333-3333-3333-3333-333333333333', 'MACH-001', 'Modelo X-1000', '2024-01-15 10:00:00', 'OPERATIONAL', '11111111-1111-1111-1111-111111111111'),
    ('44444444-4444-4444-4444-444444444444', 'MACH-002', 'Modelo Y-2000', '2024-02-20 14:30:00', 'IDLE', '11111111-1111-1111-1111-111111111111')
ON CONFLICT (machine_id) DO NOTHING;

-- Trigger para actualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_factories_updated_at BEFORE UPDATE ON factories FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_machines_updated_at BEFORE UPDATE ON machines FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_orders_updated_at BEFORE UPDATE ON production_orders FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

EOF
    echo "Archivo de inicialización de base de datos creado"
fi

# Construir y levantar los servicios
echo "Construyendo y levantando servicios con Docker Compose..."
docker-compose up --build -d

# Esperar a que los servicios estén saludables
echo "Esperando a que los servicios estén listos..."
sleep 10

# Verificar estado de los servicios
echo ""
echo "Verificando estado de los servicios:"
echo "-----------------------------------"

if docker-compose ps | grep -q "Up (healthy)"; then
    echo "✅ Todos los servicios están funcionando correctamente"
else
    echo "⚠️  Algunos servicios pueden tener problemas. Verifique con: docker-compose ps"
fi

# Mostrar información de acceso
echo ""
echo "========================================="
echo "  Sistema desplegado exitosamente!       "
echo "========================================="
echo ""
echo "📊 Servicios disponibles:"
echo "  • Aplicación Principal: http://localhost:8080"
echo "  • API REST: http://localhost:8080/api"
echo "  • Health Check: http://localhost:8080/actuator/health"
echo "  • Adminer (DB Manager): http://localhost:8081"
echo ""
echo "🔧 Comandos útiles:"
echo "  • Ver logs: docker-compose logs -f"
echo "  • Detener: docker-compose down"
echo "  • Reiniciar: docker-compose restart"
echo "  • Ver estado: docker-compose ps"
echo ""
echo "📝 Variables de entorno configuradas en .env"
echo "========================================="
```

**stop.sh**
```bash
#!/bin/bash
# stop.sh - Script para detener el sistema

echo "Deteniendo Industrial SaaS Backend..."
docker-compose down

echo "Sistema detenido."
```

**restart.sh**
```bash
#!/bin/bash
# restart.sh - Script para reiniciar el sistema

echo "Reiniciando Industrial SaaS Backend..."
docker-compose restart

echo "Esperando a que los servicios se reinicien..."
sleep 5

echo "Sistema reiniciado."
echo "Verifique el estado con: docker-compose ps"
```

**logs.sh**
```bash
#!/bin/bash
# logs.sh - Script para ver logs del sistema

if [ "$1" = "-f" ]; then
    echo "Mostrando logs en tiempo real..."
    docker-compose logs -f
else
    echo "Mostrando últimos logs..."
    docker-compose logs --tail=100
fi
```

**check-health.sh**
```bash
#!/bin/bash
# check-health.sh - Script para verificar salud del sistema

echo "Verificando salud del sistema Industrial SaaS..."
echo ""

# Verificar contenedores
echo "📦 Estado de contenedores:"
docker-compose ps

echo ""
echo "🔍 Verificando endpoints:"

# Verificar aplicación
if curl -s -f http://localhost:8080/actuator/health > /dev/null 2>&1; then
    echo "✅ Aplicación: HTTP 200 OK"
else
    echo "❌ Aplicación: No responde"
fi

# Verificar base de datos
if docker-compose exec -T postgres-db pg_isready -U saas_user -d industrial_saas > /dev/null 2>&1; then
    echo "✅ Base de datos: Conectada"
else
    echo "❌ Base de datos: Error de conexión"
fi

echo ""
echo "📊 Uso de recursos:"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}" | head -5
```

**.env.example**
```properties
# .env.example - Plantilla de variables de entorno
# Copiar este archivo a .env y modificar los valores

# Configuración de Base de Datos
DB_PASSWORD=ChangeMe123!
DB_HOST=postgres-db
DB_PORT=5432
DB_NAME=industrial_saas
DB_USERNAME=saas_user

# Configuración de la Aplicación
SPRING_PROFILES_ACTIVE=docker
SERVER_PORT=8080

# Configuración de JVM
JAVA_OPTS=-Xmx512m -Xms256m -XX:+UseG1GC -XX:MaxGCPauseMillis=200

# Configuración de Logging
LOGGING_LEVEL_COM_INDUSTRIAL_SAAS=INFO
LOGGING_LEVEL_ORG_SPRINGFRAMEWORK=WARN

# Configuración de Seguridad (para desarrollo)
SECURITY_ENABLED=false
```

**README-DEPLOY.md**
```markdown
# Industrial SaaS Backend - Guía de Despliegue

## Requisitos Previos

- Docker 20.10+ y Docker Compose 2.0+
- 2GB de RAM mínimo
- 1GB de espacio en disco

## Despliegue Rápido

1. **Clonar el repositorio**
   ```bash
   git clone <repository-url>
   cd industrial-saas-backend
   ```

2. **Configurar variables de entorno**
   ```bash
   cp .env.example .env
   # Editar .env con sus valores
   ```

3. **Ejecutar el sistema**
   ```bash
   chmod +x *.sh
   ./start.sh
   ```

## Scripts Disponibles

| Script | Descripción |
|--------|-------------|
| `start.sh` | Inicia todos los servicios |
| `stop.sh` | Detiene todos los servicios |
| `restart.sh` | Reinicia los servicios |
| `logs.sh` | Muestra los logs |
| `check-health.sh` | Verifica el estado del sistema |

## Estructura del Sistema

```
industrial-saas-backend/
├── Dockerfile              # Definición de la imagen Docker
├── docker-compose.yml      # Orquestación de servicios
├── .env.example           # Plantilla de variables
├── init-db/               # Scripts SQL de inicialización
├── start.sh              # Script principal
├── stop.sh               # Script de parada
├── restart.sh            # Script de reinicio
├── logs.sh               # Script de logs
└── check-health.sh       # Script de verificación
```

## Servicios Desplegados

1. **industrial-saas-backend** (puerto 8080)
   - Aplicación Spring Boot principal
   - API REST: `http://localhost:8080/api`
   - Health check: `http://localhost:8080/actuator/health`

2. **postgres-db** (puerto 5432)
   - Base de datos PostgreSQL
   - Datos persistentes en volumen `postgres-data`

3. **adminer** (puerto 8081, opcional)
   - Interfaz web para gestión de base de datos
   - Acceso: `http://localhost:8081`

## Variables de Entorno

Crear un archivo `.env` basado en `.env.example`:

```bash
# Configuración esencial
DB_PASSWORD=su_contraseña_segura
SPRING_PROFILES_ACTIVE=docker
```

## Comandos Docker útiles

```bash
# Ver estado de los servicios
docker-compose ps

# Ver logs en tiempo real
docker-compose logs -f

# Acceder a la base de datos
docker-compose exec postgres-db psql -U saas_user -d industrial_saas

# Reconstruir y reiniciar
docker-compose up --build -d

# Limpiar todo (incluyendo volúmenes)
docker-compose down -v
```

## Solución de Problemas

### La aplicación no inicia
```bash
# Ver logs detallados
./logs.sh

# Verificar salud
./check-health.sh

# Reconstruir
docker-compose up --build -d
```

### Base de datos no conecta
```bash
# Verificar que PostgreSQL está corriendo
docker-compose exec postgres-db pg_isready

# Recrear base de datos
docker-compose down -v
./start.sh
```

### Out of memory
Ajustar en `.env`:
```properties
JAVA_OPTS=-Xmx256m -Xms128m
```

## Monitoreo

- Health endpoint: `http://localhost:8080/actuator/health`
- Métricas: `http://localhost:8080/actuator/metrics`
- Info: `http://localhost:8080/actuator/info`

## Backup y Restauración

### Backup de base de datos
```bash
docker-compose exec postgres-db pg_dump -U saas_user industrial_saas > backup_$(date +%Y%m%d).sql
```

### Restauración
```bash
cat backup.sql | docker-compose exec -T postgres-db psql -U saas_user -d industrial_saas
```

## Seguridad en Producción

1. Cambiar todas las contraseñas por defecto
2. Configurar SSL/TLS
3. Habilitar autenticación
4. Configurar firewall
5. Usar secrets management para credenciales