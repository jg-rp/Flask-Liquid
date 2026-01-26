<h1 align="center">Flask Liquid</h1>

<p align="center">
A <a href="https://flask.palletsprojects.com/en/stable/">Flask</a> extension for <a href="https://jg-rp.github.io/liquid/">Liquid</a>. Render Liquid templates in your Flask applications.
</p>

<p align="center">
  <a href="https://github.com/jg-rp/flask-liquid/blob/main/LICENSE">
    <img src="https://img.shields.io/pypi/l/flask-liquid.svg?style=flat-square" alt="License">
  </a>
  <a href="https://github.com/jg-rp/liquid/actions/workflows/tests.yaml">
    <img src="https://img.shields.io/github/actions/workflow/status/jg-rp/liquid/tests.yaml?branch=main&label=tests&style=flat-square" alt="Tests">
  </a>
  <br>
  <a href="https://pypi.org/project/flask-liquid/">
    <img src="https://img.shields.io/pypi/v/flask-liquid.svg?style=flat-square" alt="PyPi - Version">
  </a>
  <a href="https://pypi.org/project/flask-liquid/">
    <img src="https://img.shields.io/pypi/pyversions/flask-liquid.svg?style=flat-square" alt="Python versions">
  </a>
</p>

---

## Install

Install Flask Liquid using [pip](https://pip.pypa.io/en/stable/getting-started/) or your favorite package manager:

```console
pip install flask-liquid
```

## Links

- Documentation (this README): https://github.com/jg-rp/Flask-Liquid/blob/main/README.md
- Documentation for Flask Liquid version 1.x: https://jg-rp.github.io/python-liquid-docs-archive/guides/flask-liquid
- Change Log: https://github.com/jg-rp/flask-liquid/blob/main/CHANGES.md
- PyPi: https://pypi.org/project/flask-liquid/
- Source Code: https://github.com/jg-rp/flask-liquid
- Issue Tracker: https://github.com/jg-rp/flask-liquid/issues

## Usage

Flask Liquid provides `render_template` and `render_template_string` functions that behave much like the [Flask equivalents](https://flask.palletsprojects.com/en/stable/quickstart/#rendering-templates) of the same name. By default Flask Liquid will look for templates in [app.template_folder](https://flask.palletsprojects.com/en/stable/api/#flask.Flask.template_folder). The same location Flask uses for Jinja templates.

```python
from flask import Flask

from flask_liquid import Liquid
from flask_liquid import render_template

app = Flask(__name__)
liquid = Liquid(app)

@app.route("/hello/")
@app.route("/hello/<name>")
def index(name=None):
    return render_template("index.html", name=name)
```

Set the `LIQUID_TEMPLATE_FOLDER` configuration value to change the Liquid template folder independently of `app.template_folder`.

```python
app = Flask(__name__)
app.config.update(
    LIQUID_TEMPLATE_FOLDER="/path/to/liquid/templates/",
)

liquid = Liquid(app)
```

## Factories and Blueprints

When using the factory pattern, use `Liquid.init_app(app)` instead. Any `LIQUID_*` configuration values stored on the app will override `Liquid` constructor arguments when `init_app` is called.

```python
from flask import Flask
from flask_liquid import Liquid

from yourapp.blueprints import some_blueprint

liquid = Liquid()

def create_app(config=None):
    app = Flask(__name__)
    app.register_blueprint(some_blueprint.bp)

    liquid.init_app(app)

    return app
```

## Mixing Jinja and Liquid

If you want to use Jinja and Liquid templates side by side, import Liquid render functions using an alias.

```python
from flask import render_template
from flask_liquid import render_template as render_liquid_template
```

## Auto Escape

Unlike a standard [`liquid.Environment()`](https://jg-rp.github.io/liquid/environment/), Flask Liquid enables HTML auto-escaping by default. You can disable auto-escaping by passing `autoescape=False` to `flask_liquid.Liquid()` or setting the `LIQUID_AUTOESCAPE` configuration value to `False`.

To render markup from a Liquid snippet inside a Jinja template (or vice versa), mark the string returned by `render_liquid_template` as safe using `Markup`, then include it in the Jinja template context. That is assuming you trust values in the Liquid render context or have HTML escaped them already.

```python
from flask import Flask
from flask import Markup
from flask import render_template

from flask_liquid import Liquid
from flask_liquid import render_template as render_liquid_template

app = Flask(__name__)
liquid = Liquid(app)

@app.route("/hello")
def hello():
    user_content = render_liquid_template("content.liquid")
    return render_template("page.html", content=Markup(user_content))
```

## Flask Standard Context

Flask has some [standard context variables](https://flask.palletsprojects.com/en/stable/templating/#standard-context) that are included in each Jinja template context automatically. Flask Liquid does not include these variables. If you need access to the Flask session or request, for example, you'll need to manually map session or request properties to Liquid context keys.

```python
from flask import Flask
from flask import request

from flask_liquid import Liquid
from flask_liquid import render_template

app = Flask(__name__)
liquid = Liquid(app)

@app.route("/hello/")
@app.route("/hello/<name>")
def index(name=None):
    return render_template("index.html", name=name, path=request.path)
```

## Context Processors

When the `LIQUID_FLASK_CONTEXT_PROCESSORS` configuration value is set to `True`, Flask context processors will update Liquid template contexts too.

> [!NOTE]
> Remember that Python Liquid uses the [Sequence](https://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence) and [Mapping](https://docs.python.org/3/library/collections.abc.html#collections.abc.Mapping) interfaces for resolving object properties. See [Variables, types and drops](https://jg-rp.github.io/liquid/variables_and_drops/).

```python
from flask import Flask
from flask import request

from flask_liquid import Liquid
from flask_liquid import render_template

app = Flask(__name__)
app.config.update(
    LIQUID_FLASK_CONTEXT_PROCESSORS=True,
)

liquid = Liquid(app)

@app.context_processor
def extra_context():
    return {"request_path": request.path}

@app.route("/hello/")
@app.route("/hello/<name>")
def index(name=None):
    return render_template("index.html", name=name)
```

## Async Support

Render templates asynchronously using `flask_liquid.render_template_async()` and `flask_liquid.render_template_string_async()`.

```python title="app.py"
from flask import Flask

from flask_liquid import Liquid
from flask_liquid import render_template_async

app = Flask(__name__)
liquid = Liquid(app)

@app.route("/render/<name>")
async def render_by_name(name=None):
    return await render_template_async(name)
```

## Configuration Values

The following [configuration values](https://flask.palletsprojects.com/en/stable/config/) can be used instead of passing arguments to `flask_liquid.Liquid()`.

| Configuration Value             | Liquid Argument          | Default                                 |
| ------------------------------- | ------------------------ | --------------------------------------- |
| LIQUID_TAG_START_STRING         | tag_start_string         | `"{%"`                                  |
| LIQUID_TAG_END_STRING           | tag_end_string           | `"%}"`                                  |
| LIQUID_STATEMENT_START_STRING   | statement_start_string   | `"{{"`                                  |
| LIQUID_STATEMENT_END_STRING     | statement_end_string     | `"}}"`                                  |
| LIQUID_TEMPLATE_COMMENTS        | template_comments        | `False`                                 |
| LIQUID_COMMENT_START_STRING     | statement_start_string   | `"{#"`                                  |
| LIQUID_COMMENT_END_STRING       | statement_end_string     | `"#}"`                                  |
| LIQUID_TOLERANCE                | tolerance                | `liquid.Mode.STRICT`                    |
| LIQUID_UNDEFINED                | undefined                | `liquid.Undefined`                      |
| LIQUID_STRICT_FILTERS           | strict_filters           | `True`                                  |
| LIQUID_TEMPLATE_FOLDER          |                          | `app.template_folder`                   |
|                                 | loader                   | `FileSystemLoader(app.template_folder)` |
| LIQUID_AUTOESCAPE               | autoescape               | `True`                                  |
| LIQUID_FLASK_CONTEXT_PROCESSORS | flask_context_processors | `False`                                 |
| LIQUID_FLASK_SIGNALS            | flask_signals            | `True`                                  |

Note that if you specify a [loader](https://jg-rp.github.io/liquid/loading_templates/) with the `loader` argument to `flask_liquid.Liquid()`, Flask Liquid will use that instead of creating a [`FileSystemLoader`](https://jg-rp.github.io/liquid/loading_templates/#file-system-loader) pointing to `LIQUID_TEMPLATE_FOLDER`.
