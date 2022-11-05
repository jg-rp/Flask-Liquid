Flask Liquid Change Log
=======================

Version 1.1.0
-------------

- We now use ``flask.globals.request_ctx`` instead of ``flask._request_ctx_stack`` when
  it is available. ``_request_ctx_stack`` is depreciated since Flask version 2.2.0 and
  will be removed in 2.3.0. 

Version 1.0.0
-------------

First stable release.

Version 0.4.1
-------------

- Fixed typing issues. Mypy in strict mode.
- Added ``cache_size``, ``expression_cache_size``, ``template_comments``,
  ``comment_start_string`` and ``comment_end_string`` arguments to ``Liquid``. All of
  these arguments get passed through to ``liquid.Environment``.

Version 0.4.0
-------------

- Added ``render_template_async`` and ``render_template_string_async`` functions for 
  rendering templates asynchronously.

Version 0.3.0
-------------

- Added the ``autoescape`` argument to ``Liquid``. If ``True`` (default), context
  variables will be HTML escaped before output.
- Added the ``auto_reload`` argument to ``Liquid``. If ``auto_reload`` is ``False``, 
  automatic reloading of templates is disabled. For deployments where template sources
  don't change between service reloads, setting auto_reload to `False` can yield an
  increase in performance by avoiding calls to ``uptodate``. Defaults to ``True``.

