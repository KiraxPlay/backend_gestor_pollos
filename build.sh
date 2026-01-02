
echo "========================================"
echo "         BUILD EJECUTANDOSE         "
echo "========================================"

echo "📦 1. Instalando dependencias..."
pip install -r requirements.txt

echo "🔄 2. Aplicando migraciones a Supabase..."
python manage.py migrate

echo "📁 3. Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

echo "✅ Build completado exitosamente!"
echo "========================================"