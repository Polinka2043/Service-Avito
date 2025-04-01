from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from sqlalchemy.sql import text
from flask_sqlalchemy import SQLAlchemy
import time

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'it_is_my_secret_key'
app = Flask(__name__)
app.config.from_object(Config)
app.config['SQLALCHEMY_DATABASE_URI'] ='postgresql://postgres:0000@postgres:5432/Service-Avito'
db = SQLAlchemy(app)
jwt = JWTManager(app)
time.sleep(5)
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    coins = db.Column(db.Integer, default=1000)
    purchases = db.relationship('Purchase', backref='user', lazy=True)
    inventory_items = db.relationship('Inventory', backref='owner', lazy=True)

class Merch(db.Model):
    __tablename__ = 'merch'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    price = db.Column(db.Integer, nullable=False)

class Purchase(db.Model):
    __tablename__ = 'purchase'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    merch_id = db.Column(db.Integer, db.ForeignKey('merch.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    merch = db.relationship('Merch', backref='purchases')

class Inventory(db.Model):
    __tablename__ = 'inventory'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_type = db.Column(db.String(80), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    user = db.relationship('User', backref='inventory')

class CoinTransaction(db.Model):
    __tablename__ = 'coin_transaction'
    id = db.Column(db.Integer, primary_key=True)
    from_user = db.Column(db.String(80), nullable=False)
    to_user = db.Column(db.String(80), nullable=False)
    amount = db.Column(db.Integer, nullable=False)

@app.route('/')
def testBD():
    try:
        db.session.execute(text('SELECT 1'))
        return '<h1>Подключение успешно!</h1>'
    except Exception as e:
        return f'<h1>Ошибка подключения:</h1><p>{str(e)}</p>'

@app.route('/api/auth', methods=['POST'])
def auth():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username, password=password).first()
    if user:
        token = create_access_token(identity=user.username)
        return jsonify(token=token), 200
    return jsonify(errors="Неверные учетные данные."), 401


@app.route('/api/info', methods=['GET'])
@jwt_required()
def info():
    current_user = get_jwt_identity()
    if isinstance(current_user, str):
        username = current_user
    else:
        username = current_user['username']

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify(errors="Пользователь не найден."), 404

    inventory = Inventory.query.filter_by(user_id=user.id).all()
    inventory_list = [{"type": item.item_type, "quantity": item.quantity} for item in inventory]

    coin_history = CoinTransaction.query.filter(
        (CoinTransaction.from_user == username) | (CoinTransaction.to_user == username)
    ).all()

    received = [{"fromUser ": tx.from_user, "amount": tx.amount} for tx in coin_history if tx.to_user == username]
    sent = [{"toUser ": tx.to_user, "amount": tx.amount} for tx in coin_history if tx.from_user == username]

    purchases = Purchase.query.filter_by(user_id=user.id).all()
    purchased_items = [{"name": purchase.merch.name, "quantity": purchase.quantity} for purchase in purchases]

    return jsonify(
        coins=user.coins,
        inventory=inventory_list,
        coinHistory={"received": received, "sent": sent},
        purchases=purchased_items
    ), 200

@app.route('/api/sendCoin', methods=['POST'])
@jwt_required()
def sendСoin():
    data = request.get_json()
    to_user = data.get('recipient')
    amount = data.get('amount')

    current_user = get_jwt_identity()

    if isinstance(current_user, str):
        username = current_user
    else:
        username = current_user['username']

    sender = User.query.filter_by(username=username).first()
    recipient = User.query.filter_by(username=to_user).first()
    print("to_user", to_user)
    print('recipient',recipient)
    if not recipient:
        return jsonify(errors="Получатель не найден."), 400

    if sender.coins < amount:
        return jsonify(errors="Недостаточно монет для отправки."), 400
    sender.coins -= amount
    recipient.coins += amount

    transaction = CoinTransaction(from_user=username, to_user=to_user, amount=amount)
    db.session.add(transaction)
    db.session.commit()

    return jsonify(message="Монеты отправлены."), 200

@app.route('/api/buy/<item>', methods=['GET'])
@jwt_required()
def buy(item):
    current_user = get_jwt_identity()
    if isinstance(current_user, str):
        username = current_user
    else:
        username = current_user['username']
    user = User.query.filter_by(username=username).first()
    merch_item = Merch.query.filter_by(name=item).first()
    if not merch_item:
        return jsonify(errors="Предмет не найден."), 400
    if user.coins < merch_item.price:
        return jsonify(errors="Недостаточно монет для покупки."), 400
    user.coins -= merch_item.price
    purchase = Purchase(user_id=user.id, merch_id=merch_item.id, quantity=1)
    db.session.add(purchase)
    inventory_item = Inventory(user_id=user.id, item_type=item, quantity=1)
    db.session.add(inventory_item)
    db.session.commit()
    return jsonify(message=f"Предмет {item} куплен."), 200

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify(errors="Пользователь с таким именем уже существует."), 400
    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify(message="Пользователь успешно зарегистрирован."), 201

with app.app_context():
    db.create_all()
    merch_items = [
        Merch(name='t-shirt', price=80),
        Merch(name='cup', price=20),
        Merch(name='book', price=50),
        Merch(name='pen', price=10),
        Merch(name='powerbank', price=200),
        Merch(name='hoody', price=300),
        Merch(name='umbrella', price=200),
        Merch(name='socks', price=10),
        Merch(name='wallet', price=50),
        Merch(name='pink-hoody', price=500)
    ]
    for item in merch_items:
        existing_item = Merch.query.filter_by(name=item.name).first()
        if not existing_item:
            db.session.add(item)

    db.session.commit()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

