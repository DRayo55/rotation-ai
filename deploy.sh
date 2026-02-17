#!/bin/bash
# Script de despliegue automático para MatchLineup AI

echo "═══════════════════════════════════════════════════════════════"
echo "  🚀 DESPLIEGUE AUTOMÁTICO: MATCHLINEUP AI"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Verificar si estamos en un repositorio Git
if [ ! -d .git ]; then
    echo "📦 Inicializando repositorio Git..."
    git init
    git branch -M main
fi

# Ver estado actual
echo "📋 Estado actual:"
git status --short

# Agregar todos los archivos
echo ""
echo "➕ Agregando archivos..."
git add .

# Mostrar qué se va a commitear
echo ""
echo "📝 Archivos a commitear:"
git status --short

# Pedir mensaje de commit
echo ""
read -p "💬 Mensaje de commit (o Enter para usar default): " commit_msg

if [ -z "$commit_msg" ]; then
    commit_msg="Update: $(date '+%Y-%m-%d %H:%M')"
fi

# Hacer commit
echo ""
echo "💾 Haciendo commit..."
git commit -m "$commit_msg"

# Verificar si existe remote
if ! git remote | grep -q origin; then
    echo ""
    echo "⚠️  No hay remote configurado"
    read -p "🔗 URL del repositorio GitHub: " repo_url
    git remote add origin "$repo_url"
fi

# Push
echo ""
echo "🚀 Subiendo a GitHub..."
git push -u origin main

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  ✅ DESPLIEGUE COMPLETADO"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "📌 Próximos pasos:"
echo "  1. Ir a https://streamlit.io/cloud"
echo "  2. Click en 'New app'"
echo "  3. Seleccionar tu repositorio"
echo "  4. ¡Deploy!"
echo ""
