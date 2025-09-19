FROM python:3.11-slim

WORKDIR /app

# Copiar solo el requirements.txt **al WORKDIR**
COPY worldwild_backend/requirements.txt .
COPY api/assets/ /app/worldwild_backend/api/assets/

# Instalar dependencias
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copiar todo el proyecto
COPY . .

# Exponer puerto
EXPOSE 8000

# Comando por defecto
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000", "--settings=worldwild_backend.settings.local"]

