# ============================================================
# Civilization ABM — Imagen Docker reproducible
# ============================================================
# Uso:
#   docker build -t civilization-abm .
#   docker run --rm -v $(pwd)/results:/app/results civilization-abm
#   docker run --rm -p 8888:8888 civilization-abm jupyter
# ============================================================

FROM python:3.11-slim

LABEL maintainer="civilization-abm"
LABEL description="Simulación ABM de civilización artificial"

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Dependencias del sistema (mínimas)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install jupyter nbconvert pyarrow

# Copiar código
COPY . .

# Crear directorio de resultados
RUN mkdir -p results

# Puerto para Jupyter
EXPOSE 8888

# Punto de entrada por defecto: experimentos completos
# Sobreescribir con: docker run ... python main.py
ENTRYPOINT ["python"]
CMD ["experiments/run.py"]
