from flask import Flask
from app.routes import main_bp
from app.agents import agents_bp

def create_app():
    app = Flask(__name__)
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(agents_bp, url_prefix='/api/agents')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True) 