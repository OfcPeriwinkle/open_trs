import unittest
import sqlite3

import open_trs.configs
from open_trs.server import app


class TestServer(unittest.TestCase):
    def setUp(self):
        self.connection = sqlite3.connect(':memory:')
        self.cursor = self.connection.cursor()

        app.config.from_object(open_trs.configs.TestingConfig)
        app.config['DB_CONNECTION'] = self.connection

        self.client = app.test_client()

    def tearDown(self):
        self.connection.close()

    def test_hello_world(self):
        response = self.client.get('/')
        self.assertEqual(response.data, b'Hello, World!')

    def test_add_user(self):
        new_user = {
            'name': 'test',
            'email': 'foo@bar.com',
            'password': 'password'
        }

        response = self.client.post('/users', json=new_user)
        self.assertEqual(response.status_code, 201)

        self.cursor.execute('SELECT * FROM Users')
        users = self.cursor.fetchall()

        self.assertEqual(users, [new_user])


if __name__ == '__main__':
    unittest.main()
