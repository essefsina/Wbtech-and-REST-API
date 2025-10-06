from flask import Flask, request, jsonify, abort

app = Flask(__name__)

countries = [
    {"id": 1, "name": "Thailand", "capital": "Bangkok", "area": 513120},
    {"id": 2, "name": "Australia", "capital": "Canberra", "area": 7617930},
    {"id": 3, "name": "Egypt", "capital": "Cairo", "area": 1010408}
]

def _find_next_id():
    return max(country["id"] for country in countries) + 1 if countries else 1

@app.route('/countries', methods=['GET'])
def get_countries():
    return jsonify(countries)

@app.route('/countries/<int:id>', methods=['GET'])
def get_country(id):
    country = next((c for c in countries if c['id'] == id), None)
    if not country:
        abort(404, description="Country not found")
    return jsonify(country)

@app.route('/countries', methods=['POST'])
def add_country():
    if not request.is_json:
        abort(415, description="Request must be JSON")
    new_country = request.get_json()
    new_country['id'] = _find_next_id()
    countries.append(new_country)
    return jsonify(new_country), 201

@app.route('/countries/<int:id>', methods=['PUT'])
def update_country(id):
    if not request.is_json:
        abort(415, description="Request must be JSON")
    country = next((c for c in countries if c['id'] == id), None)
    if not country:
        abort(404, description="Country not found")
    updated = request.get_json()
    country.update(updated)
    country['id'] = id  # Ensure id does not change
    return jsonify(country)

@app.route('/countries/<int:id>', methods=['PATCH'])
def patch_country(id):
    if not request.is_json:
        abort(415, description="Request must be JSON")
    country = next((c for c in countries if c['id'] == id), None)
    if not country:
        abort(404, description="Country not found")
    patch_data = request.get_json()
    country.update(patch_data)
    country['id'] = id
    return jsonify(country)

@app.route('/countries/<int:id>', methods=['DELETE'])
def delete_country(id):
    global countries
    country = next((c for c in countries if c['id'] == id), None)
    if not country:
        abort(404, description="Country not found")
    countries = [c for c in countries if c['id'] != id]
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)
