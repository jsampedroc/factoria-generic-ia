#!/bin/bash

echo "🗑️  Limpiando archivos de la factoría..."

# Detener contenedores de Docker si están corriendo
docker-compose down 2>/dev/null

# Borrar carpetas de salida
rm -rf output/backend/*
rm -rf output/frontend/*
rm -f output/docker-compose.yml
rm -f output/Dockerfile

# Crear estructuras limpias de nuevo
mkdir -p output/backend output/frontend

echo "✅ Factoría reseteada. Lista para un nuevo proyecto."