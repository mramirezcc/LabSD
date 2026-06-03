"""
Proxy local para Calculadora SOAP
Lab 07 - Sistemas Distribuidos - UNSA 2026A

Arquitectura:
  HTML (navegador) --> este proxy (localhost:5000) --> dneonline.com (SOAP)

Ejecutar:
  pip install zeep flask flask-cors
  python proxy_soap.py

Luego abrir calculadora_soap.html en el navegador.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from zeep import Client
from zeep.exceptions import Fault

app = Flask(__name__)
CORS(app)  # permite que el HTML en el navegador llame a este servidor

WSDL_URL = 'http://www.dneonline.com/calculator.asmx?WSDL'
client   = None

def get_client():
    global client
    if client is None:
        client = Client(WSDL_URL)
    return client

@app.route('/soap', methods=['POST'])
def soap_proxy():
    data = request.get_json()
    op   = data.get('operation')
    a    = int(data.get('a', 0))
    b    = int(data.get('b', 0))

    try:
        c = get_client()
        ops = {
            'Add'     : lambda: c.service.Add(a, b),
            'Subtract': lambda: c.service.Subtract(a, b),
            'Multiply': lambda: c.service.Multiply(a, b),
            'Divide'  : lambda: c.service.Divide(a, b),
        }
        if op not in ops:
            return jsonify({'error': f'Operación desconocida: {op}'}), 400

        resultado = ops[op]()
        return jsonify({'result': resultado, 'operation': op, 'a': a, 'b': b})

    except Fault as e:
        return jsonify({'error': f'SOAP Fault: {e.message}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    try:
        get_client()
        return jsonify({'status': 'online', 'wsdl': WSDL_URL})
    except Exception as e:
        return jsonify({'status': 'offline', 'error': str(e)}), 503

if __name__ == '__main__':
    print("=" * 55)
    print("  Proxy SOAP iniciado en http://localhost:5000")
    print("  Abre calculadora_soap.html en tu navegador")
    print("=" * 55)
    app.run(port=5000, debug=False)
