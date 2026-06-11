from flask import Flask, request, jsonify
from flask_cors import CORS
from two_phase_commit import TwoPhaseCommit
import logging
import os
import psycopg2
import psycopg2.extras
from datetime import datetime

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de conexiones desde variables de entorno
DB_CONFIGS = {
    'arequipa': {
        'host': os.getenv('DB_AREQUIPA_HOST', 'localhost'),
        'port': int(os.getenv('DB_AREQUIPA_PORT', 5433)),
        'database': 'banco_arequipa',
        'user': os.getenv('DB_USER', 'admin'),
        'password': os.getenv('DB_PASSWORD', 'admin123')
    },
    'cusco': {
        'host': os.getenv('DB_CUSCO_HOST', 'localhost'),
        'port': int(os.getenv('DB_CUSCO_PORT', 5434)),
        'database': 'banco_cusco',
        'user': os.getenv('DB_USER', 'admin'),
        'password': os.getenv('DB_PASSWORD', 'admin123')
    },
    'trujillo': {
        'host': os.getenv('DB_TRUJILLO_HOST', 'localhost'),
        'port': int(os.getenv('DB_TRUJILLO_PORT', 5435)),
        'database': 'banco_trujillo',
        'user': os.getenv('DB_USER', 'admin'),
        'password': os.getenv('DB_PASSWORD', 'admin123')
    },
    'logs': {
        'host': os.getenv('DB_LOGS_HOST', 'localhost'),