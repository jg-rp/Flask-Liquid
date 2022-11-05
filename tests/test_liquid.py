# type: ignore
"""Flask-Liquid test cases."""

import os
import tempfile

from contextlib import contextmanager
from unittest import TestCase
from unittest import skipIf

import flask
from flask import Flask
from flask import Blueprint
from flask import template_rendered
from flask import before_render_template

from liquid import Undefined
from liquid import StrictUndefined

from liquid.exceptions import UndefinedError
from liquid.exceptions import NoSuchFilterFunc

from liquid.loaders import DictLoader

from flask_liquid import Liquid
from flask_liquid import render_template
from flask_liquid import render_template_string
from flask_liquid import render_template_async
from flask_liquid import render_template_string_async


SKIP_ASYNC = bool(int(flask.__version__[0]) < 2)


# pylint: disable=redefined-builtin unused-variable
def create_app(config, globals=None, loader=None):
    """Test Flask application factory."""
    app = Flask(__name__)
    app.testing = True
    app.config.from_mapping(config)

    _ = Liquid(app, globals=globals, loader=loader)

    @app.context_processor
    def add_some_context():
        return {"username": "some"}

    @app.route("/fromstring")
    def from_string():
        return render_template_string(r"Hello {{ you }}", you="World")

    @app.route("/rendertemplate")
    def from_template_file():
        return render_template("index.html", you="World")

    @app.route("/render/<name>")
    def render_by_name(name):
        return render_template(name)

    @app.route("/globalcontext")
    def global_context():
        return render_template_string(r"Hello {{ you }}")

    @app.route("/standardcontext")
    def standard_context():
        return render_template_string(r"{{ g }}{{ username }}{{ request.path }}")

    @app.route("/contextprocessor")
    def with_context_from_processor():
        return render_template_string(r"{{ username }}")

    # pylint: disable=invalid-name
    bp = Blueprint("blue", __name__, url_prefix="/blue")

    @bp.route("/greeting")
    def blueprint_hello():
        return render_template_string(r"{{ greeting }}, {{ you }}.")

    @bp.context_processor
    def blueprint_context():
        return {"greeting": "Goodbye"}

    app.register_blueprint(bp)
    return app


# pylint: disable=redefined-builtin unused-variable
def create_async_app(config, globals=None, loader=None):
    """Test Flask application factory."""
    app = Flask(__name__)
    app.testing = True
    app.config.from_mapping(config)

    _ = Liquid(app, globals=globals, loader=loader)

    @app.context_processor
    def add_some_context():
        return {"username": "some"}

    @app.route("/fromstring")
    async def from_string():
        return await render_template_string_async(r"Hello {{ you }}", you="World")

    @app.route("/rendertemplate")
    async def from_template_file():
        return await render_template_async("index.html", you="World")

    @app.route("/render/<name>")
    async def render_by_name(name):
        return await render_template_async(name)

    @app.route("/globalcontext")
    async def global_context():
        return await render_template_string_async(r"Hello {{ you }}")

    @app.route("/standardcontext")
    async def standard_context():
        return await render_template_string_async(
            r"{{ g }}{{ username }}{{ request.path }}"
        )

    @app.route("/contextprocessor")
    async def with_context_from_processor():
        return await render_template_string_async(r"{{ username }}")

    return app


@contextmanager
def capture_template_rendered(app):
    """Utility context manager for capturing signals."""
    recorded = []

    # pylint: disable=unused-argument
    def record(_, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


@contextmanager
def capture_before_render_templates(app):
    """Utility context manager for capturing signals."""
    recorded = []

    # pylint: disable=unused-argument
    def record(_, template, context, **extra):
        recorded.append((template, context))

    before_render_template.connect(record, app)
    try:
        yield recorded
    finally:
        before_render_template.disconnect(record, app)


class DefaultLiquidTestCase(TestCase):
    """Flask-Liquid test case with default configuration."""

    def setUp(self):
        self.app = create_app(
            config={"LIQUID_TEMPLATE_FOLDER": "tests/templates/"},
            globals={"you": "World"},
        )

    def test_render_from_string(self):
        """Test that we can render a liquid template given as a string."""
        with self.app.test_client() as client:
            resp = client.get("/fromstring")
            self.assertEqual(resp.data, b"Hello World")

    def test_render_template(self):
        """Test that we can render a liquid template from the file system."""
        with self.app.test_client() as client:
            resp = client.get("/rendertemplate")
            self.assertEqual(resp.data, b"Hello World")

    def test_render_template_by_name(self):
        """Test that we can render a liquid template from the file system."""
        with self.app.test_client() as client:
            resp = client.get("/render/snippet.html")
            self.assertEqual(resp.data, b"Goodbye, World!\n")

    def test_render_with_global_context(self):
        """Test that we can render liquid templates with global context."""
        with self.app.test_client() as client:
            resp = client.get("/globalcontext")
            self.assertEqual(resp.data, b"Hello World")

    def test_standard_flask_context(self):
        """Test that the standard Flask context variables are not included."""
        with self.app.test_client() as client:
            resp = client.get("/standardcontext")
            self.assertEqual(resp.data, b"")

    def test_template_rendered_signal(self):
        """Test that the template_rendered signal is fired when a liquid
        template is rendered."""
        with capture_template_rendered(self.app) as templates:
            resp = self.app.test_client().get("/rendertemplate")
            self.assertEqual(resp.data, b"Hello World")

            template, _ = templates[0]
            self.assertEqual("index.html", template.name)

    def test_before_render_template_signal(self):
        """Test that the before_rendered_tempplate signal is fired before a
        liquid template is rendered."""
        with capture_before_render_templates(self.app) as templates:
            resp = self.app.test_client().get("/rendertemplate")
            self.assertEqual(resp.data, b"Hello World")

            template, _ = templates[0]
            self.assertEqual("index.html", template.name)


@skipIf(SKIP_ASYNC, "async views require flask>=2")
class AsyncLiquidTestCase(DefaultLiquidTestCase):
    """Async Flask-Liquid test case."""

    def setUp(self):
        self.app = create_async_app(
            config={"LIQUID_TEMPLATE_FOLDER": "tests/templates/"},
            globals={"you": "World"},
        )


class LiquidLoaderTestCase(TestCase):
    """Flask-Liquid test cases using arbitrary template loaders."""

    def test_render_template(self):
        """Test that we can render a template from a location of our choosing."""
        with tempfile.TemporaryDirectory() as tmpdirname:
            with open(
                os.path.join(tmpdirname, "index.html"), "w", encoding="utf-8"
            ) as fd:
                fd.write(r"Hello {{ you }}")

            app = create_app(
                config={"LIQUID_TEMPLATE_FOLDER": tmpdirname},
                globals={"you": "World"},
            )

            resp = app.test_client().get("/rendertemplate")
            self.assertEqual(resp.data, b"Hello World")

    def test_dict_loader(self):
        """Test that we can render a template from a dictionary loader."""
        snippets = {
            "index": "<HTML>{% include 'heading' %}</HTML>",
            "heading": "<h1>{{ some }}</h1>",
        }

        expected = b"<HTML><h1>other</h1></HTML>"

        app = create_app(
            config={},
            globals={"some": "other"},
            loader=DictLoader(snippets),
        )

        with app.test_client() as client:
            resp = client.get("/render/index")
            self.assertEqual(resp.data, expected)


class FlaskContextTestCase(TestCase):
    """Flask-Liquid test case using Flask context processors."""

    def setUp(self):
        self.app = create_app(
            config={"LIQUID_FLASK_CONTEXT_PROCESSORS": True},
            globals={"you": "World"},
        )

        self.async_app = create_async_app(
            config={"LIQUID_FLASK_CONTEXT_PROCESSORS": True},
            globals={"you": "World"},
        )

    def test_context_processor(self):
        """Test that we can use context variables from context processors in liquid
        templates."""
        with self.app.test_client() as client:
            resp = client.get("/contextprocessor")
            self.assertEqual(resp.data, b"some")

    @skipIf(SKIP_ASYNC, "async views require flask>=2")
    def test_context_processor_async(self):
        """Test that we can use context variables from context processors in liquid
        templates."""
        with self.async_app.test_client() as client:
            resp = client.get("/contextprocessor")
            self.assertEqual(resp.data, b"some")

    def test_blueprint_context_processor(self):
        """Test that we can use context variables from context processors registered on
        blueprints."""
        with self.app.test_client() as client:
            resp = client.get("/blue/greeting")
            self.assertEqual(resp.data, b"Goodbye, World.")


class NoSignalsTestCase(TestCase):
    """Flask-Liquid test case using Flask signals."""

    def setUp(self):
        self.app = create_app(
            config={
                "LIQUID_FLASK_SIGNALS": False,
                "LIQUID_TEMPLATE_FOLDER": "tests/templates/",
            },
            globals={"you": "World"},
        )

    def test_template_rendered_signal(self):
        """Test that the template_rendered signal is not fired when send_flask_signals
        is False."""
        with capture_template_rendered(self.app) as templates:
            resp = self.app.test_client().get("/rendertemplate")
            self.assertEqual(resp.data, b"Hello World")
            self.assertEqual(len(templates), 0)

    def test_before_render_template_signal(self):
        """Test that the before_rendered_tempplate signal is not fired when
        send_flask_signals is False"""
        with capture_before_render_templates(self.app) as templates:
            resp = self.app.test_client().get("/rendertemplate")
            self.assertEqual(resp.data, b"Hello World")
            self.assertEqual(len(templates), 0)


class LiquidEnvironmentTestCase(TestCase):
    """Liquid environment configuration test case."""

    def test_undefined(self):
        """Test that we can reference undefined variables without error."""
        app = create_app(
            config={"LIQUID_UNDEFINED": Undefined},
        )

        with app.app_context():
            result = render_template_string(r"Hello, {{ nosuchthing }}.")
            self.assertEqual(result, "Hello, .")

    def test_strict_undefined(self):
        """Test that we can set the `undefined` type."""
        app = create_app(
            config={"LIQUID_UNDEFINED": StrictUndefined},
        )

        with app.app_context():
            with self.assertRaises(UndefinedError):
                _ = render_template_string(r"Hello, {{ nosuchthing }}.")

    def test_lax_filters(self):
        """Test that undefined filters can be ignored."""
        app = create_app(
            config={"LIQUID_STRICT_FILTERS": False},
            globals={"username": "You"},
        )

        with app.app_context():
            result = render_template_string(r"Hello, {{ username | upper }}.")
            self.assertEqual(result, "Hello, You.")

    def test_strict_filters(self):
        """Test that undefined filters can raise an exception."""
        app = create_app(
            config={"LIQUID_STRICT_FILTERS": True},
            globals={"username": "You"},
        )

        with app.app_context():
            with self.assertRaises(NoSuchFilterFunc):
                _ = render_template_string(r"Hello, {{ username | upper }}.")

    def test_autoescape(self):
        """Test that autoescape is enabled by default."""
        app = create_app(
            config={},
            globals={"username": "You"},
        )

        with app.app_context():
            result = render_template_string(
                r"Hello, {{ foo }}.",
                foo="<b>you</b>",
            )
            self.assertEqual(result, "Hello, &lt;b&gt;you&lt;/b&gt;.")

    def test_disable_autoescape(self):
        """Test that we can disable autoescape."""
        app = create_app(
            config={"LIQUID_AUTOESCAPE": False},
            globals={"username": "You"},
        )

        with app.app_context():
            result = render_template_string(
                r"Hello, {{ foo }}.",
                foo="<b>you</b>",
            )
            self.assertEqual(result, "Hello, <b>you</b>.")

    def test_enable_template_comments(self):
        """Test that we can enable template comments."""
        app = create_app(
            config={"LIQUID_TEMPLATE_COMMENTS": True},
            globals={"username": "You"},
        )

        with app.app_context():
            result = render_template_string(r"Hello, {# some comment -#} World!")
            self.assertEqual(result, "Hello, World!")

    def test_expression_cache(self):
        """Test that we can enable expresssion caching."""
        app = create_app(
            config={"LIQUID_EXPRESSION_CACHE_SIZE": 1},
            globals={"username": "You"},
        )
        ext: Liquid = app.extensions["flask_liquid"]
        self.assertTrue(hasattr(ext.env.parse_filtered_expression_value, "cache_info"))
