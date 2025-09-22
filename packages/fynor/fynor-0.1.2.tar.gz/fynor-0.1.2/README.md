# Fynor

![purpose](https://img.shields.io/badge/purpose-learning-green.svg)

Fynor is a Python Web Framework built for learning purposes. The plan is to learn how frameworks are built by
implementing their features,
writing blog posts about them and keeping the codebase as simple as possible.

It is a WSGI framework and can be used with any WSGI application server such as Gunicorn.

## Inspiration

I was inspired to make a web framework after reading [Jakhongir Rakhmonov](https://t.me/jakhonrakhmonov)'
s [blog post](https://t.me/jakhonrakhmonov/419)
about how he built a web framework and became an open source maintainer. He wrote about how thrilling the experience has
been for him so I decided I would give it a try as well.
Thank you much, [Jakhongir](https://github.com/rahmonov). Go check
out [Alcazar by Jakhongir Rakhmonov](https://github.com/rahmonov/alcazar).
If you like him, show some love by staring his repos.

## Quick Start

Install it:

```bash
pip install fynor
```

Basic Usage:

```python
# app.py
from fynor import Fynor

app = Fynor()


@app.route("/")
def home(req, resp):
    resp.text = "Hello, this is a home page."


@app.route("/about")
def about_page(req, resp):
    resp.text = "Hello, this is an about page."


@app.route("/{age:d}")
def tell_age(req, resp, age):
    resp.text = f"Your age is {age}"


@app.route("/{name:l}")
class GreetingHandler:
    def get(self, req, resp, name):
        resp.text = f"Hello, {name}"


@app.route("/show/template")
def handler_with_template(req, resp):
    resp.html = app.template("example.html", context={"title": "Awesome Framework", "body": "welcome to the future!"})


@app.route("/json")
def json_handler(req, resp):
    resp.json = {"this": "is JSON"}


@app.route("/custom")
def custom_response(req, resp):
    resp.body = b'any other body'
    resp.content_type = "text/plain"
```

Start:

```bash
gunicorn app:app
```

## Handlers

If you use class based handlers, only the methods that you implement will be allowed:

```python
@app.route("/{name:l}")
class GreetingHandler:
    def get(self, req, resp, name):
        resp.text = f"Hello, {name}"
```

This handler will only allow `GET` requests. That is, `POST` and others will be rejected. The same thing can be done
with
function based handlers in the following way:

```python
@app.route("/", allowed_methods=["get"])
def home(req, resp):
    resp.text = "Hello, this is a home page."
```

Note that if you specify `methods` for class based handlers, they will be ignored.

## Templates

[//]: # (The default folder for templates is `templates`. You can change it when initializing the main `Fynor&#40;&#41;` class:)

[//]: # ()

[//]: # (```python)

[//]: # (app = Fynor&#40;templates_dir="templates_dir_name"&#41;)

[//]: # (```)

[//]: # ()

[//]: # (Then you can use HTML files in that folder like so in a handler:)

```python
@app.route("/show/template")
def handler_with_template(req, resp):
    resp.html = app.template("example.html", context={"title": "Awesome Framework", "body": "welcome to the future!"})
```

## Static Files

[//]: # (Just like templates, the default folder for static files is `static` and you can override it:)

[//]: # ()

[//]: # (```python)

[//]: # (app = Fynor&#40;static_dir="static_dir_name"&#41;)

[//]: # (```)

[//]: # ()

[//]: # (Then you can use the files inside this folder in HTML files:)

```html
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <title>{{title}}</title>

    <link href="static/main.css" rel="stylesheet" type="text/css">
</head>

<body>
<h1>{{body}}</h1>
<p>This is a paragraph</p>
</body>
</html>
```

## Custom Exception Handler

Sometimes, depending on the exception raised, you may want to do a certain action. For such cases, you can register an
exception handler:

```python
def on_exception(req, resp, exception):
    if isinstance(exception, HTTPError):
        if exception.status == 404:
            resp.text = "Unfortunately the thing you were looking for was not found"
        else:
            resp.text = str(exception)
    else:
        # unexpected exceptions
        if app.debug:
            debug_exception_handler(req, resp, exception)
        else:
            print("These unexpected exceptions should be logged.")

app = Fynor(debug=False)
app.add_exception_handler(on_exception)
```

This exception handler will catch 404 HTTPErrors and change the text
to `"Unfortunately the thing you were looking for was not found"`. For other HTTPErrors, it will simply
show the exception message. If the raised exception is not an HTTPError and if `debug` is set to True, it will show the
exception and its traceback. Otherwise, it will log it.

## Middleware

You can create custom middleware classes by inheriting from the `fynor.middleware.Middleware` class and override its
two methods
that are called before and after each request:

```python
from fynor import Fynor
from fynor.middleware import Middleware

app = Fynor()


class SimpleCustomMiddleware(Middleware):
    def process_request(self, req):
        print("Before dispatch", req.url)

    def process_response(self, req, res):
        print("After dispatch", req.url)


app.add_middleware(SimpleCustomMiddleware)
```

## Features

- WSGI compatible
- Parameterized and basic routing
- Class based handlers
- Test Client
- Support for templates
- Support for static files
- Custom exception handler
- Middleware

## Note

It is extremely raw and will hopefully keep improving. If you are interested in knowing how a particular feature is
implemented in other
frameworks, please open an issue and we will hopefully implement and explain it.