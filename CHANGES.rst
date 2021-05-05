Flask Liquid Change Log
=======================

Version 0.3.0
-------------

- Added the ``autoescape`` argument to ``Liquid``. If ``True`` (default), context
  variables will be HTML escaped before output.
- Added the ``auto_reload`` argument to ``Liquid``. If ``auto_reload`` is ``False``, 
  automatic reloading of templates is disabled. For deployments where template sources
  don't change between service reloads, setting auto_reload to `False` can yield an
  increase in performance by avoiding calls to ``uptodate``. Defaults to ``True``.

