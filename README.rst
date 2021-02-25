Flask-Liquid
============

A `Flask <https://palletsprojects.com/p/flask/>`_ extension for `Liquid <https://github.com/jg-rp/liquid>`_.
Render Liquid templates in your Flask applications.

- `Installing`_
- `Quick Start`_
- `Factories and Blueprints`_
- `Mixing Jinja and Liquid`_
- `Auto Escape`_
- `Flask Standard Context`_
- `Context Processors`_
- `Signals`_
- `Contributing`_


Installing
----------

Install and update using `pip <https://pip.pypa.io/en/stable/quickstart/>`_:

.. code-block:: text

    $ python -m pip install -U flask-liquid

Requires Python>=3.8.

Quick Start
-----------

Flask-Liquid provides ``render_template`` and ``render_template_string`` functions that behave much
like the `Flask equivalents <https://flask.palletsprojects.com/en/1.1.x/quickstart/#rendering-templates>`_
of the same name. By default Flask-Liquid will look for templates in the ``templates`` folder. The same
location Flask uses for Jinja templates.

.. code-block:: python

    # saved as app.py
    from flask import Flask

    from flask_liquid import Liquid
    from flask_liquid import render_template

    app = Flask(__name__)
    liquid = Liquid(app)

    @app.route("/hello/")
    @app.route("/hello/<name>")
    def index(name=None):
        return render_template("index.html", name=name)


Set the ``LIQUID_TEMPLATE_FOLDER`` configuration value to change the Liquid template folder
independently of ``app.template_folder``.

.. code-block:: python

    app = Flask(__name__)
    app.config.update(
        LIQUID_TEMPLATE_FOLDER="/path/to/liquid/templates/",
    )

    liquid = Liquid(app)


Factories and Blueprints
++++++++++++++++++++++++

When using the factory pattern, use ``liquid.init_app(app)`` instead. Any ``LIQUID_*``
configuration values stored on the app will override ``Liquid`` constructor arguments
when ``init_app`` is called.

.. code-block:: python

    from flask import Flask
    from flask_liquid import Liquid

    from yourapp.blueprints import some_blueprint

    liquid = Liquid()

    def create_app(config=None):
        app = Flask(__name__)
        app.register_blueprint(some_blueprint.bp)

        liquid.init_app(app)

        return app


Mixing Jinja and Liquid
-----------------------

If you want to use Jinja and Liquid templates side by side, import Liquid render functions
using an alias.

.. code-block:: Python

    from flask import render_template
    from flask_liquid import render_template as render_liquid_template


Auto Escape
+++++++++++

Whereas Flask configures Jinja with auto escaping enabled by default, forcing you to explicitly
mark strings of HTML (for example) or template blocks as safe, Liquid does the opposite. Liquid
includes the ``escape`` and ``escape_once`` filters for escaping untrusted strings, but does not
have a ``safe`` filter nor an auto escape feature.

To render markup from a Liquid snippet inside a Jinja template, mark the string returned by
``render_liquid_template`` as safe using ``Markup``, then include it in the Jinja template
context. That is assuming you trust values in the Liquid render context and/or have used
the ``escape`` filter appropriately in your Liquid templates.

.. code-block:: python

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


Flask Standard Context
----------------------

Flask has some `standard context <https://flask.palletsprojects.com/en/1.1.x/templating/#standard-context>`_
variables that are included in each Jinja template context automatically. Flask-Liquid does not
include these variables. If you need access to the Flask session or request, for example, you'll
need to manually map session or request properties to Liquid context keys.

.. code-block:: python

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


Context Processors
------------------

When the ``LIQUID_FLASK_CONTEXT_PROCESSORS`` configuration value is set to ``True``, Flask context
processors will update Liquid template contexts too. Be aware that Python Liquid relies on the
``Mapping`` interface for resolving identifiers, using ``operators.getitem`` internally. So for
values returned from context processors to be useful within Liquid templates, they must behave like
a dictionary.

.. code-block:: python

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


Signals
-------

By default, when `signals are available <https://flask.palletsprojects.com/en/1.1.x/api/#flask.signals.signals_available>`_,
Flask-Liquid will send a ``before_render_template`` and ``template_rendered`` signal for each
successful call to ``render_template`` and ``render_template_string``.

You can disable these signals for Liquid templates by setting the ``LIQUID_FLASK_SIGNALS``
configuration value to ``False``.


Contributing
------------

- Install development dependencies with `Pipenv <https://github.com/pypa/pipenv>`_

- Flask-Liquid fully embraces type hints and static type checking. I like to use the
  `Pylance <https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance>`_
  extension for Visual Studio Code, which includes `Pyright <https://github.com/microsoft/pyright>`_
  for static type checking.

- Format code using `black <https://github.com/psf/black>`_.

- Write tests using ``unittest.TestCase``.

- Run tests with ``make test`` or ``python -m unittest``.

- Check test coverage with ``make coverage`` and open ``htmlcov/index.html`` in your browser.