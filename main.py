from flask import Flask, render_template, send_from_directory, request, redirect, url_for
from flask_cors import CORS
from flask import Flask, render_template, request, jsonify, session
from routes.wep import defaultAPI
from routes.auth import authAPI
from routes.lab import labAPI
from routes.api import apiAPI
from dotenv import load_dotenv
import os


load_dotenv()


app = Flask(__name__)
CORS(app)
app.template_folder = 'templates'
app.static_folder = 'static'
app.secret_key = os.getenv("PRIVATE_KEY")

app.register_blueprint(defaultAPI, url_prefix='/')
app.register_blueprint(authAPI, url_prefix='/auth')
# ส่วนหน้าเข้าระบบแอดมิน
app.register_blueprint(labAPI, url_prefix='/lab')
app.register_blueprint(apiAPI, url_prefix='/api')


if __name__ == '__main__':
    app.run(debug=True)
    # app.run(host=os.getenv('HOST'), port=int(os.getenv('PORT')), debug=True)


