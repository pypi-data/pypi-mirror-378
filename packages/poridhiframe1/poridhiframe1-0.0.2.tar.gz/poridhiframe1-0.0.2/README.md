# PoridhiFrame: Python Web Framework built for learning purposes

![purpose](https://img.shields.io/badge/purpose-learning-green.svg)
![PyPI](https://img.shields.io/pypi/v/poridhiframe1.svg)
![Python Version](https://img.shields.io/badge/python-3.6%2B-blue.svg)

PoridhiFrame is a Python web framework built for learning purposes. It demonstrates modern web framework architecture including middleware, routing, templating, and more.

It's a WSGI framework and can be used with any WSGI application server such as Gunicorn.

## Installation

```shell
pip install poridhiframe
```

## How to use it

### Basic usage:

```python
from poridhiframe.api import API

app = API()

@app.route("/home")
def home(request, response):
    response.text = "Hello from the HOME page"

@app.route("/hello/{name}")
def greeting(request, response, name):
    response.text = f"Hello, {name}"

@app.route("/books")
class BooksResource:
    def get(self, req, resp):
        resp.text = "Books Page"

    def post(self, req, resp):
        resp.text = "Endpoint to create a book"
```

### Response Types

PoridhiFrame supports multiple response types with automatic content-type setting:

```python
@app.route("/json")
def json_handler(req, resp):
    resp.json = {"message": "Hello JSON"}

@app.route("/html")
def html_handler(req, resp):
    resp.html = "<h1>Hello HTML</h1>"

@app.route("/text")
def text_handler(req, resp):
    resp.text = "Hello Text"
```

### HTTP Method Control

Restrict handlers to specific HTTP methods:

```python
@app.route("/api/users", allowed_methods=["GET", "POST"])
def users_api(req, resp):
    if req.method == "GET":
        resp.json = {"users": ["Alice", "Bob"]}
    elif req.method == "POST":
        resp.json = {"message": "User created"}
```

### Templates

The default folder for templates is `templates`. You can change it when initializing the main `API()` class:

```python
app = API(templates_dir="templates_dir_name")
```

Then you can use HTML files in that folder like so in a handler:

```python
@app.route("/show/template")
def handler_with_template(req, resp):
    resp.html = app.template(
        "example.html", 
        context={"title": "Awesome Framework", "body": "welcome to the future!"}
    )
```

### Static Files

Just like templates, the default folder for static files is `static` and you can override it:

```python
app = API(static_dir="static_dir_name")
```

Then you can use the files inside this folder in HTML files:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{{title}}</title>
    <link href="/static/main.css" rel="stylesheet" type="text/css">
</head>
<body>
    <h1>{{body}}</h1>
    <p>This is a paragraph</p>
</body>
</html>
```

### Middleware

You can create custom middleware classes by inheriting from the `poridhiframe.middleware.Middleware` class and overriding its two methods that are called before and after each request:

```python
from poridhiframe.api import API
from poridhiframe.middleware import Middleware

app = API()

class SimpleCustomMiddleware(Middleware):
    def process_request(self, req):
        print("Before dispatch", req.url)

    def process_response(self, req, res):
        print("After dispatch", req.url)

app.add_middleware(SimpleCustomMiddleware)
```

### Unit Tests

The recommended way of writing unit tests is with [pytest](https://docs.pytest.org/en/latest/). There are two built in fixtures that you may want to use when writing unit tests with PoridhiFrame. The first one is `app` which is an instance of the main `API` class:

```python
def test_route_overlap_throws_exception(app):
    @app.route("/")
    def home(req, resp):
        resp.text = "Welcome Home."

    with pytest.raises(AssertionError):
        @app.route("/")
        def home2(req, resp):
            resp.text = "Welcome Home2."
```

The other one is `client` that you can use to send HTTP requests to your handlers. It is based on the famous [requests](https://requests.readthedocs.io/) library:

```python
def test_parameterized_route(app, client):
    @app.route("/{name}")
    def hello(req, resp, name):
        resp.text = f"hey {name}"

    assert client.get("http://testserver/matthew").text == "hey matthew"
```

## Running with WSGI Servers

### Development Server (Python built-in)

```python
# app.py
from poridhiframe.api import API

app = API()

@app.route("/")
def home(req, resp):
    resp.text = "Hello World"

if __name__ == "__main__":
    # Simple development server
    from wsgiref.simple_server import make_server
    server = make_server('localhost', 8000, app)
    print("Server running on http://localhost:8000")
    server.serve_forever()
```

### Production Server (Gunicorn)

```bash
# Install gunicorn
pip install gunicorn

# Run your application
gunicorn app:app
```

## Contributing

This framework was built for educational purposes. Feel free to fork, modify, and experiment with the code to learn more about web framework internals.

## License

MIT License