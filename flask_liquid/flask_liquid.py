"""Add Liquid templates to a Flask application."""

from __future__ import annotations

from contextlib import contextmanager
from itertools import chain
from typing import TYPE_CHECKING
from typing import Any
from typing import Callable
from typing import Dict
from typing import Iterable
from typing import Iterator
from typing import Mapping
from typing import Optional
from typing import Type

from flask import Flask
from flask import before_render_template
from flask import current_app
from flask import template_rendered
from flask.globals import request_ctx
from liquid import BaseLoader  # type: ignore
from liquid import Environment
from liquid import FileSystemLoader
from liquid import Mode
from liquid import Undefined

if TYPE_CHECKING:
    from liquid import BoundTemplate


class Liquid:
    """The Liquid template extension for Flask.

    Args:
        extra: If `True`, register all extra tags and filters. Defaults to `False`.
        tag_start_string: The sequence of characters indicating the start of a
            liquid tag.
        tag_end_string: The sequence of characters indicating the end of a liquid
            tag.
        statement_start_string: The sequence of characters indicating the start of
            an output statement.
        statement_end_string: The sequence of characters indicating the end of an
            output statement.
        template_comments: If `True`, enable template comments, where, by default,
            anything between `{#` and `#}` is considered a comment.
        comment_start_string: The sequence of characters indicating the start of a
            comment. `template_comments` must be `True` for `comment_start_string`
            to have any effect.
        comment_end_string: The sequence of characters indicating the end of a
            comment.  `template_comments` must be `True` for `comment_end_string`
            to have any effect.
        tolerance: Indicates how tolerant to be of errors. Must be one of
            `Mode.LAX`, `Mode.WARN` or `Mode.STRICT`.
        loader: A template loader. If you want to use the builtin "render" or
            "include" tags, a loader must be configured.
        undefined: A subclass of `Undefined` that represents undefined values. Could be
            one of the built-in undefined types, `Undefined`, `DebugUndefined` or
            `StrictUndefined`.
        strict_filters: If `True`, will raise an exception upon finding an
            undefined filter. Otherwise undefined filters are silently ignored.
        autoescape: If `True`, all render context values will be HTML-escaped before
            output unless they've been explicitly marked as "safe".
        globals: An optional mapping that will be added to the render context of any
            template loaded from this environment.
        flask_context_processors: If set to `True` Flask context processors
            will be applied to Liquid every render context. Defaults to `False`.
        flask_signals: If set to `True` the `template_rendered` and
            `before_template_rendered` signals will be emitted for Liquid templates.
            Defaults to `True`.
    """

    def __init__(
        self,
        app: Optional[Flask] = None,
        *,
        extra: bool = False,
        tag_start_string: str = r"{%",
        tag_end_string: str = r"%}",
        statement_start_string: str = r"{{",
        statement_end_string: str = r"}}",
        tolerance: Mode = Mode.STRICT,
        loader: Optional[BaseLoader] = None,
        undefined: Type[Undefined] = Undefined,
        strict_filters: bool = True,
        autoescape: bool = True,
        globals: Optional[Mapping[str, object]] = None,  # noqa: A002
        template_comments: bool = False,
        comment_start_string: str = "{#",
        comment_end_string: str = "#}",
        flask_context_processors: bool = False,
        flask_signals: bool = True,
    ):
        self.app = app

        self.env = Environment(
            extra=extra,
            tag_start_string=tag_start_string,
            tag_end_string=tag_end_string,
            statement_start_string=statement_start_string,
            statement_end_string=statement_end_string,
            tolerance=tolerance,
            loader=loader,
            undefined=undefined,
            strict_filters=strict_filters,
            autoescape=autoescape,
            globals=globals,
            template_comments=template_comments,
            comment_start_string=comment_start_string,
            comment_end_string=comment_end_string,
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

    def init_app(self, app: Flask) -> None:
        """Initialise a Flask app with a Liquid environment."""
        app.config.setdefault(
            "LIQUID_TAG_START_STRING",
            self.env.tag_start_string,
        )
        app.config.setdefault(
            "LIQUID_TAG_END_STRING",
            self.env.tag_end_string,
        )
        app.config.setdefault(
            "LIQUID_STATEMENT_START_STRING",
            self.env.statement_start_string,
        )
        app.config.setdefault(
            "LIQUID_STATEMENT_END_STRING",
            self.env.statement_end_string,
        )

        app.config.setdefault(
            "LIQUID_TEMPLATE_COMMENTS",
            self.env.template_comments,
        )
        app.config.setdefault(
            "LIQUID_COMMENT_START_STRING",
            self.env.comment_start_string or "{#",
        )
        app.config.setdefault(
            "LIQUID_COMMENT_END_STRING",
            self.env.comment_end_string or "#}",
        )

        app.config.setdefault("LIQUID_TOLERANCE", self.env.mode)
        app.config.setdefault("LIQUID_UNDEFINED", self.env.undefined)
        app.config.setdefault("LIQUID_STRICT_FILTERS", self.env.strict_filters)
        app.config.setdefault("LIQUID_TEMPLATE_FOLDER", app.template_folder)
        app.config.setdefault("LIQUID_AUTOESCAPE", self.env.autoescape)

        app.config.setdefault(
            "LIQUID_FLASK_CONTEXT_PROCESSORS",
            self.flask_context_processors,
        )
        app.config.setdefault(
            "LIQUID_FLASK_SIGNALS",
            self.flask_signals,
        )

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
        self.env.undefined = app.config["LIQUID_UNDEFINED"]
        self.env.strict_filters = app.config["LIQUID_STRICT_FILTERS"]
        self.env.autoescape = app.config["LIQUID_AUTOESCAPE"]
        self.env.mode = app.config["LIQUID_TOLERANCE"]
        self.env.loader = self._loader

        self.env.comment_start_string = app.config["LIQUID_COMMENT_START_STRING"]
        self.env.comment_end_string = app.config["LIQUID_COMMENT_END_STRING"]
        self.env.template_comments = app.config["LIQUID_TEMPLATE_COMMENTS"]

        # Working around a bad decision in the Environment constructor.
        if not self.env.template_comments:
            self.env.comment_start_string = ""
            self.env.comment_end_string = ""

        app.extensions["flask_liquid"] = self
        self.app = app

    def _make_context(self, context: Dict[str, object]) -> Dict[str, object]:
        """Add the result of Flask context processors to the given context."""
        # NOTE: We're not using `app.update_template_context` because we don't want
        # g, request, session etc.

        # Updates `context` in place. Will not overwrite keys already in context.
        if self.flask_context_processors and self.app:
            processors = self.app.template_context_processors
            funcs: Iterable[Callable[[], Any]] = processors[None]
            request_context = request_ctx

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
    def _signals(
        self, template: BoundTemplate, context: Mapping[str, object]
    ) -> Iterator[Liquid]:
        if self.flask_signals:
            before_render_template.send(
                self.app,
                template=template,
                context=context,
            )

        yield self

        if self.flask_signals:
            template_rendered.send(
                self.app,
                template=template,
                context=context,
            )

    def render_template(self, template_name: str, **context: object) -> str:
        """Render a Liquid template from the configured template loader."""
        context = self._make_context(context)
        template = self.env.get_template(template_name)

        with self._signals(template, context):
            return template.render(**context)

    async def render_template_async(self, template_name: str, **context: object) -> str:
        """Render a Liquid template from the configured template loader."""
        context = self._make_context(context)
        template = await self.env.get_template_async(template_name)

        with self._signals(template, context):
            return await template.render_async(**context)

    def render_template_string(self, source: str, **context: object) -> str:
        """Render a Liquid template from a template string."""
        context = self._make_context(context)
        template = self.env.from_string(source)

        with self._signals(template, context):
            return template.render(**context)

    async def render_template_string_async(self, source: str, **context: object) -> str:
        """Render a Liquid template from a template string."""
        context = self._make_context(context)
        template = self.env.from_string(source)

        with self._signals(template, context):
            return await template.render_async(**context)


def render_template(template_name: str, **context: object) -> str:
    """Render a Liquid template in the current Flask application context."""
    ext: Liquid = current_app.extensions["flask_liquid"]
    return ext.render_template(template_name, **context)


async def render_template_async(template_name: str, **context: object) -> str:
    """Render a Liquid template in the current Flask application context."""
    ext: Liquid = current_app.extensions["flask_liquid"]
    return await ext.render_template_async(template_name, **context)


def render_template_string(source: str, **context: object) -> str:
    """Render a template from a string in the current Flask application context."""
    ext: Liquid = current_app.extensions["flask_liquid"]
    return ext.render_template_string(source, **context)


async def render_template_string_async(source: str, **context: object) -> str:
    """Render a template from a string in the current Flask application context."""
    ext: Liquid = current_app.extensions["flask_liquid"]
    return await ext.render_template_string_async(source, **context)
