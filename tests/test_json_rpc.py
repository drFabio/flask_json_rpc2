import unittest
from flask import Flask, json
from flask_json_rpc2.json_rpc import (
    rpc_request,
    ErrorCode,
    RPCHandler,
    RPCError)


class MyHandler(RPCHandler):

    def hello(self):
        return 'Hello from hello'

    def sum(self, a, b):
        return a+b

    def error(self):
        raise Exception('SOME ERROR')


def json_rpc_request(client, url, method, params=None, id=123):
    resp = client.post(
        url,
        data=json.dumps({
            'jsonrpc': '2.0',
            'id': id,
            'method': method,
            'params': params
        }),
        content_type='application/json'
    )
    response = json.loads(resp.get_data())
    return response


class JSONRPC_Test(unittest.TestCase):

    def _create_app(self):
        app = Flask(__name__)
        app.debug = True

        @app.route('/hello', methods=['POST'])
        @rpc_request
        def func(method):
            return 'Hello from '+method

        @app.route('/no_method_and_params', methods=['POST'])
        @rpc_request
        def func_with_params(method, sum_a, sum_b):
            return 'Hello from '+method+' and your sum is %d' % (sum_a+sum_b)

        @app.route('/with_method', methods=['POST'])
        @rpc_request(rpc_method='fixed_method')
        def func_with_method():
            return 'Hello from fixed method'

        @app.route('/with_method_and_params', methods=['POST'])
        @rpc_request(rpc_method='another_fixed_method')
        def func_with_method_and_params(diff_a, diff_b):
            return ('Hello from another_fixed_method '
                    'and your diff is %d' % (diff_a-diff_b))

        @app.route('/with_exception', methods=['POST'])
        @rpc_request
        def func_with_exception(method):
            raise RPCError(message='SOME ERROR')
        handler = MyHandler()
        handler.register('/class', app)
        return app

    def request(self, url, method, params=None, id=123):
        response = json_rpc_request(self.client, url, method, params, id)
        self.assertEqual('2.0', str(response['jsonrpc']))
        if id is not None:
            self.assertEqual(id, response['id'])
        self.assertTrue(any(k in response for k in ('result', 'error')))
        return response

    def setUp(self):
        app = self._create_app()
        self.client = app.test_client()

    def _test_rpc_error(self, response, expected_code, expected_message=None):
        self.assertIn('error', response)
        error_code = response['error']['code']
        self.assertEqual(error_code, expected_code)
        message = response['error']['message']
        self.assertIsNotNone(message)
        if expected_message:
            self.assertEqual(message, expected_message)

    def test_error_no_id(self):
        response = self.request('/hello', 'hi', id=None)
        self._test_rpc_error(response, ErrorCode.invalid_request.value)

    def test_error_wrong_params(self):
        """
            Params should ALWAYS be a list or dict
        """
        response = self.request('/no_method_and_params', 'sum', 2)
        self._test_rpc_error(response, ErrorCode.invalid_param.value)

    def test_function(self):
        response = self.request('/hello', 'hi')
        self.assertEqual(response['result'], 'Hello from hi')

    def test_function_with_params(self):
        response = self.request('/no_method_and_params', 'sum', [1, 2])
        self.assertEqual(
            response['result'], 'Hello from sum and your sum is 3')

    def test_function_with_pos_params(self):
        response = self.request(
            '/no_method_and_params', 'sum', {'sum_a': 3, 'sum_b': 1})
        self.assertEqual(
            response['result'], 'Hello from sum and your sum is 4')

    def test_function_with_method(self):
        response = self.request('/with_method', 'fixed_method')
        self.assertEqual(response['result'], 'Hello from fixed method')

    def test_function_with_method_and_params(self):
        response = self.request(
            '/with_method_and_params', 'another_fixed_method', [2, 1])
        expected = 'Hello from another_fixed_method and your diff is 1'
        self.assertEqual(response['result'], expected)

    def test_fixed_method_wrong_method(self):
        response = self.request('/with_method', 'non_existant')
        self._test_rpc_error(response, ErrorCode.method_not_found.value)

    def test_class_no_params(self):
        response = self.request('/class', 'hello')
        self.assertEqual(response['result'], 'Hello from hello')

    def test_with_exception(self):
        response = self.request('/with_exception', 'some_method')
        self._test_rpc_error(
            response, ErrorCode.internal_error.value, 'SOME ERROR')
