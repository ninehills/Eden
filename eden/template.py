#!/usr/bin/env python

from mako.lookup import TemplateLookup

template_vars = {
    
}


def get_template(path):
    return _g_lookup.get_templte(path)


def new_templatelookup(directories, filesystem_checks=True, module_directory=None):
    import os.path
    module_directory = module_directory or os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cache')
    lookup = TemplateLookup(directories=directories, filesystem_checks=True,
                            module_directory=module_directory, input_encoding='utf-8', output_encoding='utf-8', encoding_errors='replace')
    return lookup


def setup_template(directories, cache=False, module_cache_dir=None):
    global _g_lookup
    _g_lookup = new_templatelookup(directories, filesystem_checks=True, module_directory=None)


def render_template(path, **kwargs):
    kwargs.update(template_vars)
    return _g_lookup.get_template(path).render(**kwargs)

