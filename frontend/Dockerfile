FROM python:3.9-slim

WORKDIR /app

# copia todos os arquivos estáticos (HTML, CSS, JS) da pasta public
COPY public/ ./

# expõe a porta 8000 para o host
EXPOSE 8000

# inicia o servidor estático embutido no Python
CMD ["python", "-m", "http.server", "8000"]
