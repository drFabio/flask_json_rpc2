# Lightweight JSON RPC 2.0 extension for flask

## Examples

### Methods

    You can handle all methods on a single end point
```python
    @app.route('/hello', methods=['POST'])
    @rpc_request
    def func(method):
        return 'Hello from '+method
```

    Or you can just listen on a specific method 

```python
    @app.route('/with_method', methods=['POST'])
    @rpc_request(rpc_method='fixed_method')
    def func_with_method():
        return 'Hello from fixed method'
```

Also you are able to handle params from the JSON RPC 2.0 with or without a method

```python
    @app.route('/no_method_and_params', methods=['POST'])
    @rpc_request
    def func_with_params(method, sum_a, sum_b):
        return 'Hello from '+method+' and your sum is %d' % (sum_a+sum_b)

    @app.route('/with_method_and_params', methods=['POST'])
    @rpc_request(rpc_method='another_fixed_method')
    def func_with_method_and_params(diff_a, diff_b):
        return ('Hello from another_fixed_method '
                'and your diff is %d' % (diff_a-diff_b))
```

### Classes
The class bellow will listen on the methods hello, sum and error 
```python
    class MyHandler(RPCHandler):

        def hello(self):
            return 'Hello from hello'

        def sum(self, a, b):
            return a+b

        def error(self):
            raise Exception('SOME ERROR')
```

After the class creation it is needed to be registered on some end point 

```python
    handler = MyHandler()
    handler.register('/class', app)
```