#!/bin/bash

echo "🚀 Iniciando Factoría de Software de IA..."

# 1. Ejecutar el equipo de agentes para generar el código
python alutech_pro_enterprise_final.py

# 2. Una vez generado el código, levantar la infraestructura
echo "🏗️  Levantando contenedores locales..."
docker-compose up --build -d

echo "✅ App de Facturación lista en http://localhost:3000"
