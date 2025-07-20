from flask import Flask
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

# Importa e registra o blueprint de roteamento
from backend.routing.routes import routes as routes_blueprint
app.register_blueprint(routes_blueprint)

from backend.sensor_control.sensor_routes import sensor_bp
app.register_blueprint(sensor_bp, url_prefix='/api/sensor_control')

if __name__ == '__main__':
    from backend.init_services import initialize_services
    initialize_services()
    app.run(host="0.0.0.0", debug=True, port=5000, use_reloader=False)