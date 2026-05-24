import re
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

estudiantes = []
_next_id = 1

SEMESTRES_VALIDOS = {'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X'}
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')


def validar_estudiante(datos):
    """Valida los campos del estudiante y retorna lista de errores."""
    errores = []

    if not datos:
        return ['No se recibieron datos']

    nombre = (datos.get('nombre') or '').strip()
    email = (datos.get('email') or '').strip()
    carrera = (datos.get('carrera') or '').strip()
    semestre = (datos.get('semestre') or '').strip()

    # Nombre: obligatorio, mínimo 3 caracteres, solo letras y espacios
    if not nombre:
        errores.append('El nombre es obligatorio')
    elif len(nombre) < 3:
        errores.append('El nombre debe tener al menos 3 caracteres')
    elif not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$', nombre):
        errores.append('El nombre solo puede contener letras y espacios')

    # Email: obligatorio, formato válido
    if not email:
        errores.append('El correo electrónico es obligatorio')
    elif not EMAIL_REGEX.match(email):
        errores.append('El correo electrónico no tiene un formato válido')

    # Carrera: obligatorio, mínimo 3 caracteres
    if not carrera:
        errores.append('La carrera es obligatoria')
    elif len(carrera) < 3:
        errores.append('La carrera debe tener al menos 3 caracteres')

    # Semestre: obligatorio, valor válido
    if not semestre:
        errores.append('El semestre es obligatorio')
    elif semestre not in SEMESTRES_VALIDOS:
        errores.append('El semestre seleccionado no es válido')

    return errores


def verificar_email_duplicado(email, excluir_id=None):
    """Verifica si el email ya está registrado por otro estudiante."""
    for est in estudiantes:
        if est.get('email', '').lower() == email.lower():
            if excluir_id is None or est.get('id') != excluir_id:
                return True
    return False


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/estudiantes', methods=['GET'])
def listar():
    return jsonify(estudiantes)


@app.route('/estudiantes', methods=['POST'])
def agregar():
    global _next_id
    datos = request.json
    errores = validar_estudiante(datos)

    email = (datos.get('email') or '').strip()
    if not errores and verificar_email_duplicado(email):
        errores.append('Ya existe un estudiante con ese correo electrónico')

    if errores:
        return jsonify({"ok": False, "errores": errores}), 400

    datos['nombre'] = datos['nombre'].strip()
    datos['email'] = datos['email'].strip().lower()
    datos['carrera'] = datos['carrera'].strip()
    datos['semestre'] = datos['semestre'].strip()
    datos['id'] = _next_id
    _next_id += 1
    estudiantes.append(datos)
    return jsonify({"ok": True, "id": datos['id']}), 201


@app.route('/estudiantes/<int:i>', methods=['PUT'])
def actualizar(i):
    for idx, est in enumerate(estudiantes):
        if est.get('id') == i:
            datos = request.json
            errores = validar_estudiante(datos)

            email = (datos.get('email') or '').strip()
            if not errores and verificar_email_duplicado(email, excluir_id=i):
                errores.append('Ya existe un estudiante con ese correo electrónico')

            if errores:
                return jsonify({"ok": False, "errores": errores}), 400

            datos['nombre'] = datos['nombre'].strip()
            datos['email'] = datos['email'].strip().lower()
            datos['carrera'] = datos['carrera'].strip()
            datos['semestre'] = datos['semestre'].strip()
            datos['id'] = i
            estudiantes[idx] = datos
            return jsonify({"actualizado": True})
    return jsonify({"error": "Estudiante no encontrado"}), 404


@app.route('/estudiantes/<int:i>', methods=['DELETE'])
def eliminar(i):
    for idx, est in enumerate(estudiantes):
        if est.get('id') == i:
            estudiantes.pop(idx)
            return jsonify({"eliminado": True})
    return jsonify({"error": "Estudiante no encontrado"}), 404


if __name__ == '__main__':
    app.run(debug=True, port=5000)
