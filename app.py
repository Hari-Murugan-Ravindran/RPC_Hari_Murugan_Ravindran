from flask import Flask, jsonify, request
import uuid , math
from datetime import datetime

app = Flask(__name__)
receipts = {}

def receipt_id_generation():
    return str(uuid.uuid4())


def date_validation(date_str):
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def time_validation(time_str):
    try:
        datetime.strptime(time_str, '%H:%M')
        return True
    except ValueError:
        return False


def price_validation(price_str):
    try:
        float(price_str)
        return True
    except ValueError:
        return False


def poins_computation(receipt):
    points = 0

    retailer_points = sum(1 for char in receipt['retailer'] if char.isalnum())
    points += retailer_points

    total = float(receipt['total'])
    if total.is_integer() and total != 0:
        points += 50

    if total % 0.25 == 0:
        points += 25

    points += len(receipt['items']) // 2 * 5

    for item in receipt['items']:
        description_length = len(item['shortDescription'].strip())
        if description_length % 3 == 0:
            price = float(item['price'])
            item_points = int(math.ceil(price * 0.2))
            points += item_points

    purchase_time = datetime.strptime(receipt['purchaseTime'], "%H:%M")
    if purchase_time.hour >= 14 and purchase_time.hour < 16:
        points += 10

    purchase_date = datetime.strptime(receipt['purchaseDate'], "%Y-%m-%d")
    if purchase_date.day % 2 != 0:
        points += 6

    return points


@app.route('/receipts/process', methods=['POST'])
def receipt_processing():
    receipt = request.get_json()
    if not validate_receipt(receipt):
        return jsonify({"error": "Invalid receipt format"}), 400

    receipt_id = receipt_id_generation()
    receipts[receipt_id] = receipt
    return jsonify({"id": receipt_id})


@app.route('/receipts/<string:receipt_id>/points', methods=['GET'])
def get_points(receipt_id):
    receipt = receipts.get(receipt_id)
    if not receipt:
        return jsonify({"error": "Receipt not found"}), 404

    points = poins_computation(receipt)
    return jsonify({"points": points})


def validate_receipt(receipt):
    required_fields = ['retailer', 'purchaseDate', 'purchaseTime', 'items', 'total']
    for field in required_fields:
        if field not in receipt:
            return False

    if not isinstance(receipt['retailer'], str) or not receipt['retailer'].strip():
        return False

    if not isinstance(receipt['purchaseDate'], str) or not date_validation(receipt['purchaseDate']):
        return False

    if not isinstance(receipt['purchaseTime'], str) or not time_validation(receipt['purchaseTime']):
        return False

    if not isinstance(receipt['items'], list) or len(receipt['items']) == 0:
        return False

    for item in receipt['items']:
        if not isinstance(item, dict) or 'shortDescription' not in item or 'price' not in item:
            return False

        if not isinstance(item['shortDescription'], str) or not item['shortDescription'].strip():
            return False

        if not isinstance(item['price'], str) or not price_validation(item['price']):
            return False

    if not isinstance(receipt['total'], str) or not price_validation(receipt['total']):
        return False

    return True

if __name__ == '__main__':
    app.run()
