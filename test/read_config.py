import unittest
import context
import src.read_config as read_config

config = {
    'keyword_subscribers': {
        'guild_id_1': {
            'user_id_1': ['keyword_1', 'keyword_2'],
            'user_id_2': ['keyword_3', 'keyword_4'],
        }
    },
    'subscribers': {
        'guild_id_1': ['user_id_3', 'user_id_4']
    },
}

products = ['product with keyword_1 in it', 'product with keyword_3 in it']

expected_user_keywords = ['keyword_1', 'keyword_2']
expected_subs_to_notify = ['user_id_3', 'user_id_4']
expected_subs_to_notify_keyword = {'user_id_1'}
expected_subs_to_notify_products = {'user_id_1', 'user_id_2'}
expected_all_keywords = {'keyword_1', 'keyword_2', 'keyword_3', 'keyword_4'}

class TestReadConfig(unittest.TestCase):

    def setUp(self):
        self.read_config = read_config.ReadConfig(config)

    def test_get_keyword_for_user(self):
        user_keywords = self.read_config.get_keywords_for_user('user_id_1', 'guild_id_1')
        self.assertEqual(user_keywords, expected_user_keywords)

    def test_get_user_ids_to_notify(self):
        user_ids = self.read_config.get_user_ids_to_notify('guild_id_1')
        self.assertEqual(user_ids, expected_subs_to_notify)

    def test_get_user_ids_to_notify_keyword(self):
        user_ids = self.read_config.get_user_ids_to_notify_keyword('guild_id_1', 'product with keyword_1 in it')
        self.assertEqual(user_ids, expected_subs_to_notify_keyword)

    def test_get_users_to_notify_for_products(self):
        users = self.read_config.get_users_to_notify_for_products('guild_id_1', products)
        self.assertEqual(users, expected_subs_to_notify_products)

    def test_get_users_to_notify_for_products_when_guild_not_exist(self):
        users = self.read_config.get_users_to_notify_for_products('guild_id_5', products)
        self.assertEqual(users, set())
    
    def test_get_all_keywords(self):
        keywords = self.read_config.get_all_keywords('guild_id_1')
        self.assertEqual(keywords, expected_all_keywords)

if __name__ == '__main__':
    unittest.main()