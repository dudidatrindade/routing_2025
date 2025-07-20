FROM python:3.9-slim
WORKDIR /app

# 1) Instala dependências
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 2) Copia todo o código do backend
COPY backend ./backend

EXPOSE 5001
# 3) Executa o app via módulo
CMD ["python", "-m", "backend.app"]
