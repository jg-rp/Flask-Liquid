"""Flask-Liquid test cases."""

import os
import tempfile

from contextlib import contextmanager
from unittest import TestCase

from flask import Flask
from flask import template_rendered
from flask import before_render_template

from liquid.loaders import DictLoader

from flask_liquid import Liquid
from flask_liquid import render_template
from flask_liquid import render_template_string


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
        return render_template_string("Hello {{ you }}", you="World")

    @app.route("/rendertemplate")
    def from_template_file():
        return render_template("index.html", you="World")

    @app.route("/render/<name>")
    def render_by_name(name):
        return render_template(name)

    @app.route("/globalcontext")
    def global_context():
        return render_template_string("Hello {{ you }}")

    @app.route("/standardcontext")
    def standard_context():
        return render_template_string("{{ g }}{{ username }}{{ request.path }}")

    @app.route("/contextprocessor")
    def with_context_from_processor():
        return render_template_string("{{ username }}")

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


class LiquidLoaderTestCase(TestCase):
    """Flask-Liquid test cases using arbitrary template loaders."""

    def test_render_template(self):
        """Test that we can render a template from a location of our choosing."""
        with tempfile.TemporaryDirectory() as tmpdirname:
            with open(os.path.join(tmpdirname, "index.html"), "w") as fd:
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
        self.app = create_app(config={"LIQUID_FLASK_CONTEXT_PROCESSORS": True})

    def test_context_processor(self):
        """Test that we can use context variables from context processors in liquid
        templates."""
        with self.app.test_client() as client:
            resp = client.get("/contextprocessor")
            self.assertEqual(resp.data, b"some")


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
