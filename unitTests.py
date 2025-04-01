import unittest
from flask import json
from launcher import app, db, User, Merch


class FlaskAppTests(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:0000@localhost/Service-Avito'
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
            self.create_test_data()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def create_test_data(self):
        with self.app.app_context():
            user = User.query.filter_by(username='testuser').first()
            if not user:
                user = User(username='testuser', password='testpass')
                db.session.add(user)
                db.session.commit()

            merch_items = [
                Merch(name='t-shirt', price=80),
                Merch(name='cup', price=20)
            ]

            for item in merch_items:
                existing_item = Merch.query.filter_by(name=item.name).first()
                if not existing_item:
                    db.session.add(item)

            db.session.commit()

    def test_register(self):
        response = self.client.post('/api/register', json={'username': 'newuser', 'password': 'newpass'})
        self.assertEqual(response.status_code, 201)
        actual_message = json.loads(response.get_data(as_text=True))['message']
        self.assertIn('Пользователь успешно зарегистрирован.', actual_message)

    def test_auth(self):
        response = self.client.post('/api/auth', json={'username': 'testuser', 'password': 'testpass'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.get_data(as_text=True))

    def test_info(self):
        auth_response = self.client.post('/api/auth', json={'username': 'testuser', 'password': 'testpass'})
        token = json.loads(auth_response.data)['token']
        response = self.client.get('/api/info', headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('coins', response.get_data(as_text=True))

    def test_send_coin(self):
        with self.app.app_context():
            # Authenticate and get token
            auth_response = self.client.post('/api/auth', json={'username': 'testuser', 'password': 'testpass'})
            token = json.loads(auth_response.data)['token']

            # Create a recipient user
            recipient = User(username='recipient', password='recipientpass')
            db.session.add(recipient)
            db.session.commit()

            # Ensure the sender has insufficient coins
            sender = User.query.filter_by(username='testuser').first()
            sender.coins = 5  # Set to a low amount to trigger insufficient coins
            db.session.commit()

            # Attempt to send coins without sufficient balance
            response = self.client.post('/api/sendCoin', json={'recipient': 'recipient', 'amount': 10},
                                        headers={'Authorization': f'Bearer {token}'})
            self.assertEqual(response.status_code, 400)  # Expecting insufficient coins

            # Now add coins to the user
            sender.coins = 100  # Set to a sufficient amount
            db.session.commit()

            # Now send coins
            response = self.client.post('/api/sendCoin', json={'recipient': 'recipient', 'amount': 10},
                                        headers={'Authorization': f'Bearer {token}'})
            self.assertEqual(response.status_code, 200)
            actual_message = json.loads(response.get_data(as_text=True))['message']
            self.assertIn('Монеты отправлены.', actual_message)

    def test_buy(self):
        with self.app.app_context():
            auth_response = self.client.post('/api/auth', json={'username': 'testuser', 'password': 'testpass'})
            token = json.loads(auth_response.data)['token']

            user = User.query.filter_by(username='testuser').first()
            user.coins = 100
            db.session.commit()

            response = self.client.get('/api/buy/t-shirt', headers={'Authorization': f'Bearer {token}'})
            self.assertEqual(response.status_code, 200)
            # Decode the actual response to match the expected message
            actual_message = json.loads(response.get_data(as_text=True))['message']
            print("удачно")
            self.assertIn('Предмет t-shirt куплен.', actual_message)

    def test_buy_insufficient_coins(self):
        with self.app.app_context():
            auth_response = self.client.post('/api/auth', json={'username': 'testuser', 'password': 'testpass'})
            token = json.loads(auth_response.data)['token']

            user = User.query.filter_by(username='testuser').first()
            user.coins = 0
            db.session.commit()

            response = self.client.get('/api/buy/t-shirt', headers={'Authorization': f'Bearer {token}'})
            self.assertEqual(response.status_code, 400)
            actual_message = json.loads(response.get_data(as_text=True))['errors']
            self.assertIn('Недостаточно монет для покупки.', actual_message)


if __name__ == '__main__':
    unittest.main()