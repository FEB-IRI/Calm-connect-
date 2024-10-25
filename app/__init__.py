from flask import Flask
from app.views import bp

calm = Flask(__name__)
calm.register_blueprint(bp)
calm.secret_key='!QAZXSW#EDCFRTG'