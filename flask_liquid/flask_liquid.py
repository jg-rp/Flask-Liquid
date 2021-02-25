"""Add Liquid templates to a Flask application."""

from contextlib import contextmanager
from itertools import chain

from typing import Mapping
from typing import Optional

from flask import Flask
from flask import current_app
from flask import signals_available
from flask import template_rendered
from flask import before_render_template
from flask import _request_ctx_stack

from liquid import Environment
from liquid import Mode
from liquid import Template

from liquid.loaders import BaseLoader
from liquid.loaders import FileSystemLoader

# TODO: Markupsafe!
# TODO: README
# TODO: Package


class Liquid:
    """The Liquid template extension for Flask.

    Args:
        tag_start_string: The sequence of characters indicating the start of a
            liquid tag.
        tag_end_string: The sequence of characters indicating the end of a
            liquid tag.
        statement_start_string: The sequence of characters indicating the start
            of an output statement.
        statement_end_string: The sequence of characters indicating the end
            of an output statement.
        tolerance: Indicates how tolerant to be of errors. Must be one of
            `Mode.LAX`, `Mode.WARN` or `Mode.STRICT`.
        loader: A template loader. Defaults to a FileSystem loader with a search path
            at the same location as `app.template_folder`.
        globals: A mapping that will be added to the context of any template
            loaded from this environment.
        flask_context_processors: If set to `True` Flask context processors
            will be applied to Liquid every render context. Defaults to `False`.
        flask_signals: If set to `True` the `template_rendered` and
            `before_template_rendered` signals will be emitted for Liquid templates.
    """

    # pylint: disable=redefined-builtin too-many-arguments
    def __init__(
        self,
        app: Optional[Flask] = None,
        tag_start_string: str = r"{%",
        tag_end_string: str = r"%}",
        statement_start_string: str = r"{{",
        statement_end_string: str = r"}}",
        tolerance: Mode = Mode.STRICT,
        loader: Optional[BaseLoader] = None,
        globals: Optional[Mapping[str, object]] = None,
        flask_context_processors: bool = False,
        flask_signals: bool = True,
    ):
        self.app = app

        self.env = Environment(
            tag_start_string=tag_start_string,
            tag_end_string=tag_end_string,
            statement_start_string=statement_start_string,
            statement_end_string=statement_end_string,
            tolerance=tolerance,
            loader=loader,
            globals=globals,
        )

        # init_app will default to a file system loader if one was not provided.
        # This differs from the default behavior of `liquid.Environment`, where the
        # default loader is an empty DictLoader.
        self._loader = loader

        # Indicates if Flask context processors should be used to update the liquid
        # context on each request.
        self.flask_context_processors = flask_context_processors

        # Indicates if the extension should trigger Flask's `template_rendered` and
        # `before_template_rendered` signals.
        self.flask_signals = flask_signals

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        """Initialise a Flask app with a Liquid environment."""
        app.config.setdefault("LIQUID_TAG_START_STRING", self.env.tag_start_string)
        app.config.setdefault("LIQUID_TAG_END_STRING", self.env.tag_end_string)
        app.config.setdefault(
            "LIQUID_STATEMENT_START_STRING", self.env.statement_start_string
        )
        app.config.setdefault(
            "LIQUID_STATEMENT_END_STRING", self.env.statement_end_string
        )
        app.config.setdefault("LIQUID_TOLERANCE", self.env.mode)
        app.config.setdefault("LIQUID_TEMPLATE_FOLDER", app.template_folder)

        app.config.setdefault(
            "LIQUID_FLASK_CONTEXT_PROCESSORS", self.flask_context_processors
        )
        app.config.setdefault("LIQUID_FLASK_SIGNALS", self.flask_signals)

        self.flask_signals = app.config["LIQUID_FLASK_SIGNALS"]

        if not self._loader:
            self._loader = FileSystemLoader(
                search_path=app.config["LIQUID_TEMPLATE_FOLDER"]
            )

        self.flask_context_processors = app.config["LIQUID_FLASK_CONTEXT_PROCESSORS"]

        self.env.tag_start_string = app.config["LIQUID_TAG_START_STRING"]
        self.env.tag_end_string = app.config["LIQUID_TAG_END_STRING"]
        self.env.statement_start_string = app.config["LIQUID_STATEMENT_START_STRING"]
        self.env.statement_end_string = app.config["LIQUID_STATEMENT_END_STRING"]
        self.env.mode = app.config["LIQUID_TOLERANCE"]
        self.env.loader = self._loader

        # Just in case init_app is called late and templates have already been loaded.
        self.env.cache.clear()

        app.extensions["flask_liquid"] = self
        self.app = app

    def _make_context(self, context: Mapping[str, object]) -> Mapping[str, object]:
        """Add the result of Flask context processors to the given context."""
        # NOTE: We're not using `app.update_template_context` because we don't want
        # g, request, session etc.

        # Updates `context` in place. Will not overwrite keys already in context.
        if self.flask_context_processors:
            processors = self.app.template_context_processors
            funcs = processors[None]
            request_context = _request_ctx_stack.top
            if request_context is not None:
                blueprint = request_context.request.blueprint
                if blueprint is not None and blueprint in processors:
                    funcs = chain(funcs, processors[blueprint])

            orig_ctx = context.copy()
            for func in funcs:
                context.update(func())
            context.update(orig_ctx)
        return context

    @contextmanager
    def _signals(self, template: Template, context: Mapping[str, object]):
        if signals_available and self.flask_signals:
            before_render_template.send(
                self.app,
                template=template,
                context=context,
            )

        yield self

        if signals_available and self.flask_signals:
            template_rendered.send(
                self.app,
                template=template,
                context=context,
            )

    def render_template(self, template_name: str, **context: ...) -> str:
        """Render a Liquid template from the configured template loader."""
        context = self._make_context(context)
        template = self.env.get_template(template_name)

        with self._signals(template, context):
            rendered = template.render(**context)

        return rendered

    def render_template_string(self, source: str, **context: ...) -> str:
        """Render a Liquid template from a template string."""
        context = self._make_context(context)
        template = self.env.from_string(source)

        with self._signals(template, context):
            rendered = template.render(**context)

        return rendered


def render_template(template_name: str, **context: ...) -> str:
    """Render a Liquid template in the current Flask application context."""
    ext = current_app.extensions["flask_liquid"]
    return ext.render_template(template_name, **context)


def render_template_string(source: str, **context: ...) -> str:
    """Render a Liquid template from a string in the current Flask application
    context."""
    ext = current_app.extensions["flask_liquid"]
    return ext.render_template_string(source, **context)
