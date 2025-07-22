from flask import Flask
from flask_cors import CORS

app = Flask(__name__, static_folder='static')
CORS(app)   # vai permitir Access-Control-Allow-Origin: * em TODAS as rotas

# garante que TODO response (sucesso ou erro) receba o header de CORS
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

# Importa e registra o blueprint de roteamento
from backend.routing.routes import routes as routes_blueprint
app.register_blueprint(routes_blueprint)

from backend.sensor_control.sensor_routes import sensor_bp
app.register_blueprint(sensor_bp, url_prefix='/api/sensor_control')

if __name__ == '__main__':
    from backend.init_services import initialize_services
    initialize_services()
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)