from enum import Enum
from flask import request
from flask import jsonify
from functools import wraps
import sys


def send_response(response):
    """
    Creates a response based on the object
    Args:
        response: A json serializable response
    Returns:
        flask.Response : with status code 200 always
    """
    resp = jsonify(response)
    resp.status_code = 200
    return resp


class ErrorCode(Enum):

    """
    JSON RPC default error Codes
    """
    parse_error = -32700
    invalid_request = -32600
    method_not_found = -32601
    invalid_param = -32602
    internal_error = -32603


def build_error(error_code, message, data=None, rpc_id=None):
    """
    Build a JSON RPC error dict
    Args:
        error_code (int): JSON or app error code
        message (string): Message to display
        data : Json serializable data
        rpc_id (int): The request id 
    Returns:
        dict the json_rpc error response as dict
    """
    resp = {
        'jsonrpc': '2.0',
        'id': rpc_id or 'null',
        'error': {
            'code': error_code,
            'message': message,
            'data': None
        }

    }
    return resp


def build_response(rpc_id, result):
    """
    Build a JSON response
    Args:
        rpc_id (int): The request id 
        result : Json serializable data
    Returns:
        dict the json_rpc success response as dict
    """
    resp = {
        'jsonrpc': '2.0',
        'id': rpc_id,
        'result': result
    }
    return resp


def handle_exception(error, rpc_id):
    """
    Turns an exception into json rpc error 
    Args:
        error (Exception)
        rpc_id (int): The request id 
    """
    error_code = getattr(error, 'error_code', ErrorCode.internal_error.value)
    message = getattr(error, 'message', "Internal error")
    response = build_error(
        error_code, message, None, rpc_id)

    return send_response(response)


class RPCError(BaseException):
    __slots__ = ['error_code', 'message']
    internal_error = ErrorCode.internal_error.value

    def __init__(self, error_code=internal_error, message="Internal error"):
        self.error_code = error_code
        self.message = message
        super().__init__()


class RPCHandler:

    """
    Handles RPC methods
    """

    def _call_method(self, method, *args, **kwargs):
        """
        Class the method on the class,
        raise RPCError otherwise
        Args:
            method (string): the method coming from the request
        """
        method_func = getattr(self, method, None)
        if not callable(method_func):
            raise RPCError()
        return method_func(*args, **kwargs)

    def _handle_route(self):
        return _handle_request(self._call_method)

    def register(self, url, app):
        """
        Register the class to handle RPC requests on the url
        Args:
            url (string): Url to handle
            app (string): Flask app like object (could be Blueprnt)
        """
        app.route(url, methods=['POST'])(self._handle_route)


def _handle_request(func, defined_method=None):
    """
    Handles and validate a request
    Args:
        func (function): Function to call if request ok
        defined_method (string): only accept method if present
    """
    data = request.get_json(force=True, silent=True)
    fields = ['jsonrpc', 'method', 'id']
    not_2 = str(data['jsonrpc']) != '2.0'
    missing_required = not all(
        k in data and data[k] is not None for k in fields)
    if missing_required or not_2:
        error_code = ErrorCode.invalid_request.value
        response = build_error(
            error_code, 'Invalid json rpc request', rpc_id=data.get('id'))
        return send_response(response)

    list_args = []
    dict_args = {}

    if 'params' in data and data['params'] is not None:
        if isinstance(data['params'], dict):
            dict_args = data['params']
        elif isinstance(data['params'],  list):
            list_args = data['params']
        else:
            error_code = ErrorCode.invalid_param.value
            response = build_error(
                error_code, 'Invalid json rpc request', None, data.get('id'))
            return send_response(response)
    sent_method = data['method']

    if defined_method:
        if sent_method != defined_method:
            error_code = ErrorCode.method_not_found.value
            response = build_error(
                error_code, 'Method not found', None, data.get('id'))
            return send_response(response)
    else:
        list_args = [sent_method] + list_args
    try:
        response = func(*list_args, **dict_args)
    except BaseException as e:
        print("HERE")
        print(e)
        return handle_exception(e, data.get('id'))

    return send_response(build_response(data['id'], response))


def rpc_request(*args, **kwargs):
    """
    Decorator for rpc_requests handler
    """
    defined_method = None

    def func_wrapper(func):
        @wraps(func)
        def wrapper():
            return _handle_request(func, defined_method)
        return wrapper

    if len(args) == 1 and callable(args[0]):
        return func_wrapper(args[0])
    else:
        if 'rpc_method' in kwargs:
            defined_method = kwargs['rpc_method']
        return func_wrapper
