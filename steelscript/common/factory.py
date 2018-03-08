# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

from __future__ import (unicode_literals, print_function, division,
                        absolute_import)

import logging

from importlib import import_module


class FactoryLookupError(LookupError):
    """
    Indicates that a lookup failed due to no module or class being found.

    If a module was found but did not import cleanly, do not use this
    exception, instead allow the ImportError to propagate.
    """
    pass


class NoModuleFound(FactoryLookupError):
    """
    No matching module was found.

    :param searched_modules: The list of modules examined.
    """
    def __init__(self, searched_modules):
        super(NoModuleFound, self).__init__(
            "Could not find a matching module, searched: [\n\t%s\n]" %
            '\n\t'.join((str(m) for m in searched_modules)))
        self.searched_modules = searched_modules


class TooManyCallables(FactoryLookupError):
    """
    Too many matching callables found in the matched module.

    :param module: The matched module
    :searched contents: The matching callables in the module.
    """
    def __init__(self, module, matched_contents):
        super(TooManyCallables, self).__init__(
            "Found too many callables in %s: [\n\t%s\n]" %
            (module, '\n\t'.join((str(c) for c in matched_contents))))
        self.module = module
        self.matched_contents = matched_contents


class NoMatchingCallable(FactoryLookupError):
    """
    No matching callables found in the matched module.

    :param module: The matched module
    :param searched_contents: The contents of the module that were examined.
    """
    def __init__(self, module, searched_contents=()):
        super(NoMatchingCallable, self).__init__(
            "No matching callable in %s, searched: [\n\t%s\n]" %
            (module, '\n\t'.join((str(c) for c in searched_contents))))
        self.module = module
        self.searched_contents = searched_contents


def set_marker(thing, mark_name):
    """
    Decorator for marking something for future searches within modules.

    :param thing: A class or other callable that produces an instance
        of whatever the mark represents.
    :param mark_name: The text to use for the mark.
    """
    setattr(thing, mark_name, True)
    return thing


def check_marker(thing, mark_name, parent=None):
    """
    Companion to the @set_marker decorator to find marked things.

    These two functions are intended to be used to implement pairs
    of private mark/check functions within a specific factory module.

    :param thing: Any object which we will check for decoration.
    :param mark_name: The name to look for as a mark.
    :param parent: Optionally, a parent class to require if ``thing``
        is a class.  Silently ignored if ``thing`` is not a class.
    """
    # Could make this one big condition, but more readable like this.
    if not hasattr(thing, mark_name) or not getattr(thing, mark_name):
        return False
    if parent and type(thing) is type and not issubclass(thing, parent):
        return False
    return True


def get_by_standard_fwk_layout(build_info, module_name,
                               service=None, feature=None,
                               check=None, first_fail=False, versioned=True):
    """
    The order of packages in which we search is determined by the
    subproducts list in the build info, which always begins with
    the main product and ends with the framework.

    The location is further specified by the given service or feature
    (if any).

    :param build_info: A dictionary of build information from which
        most of the factory parameters are drawn.
    :param module_name: The module portion of the search for this particular
        factory lookup.
    :param service: The name of a REST service.  Must be None if feature
        is specified.
    :param feature: The name of a non-REST service area of functionality.
        This may be an area composed of multiple REST services.  Must be None
        if service is specified.
    :param check: An optional callable to apply to each of the module contents.
        A single match is required, and will be returned in place of the
        module.
    :param first_fail: If ``True`` and ``check`` is passed, raise an
        exception the first time we find a module if none of its contents
        pass the check.  By default, this is ``False`` and the lookup
        will continue searching more modules.
    :param versioned: If ``True`` (the default), use the build info
        to look for a version-specific module path.

    :return: The imported module or (if a module content check is given),
        the module attribute that passed the check.

    :raises TypeError: if both service and feature are not None.
        It is valid for both of them to be None.
    :raises NoModuleFound: if no module path produced by the search list
        exists, or if ``check`` is specified and ``first_fail`` is False,
        no module that was found had any contents matching the check.
    :raises NoMatchingCallable: if ``check`` is specified, ``first_fail``
        is ``True`` and no module attributes pass the check.
    :raises TooManyCallables: if ``check`` was specified and matched
        multiple attributes in the module.
    :raises ImportError: if a module exists but fails to import.  This is the
        import error triggered by attempting to import the module in question.
    """
    # TODO: build_info should be used to pass the following information:
    #   sub_products:  list of products on this appliance.
    #   package:  e.g. "steelscript.steelhead"
    #   version:  Current product version.  e.g. '8.5.1a'
    args = {
        'base_package': 'steelscript.steelhead',
        'module_name': module_name,
        'service': service,
        'feature': feature,
        'check': check,
        'first_fail': first_fail
    }
    if versioned:
        # TODO:  Finding the 'search_list'
        # The search_start_value should come from the build_info.
        args['search_list'] = ['v9_0', 'v8_6', 'v8_5', 'v8_0']
        args['search_start_value'] = 'v9_0'
    return get_by_standard_layout(**args)


def get_by_standard_layout(base_package, module_name, search_list=None,
                           search_start_value=None,
                           service=None, feature=None,
                           check=None, first_fail=False):
    """
    Implement a dynamic lookup based on common SteelScript layout patterns.

    The basic structure is::
      base_package.<optional area>.<version from search_list>.module_name

    where the optional area may be::

      services.<service>
        (for REST Service based products)
      features.<feature>
        (for large systems including non-REST Service based products)

    Optionally, a callable may be passed as a check on the module contents.
    If passed, then a single attribute of the module must pass the check,
    and that attribute is returned instead of the module itself.

    The lookup can either fail on the first module that fails a check,
    or can continue looking for more matching modules that could pass it.

    :param base_package: The initial python prefix, i.e.
        ``steelscript.steelhead``.  Required.
    :param module_name: The name of the last module in the path.  Typically
        named for the type of module.
    :param service: The name of a REST service.  Must be None if feature
        is specified.
    :param feature: The name of a non-REST service area of functionality.
        This may be an area composed of multiple REST services.  Must be None
        if service is specified.
    :param search_list: A list of 2nd-to-last module components to search.
        If None, this aspect of searching is omitted.
    :param search_start_value: The value to start from in the list.  If None,
        start from the beginning.
    :param check: An optional callable to apply to each of the module contents.
        A single match is required, and will be returned in place of the
        module.
    :param first_fail: If ``True`` and ``check`` is passed, raise an
        exception the first time we find a module if none of its contents
        pass the check.  By default, this is ``False`` and the lookup
        will continue searching more modules.

    :return: The imported module or (if a module content check is given),
        the module attribute that passed the check.

    :raises TypeError: if both service and feature are not None.
        It is valid for both of them to be None.
    :raises NoModuleFound: if no module path produced by the search list
        exists, or if ``check`` is specified and ``first_fail`` is False,
        no module that was found had any contents matching the check.
    :raises NoMatchingCallable: if ``check`` is specified, ``first_fail``
        is ``True`` and no module attributes pass the check.
    :raises TooManyCallables: if ``check`` was specified and matched
        multiple attributes in the module.
    :raises ImportError: if a module exists but fails to import.  This is the
        import error triggered by attempting to import the module in question.
    """
    if None not in(service, feature):
        raise TypeError("At most one of service or feature may be set.")

    mod_template = _make_module_template(base_package, module_name,
                                         service, feature,
                                         bool(search_list))
    searched = []
    if search_list:
        if search_start_value is None:
            start_pos = 0
        else:
            start_pos = search_list.index(search_start_value)

        for name in search_list[start_pos:]:
            mod_path = mod_template % name
            result = _attempt_import_and_check(searched, mod_path,
                                               check, first_fail)
            if result is not None:
                return result
    else:
        # Nothing to templatize, mod_template == mod_path.
        result = _attempt_import_and_check(searched, mod_template, check,
                                           first_fail)
        if result is not None:
            return result

    raise NoModuleFound(searched_modules=searched)


def _attempt_import_and_check(searched, mod_path, check, first_fail):
    try:
        searched.append(mod_path)
        module = import_module(mod_path)
        if check is None:
            return module
        thing = _run_check(module, check, first_fail)
        if thing is not None:
            return thing

    except ImportError as ie:
        # TODO: Is this message the same in Python 3?
        # Last token is the import name that failed, which may just be
        # the tail of our attempted module if parts of the module path
        # exist.
        not_found = str(ie).split()[-1]
        if not mod_path.endswith(not_found):
            # If we found it and it won't import properly, for some
            # other reason such as a module that *it* imports not
            # existing, we should let that error escape.
            raise
        logging.debug("Module '%s' not present.  Continuing lookup..." %
                      mod_path)


def _run_check(module, check, first_fail):
    attrs = [getattr(module, a) for a in dir(module)]
    matches = [a for a in attrs if check(a)]
    if len(matches) == 1:
        return matches[0]

    if len(matches) > 1:
        raise TooManyCallables(module, matches)

    # No matches if we get this far.
    check_str = '' if check.__doc__ is None else (' (%s)' % check.__doc__)
    message = ("Module '%s' found but no contents pass the check%s." %
               (module, check_str))
    if first_fail:
        logging.debug(("%s  Ending lookup for this package on "
                       "first failed check.") % message)
        raise NoMatchingCallable(module, matches)

    logging.debug("%s  Continuing lookup..." % message)
    return None


def _make_module_template(base_package, module_name, service, feature,
                          versioned):
    if service is not None:
        prefix = '%s.services.%s' % (base_package, service)
    elif feature is not None:
        prefix = '%s.features.%s' % (base_package, feature)
    else:
        prefix = base_package

    if versioned:
        # The %%s in the middle is intentional, as this has two passes of
        # substitution performed on it.
        return '%s.%%s.%s' % (prefix, module_name)
    else:
        return '%s.%s' % (prefix, module_name)
