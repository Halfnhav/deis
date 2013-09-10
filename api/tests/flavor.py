"""
Unit tests for the Deis api app.

Run the tests with "./manage.py test api"
"""

from __future__ import unicode_literals

import json

from django.test import TestCase
import yaml


class FlavorTest(TestCase):

    """Tests creation of different node flavors"""

    fixtures = ['tests.json']

    def setUp(self):
        self.assertTrue(
            self.client.login(username='autotest', password='password'))
        url = '/api/providers'
        creds = {'secret_key': 'x'*64, 'access_key': 1*20}
        body = {'id': 'autotest', 'type': 'mock', 'creds': json.dumps(creds)}
        response = self.client.post(url, json.dumps(body), content_type='application/json')
        self.assertEqual(response.status_code, 201)

    def test_flavor(self):
        """
        Test that a user can create, read, update and delete a node flavor
        """
        url = '/api/flavors'
        body = {'id': 'autotest', 'provider': 'autotest',
                'params': json.dumps({'region': 'us-west-2', 'instance_size': 'm1.medium'})}
        response = self.client.post(url, json.dumps(body), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        flavor_id = response.data['id']
        response = self.client.get('/api/flavors')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        url = "/api/flavors/{flavor_id}".format(**locals())
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        new_init = {'ssh_authorized_keys': ['ssh-rsa aaaaaaaaa']}
        body = {'init': yaml.safe_dump(new_init)}
        response = self.client.patch(url, json.dumps(body), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(yaml.safe_load(response.data['init']), new_init)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)

    def test_flavor_contents(self):
        """Tests that flavors explicitly contain AMI ID, instance size, region, and zone."""
        url = '/api/flavors'
        body = {'id': 'autotest', 'provider': 'autotest', 'params': json.dumps({})}
        response = self.client.post(url, json.dumps(body), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        flavor_id = response.data['id']
        response = self.client.get('/api/flavors')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        url = "/api/flavors/{flavor_id}".format(**locals())
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        params = json.loads(response.data['params'])
        self.assertEqual(params['region'], 'us-east-1')
        self.assertEqual(params['zone'], 'any')
        self.assertEqual(params['size'], 'm1.medium')
        self.assertTrue(params['image'])

    def test_flavor_update(self):
        """Tests that flavors can be updated by the client."""
        url = '/api/flavors'
        params = {
            'region': 'us-west-2',
            'size': 't1.micro',
        }
        body = {'id': 'autotest', 'provider': 'autotest', 'params': json.dumps(params)}
        response = self.client.post(url, json.dumps(body), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        flavor_id = response.data['id']
        response = self.client.get('/api/flavors')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        url = "/api/flavors/{flavor_id}".format(**locals())
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        params = json.loads(response.data['params'])
        self.assertEqual(params['region'], 'us-west-2')
        self.assertEqual(params['zone'], 'any')
        self.assertEqual(params['size'], 't1.micro')
        self.assertTrue(params['image'])
        params = {
            'size': 'c1.xlarge',
            'image': 'ami-c98d1bf9',
        }
        body = {'id': flavor_id, 'params': json.dumps(params)}
        response = self.client.patch(url, json.dumps(body), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        flavor_id = response.data['id']
        response = self.client.get('/api/flavors')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        url = "/api/flavors/{flavor_id}".format(**locals())
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        params = json.loads(response.data['params'])
        self.assertEqual(params['region'], 'us-west-2')
        self.assertEqual(params['zone'], 'any')
        self.assertEqual(params['size'], 'c1.xlarge')
        self.assertEqual(params['image'], 'ami-c98d1bf9')
