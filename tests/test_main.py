# Python imports
import copy
import json

# dependency imports
from flask.ext.testing import TestCase

# project imports
from api import main
from api import manager

# keep an unmodified version of the USERS and GROUPS variables handy, so that
# tests don't affect each other
USERS_ORIG = copy.deepcopy(manager.USERS)
GROUPS_ORIG = copy.deepcopy(manager.GROUPS)

app = main.app


class TestUser(TestCase):

    def create_app(self):

        app.config['TESTING'] = True
        return app

    def setUp(self):
        # reset groups and users between tests
        self.USERS = copy.deepcopy(USERS_ORIG)
        manager.USERS = self.USERS

        self.GROUPS = copy.deepcopy(GROUPS_ORIG)
        manager.GROUPS = self.GROUPS

    def test_HelloWorld(self):
        response = self.client.get('/').json
        expected = dict(response='Hello World!')

        self.assertEqual(response, expected)

    def test_get_user(self):
        response = self.client.get('/users/jsmith').json
        expected = manager.USERS['jsmith']

        self.assertEqual(response, expected)

    def test_get_user_missing(self):
        response = self.client.get('/users/joesmith').json
        expected = {'status': 404, 'message': 'User not found: joesmith'}

        self.assertEqual(response, expected)

    def test_post_user_exists(self):
        data = json.dumps(manager.USERS['jsmith'])
        url = '/users/jsmith'
        ct = 'application/json'

        response = self.client.post(url, data=data, content_type=ct).json
        expected = {'status': 409,
                    'message': 'Conflict: username jsmith already exists'}

        self.assertEqual(response, expected)

    def test_post_user_inconsistent(self):
        data = manager.USERS['jsmith']
        data['userid'] = 'mrsmith'
        data = json.dumps(data)
        url = '/users/glah'
        ct = 'application/json'
        msg = 'Inconsistent userid in URL & payload: glah vs. mrsmith'

        response = self.client.post(url, data=data, content_type=ct).json
        expected = {'status': 400, 'message': msg}

        self.assertEqual(response, expected)

    def test_post_user(self):
        data = json.dumps(dict(first_name='Neiman', last_name='Marcus',
                               userid='nmarcus', groups=['sales', 'admins']))
        url = '/users/nmarcus'
        ct = 'application/json'

        response = self.client.post(url, data=data, content_type=ct).json
        expected = json.loads(data)

        self.assertEqual(response, expected)
        self.assertTrue('nmarcus' in manager.USERS)

    def test_put_user(self):
        data = manager.USERS['jsmith']
        data['first_name'] = 'Joseph'
        data['groups'] = ['musicians']
        data = json.dumps(data)

        url = '/users/jsmith'
        ct = 'application/json'

        response = self.client.put(url, data=data, content_type=ct).json
        expected = json.loads(data)

        self.assertEqual(response, expected)
        self.assertTrue('musicians' in manager.GROUPS)
        self.assertTrue('jsmith' in manager.GROUPS['musicians'])

    def test_put_user_missing(self):
        data = manager.USERS['jsmith']
        data['groups'] = ['robot']
        data['userid'] = 'johnny5'
        data = json.dumps(data)

        url = '/users/johnny5'
        ct = 'application/json'
        msg = 'User johnny5 not found so cannot be updated.'

        response = self.client.put(url, data=data, content_type=ct).json
        expected = {'message': msg, 'status': 404}

        self.assertEqual(response, expected)

    def test_delete_user(self):
        url = '/users/jsmith'

        response = self.client.delete(url).json
        expected = {'status': 200, 'message': 'Deleted user jsmith'}

        self.assertEqual(response, expected)
        self.assertTrue('jsmith' not in manager.USERS)
        self.assertTrue('jsmith' not in manager.GROUPS['admins'])

    def test_delete_user_missing(self):
        url = '/users/johnny5'

        response = self.client.delete(url).json
        expected = {'status': 404, 'message': 'User not found: johnny5'}

        self.assertEqual(response, expected)


class TestGroup(TestCase):

    def create_app(self):

        app.config['TESTING'] = True
        return app

    def setUp(self):
        # reset groups and users between tests
        self.USERS = copy.deepcopy(USERS_ORIG)
        manager.USERS = self.USERS

        self.GROUPS = copy.deepcopy(GROUPS_ORIG)
        manager.GROUPS = self.GROUPS

    def test_get_group(self):
        response = self.client.get('/groups/admins').json
        expected = manager.GROUPS['admins']

        self.assertEqual(response, expected)

    def test_post_group(self):
        data = json.dumps(dict(name='mygroup'))
        ct = 'application/json'

        response = self.client.post('/groups', data=data, content_type=ct).json
        expected = dict(mygroup=[])

        self.assertEqual(response, expected)
        self.assertTrue('mygroup' in manager.GROUPS)

    def test_post_group_duplicate(self):
        data = json.dumps(dict(name='admins'))
        ct = 'application/json'
        msg = 'Conflict: group admins already exists'

        response = self.client.post('/groups', data=data, content_type=ct).json
        expected = {'message': msg, 'status': 409}

        self.assertEqual(response, expected)

    def test_put_group(self):
        data = json.dumps(['jsmith', 'nmarcus', 'mjackson'])
        url = '/groups/admins'
        ct = 'application/json'

        response = set(self.client.put(url, data=data,
                                       content_type=ct).json['admins'])
        expected = set(json.loads(data))

        self.assertEqual(response, expected)
        self.assertTrue('nmarcus' in manager.GROUPS['admins'])

    def test_delete_group(self):
        url = '/groups/admins'

        response = self.client.delete(url).json
        expected = {'status': 200, 'message': 'Deleted group admins'}

        self.assertEqual(response, expected)
        self.assertTrue('admins' not in manager.GROUPS)
