# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

from __future__ import (unicode_literals, print_function, division,
                        absolute_import)

from steelscript.common import factory


def model(thing):
    """
    Decorator for flagging a class as a model.

    :param thing: A class or other callable that produces a model instance.
    """
    return factory.set_marker(thing, '_produces_model')


def _check_model(thing):
    """
    Companion to the @model decorator to keep the marking private to
    these two functions.  This function is private to this module.

    :param thing: Any object which we will check for decoration.
    """
    return factory.check_marker(thing, '_produces_model', Model)


class Model(object):
    """
    Base Model class for Riverbed appliance CLI model methods

    :param resource: The resource to which this model is attached.
    :param cli: An open CLI session, if available.
    :param build_info: Pre-fetched build information, if available.
    """

    @classmethod
    def get(cls, resource, service=None, feature=None, **kwargs):
        """
        Look up a model instance for this resource based on its build info

        Either feature or service must be specified, but not both.

        :param resource: The resource for which we are looking up a model.
        :param service: The lumberjack service, if there is a single service
            that the model represents.  Either this or `feature` must
            be specified, but not both.
        :param feature: The feature (which may be a grouping of lumberjack
            services or a legacy non-lumberjack area) that the model
            represents.  Either this or `service` must be specified,
            but not both.

        :return: An instance of the appropriate model class.

        :raises steelscript.common.factory.FactoryLookupError: if no model can
            be found.
        :raises ImportError: if a module was found but failed to import
            properly.  Other errors that Python may raise while importing
            a module may also be raised out of this method.
        """
        # TODO: Read the build_info from the resource.  Right now 'None'
        # just means 'use the latest'.
        build_info = None

        model_callable = factory.get_by_standard_fwk_layout(
            build_info=build_info,
            module_name='model',
            service=service,
            feature=feature,
            check=_check_model,
            first_fail=True)
        return model_callable(resource, **kwargs)

    def __init__(self, resource, cli=None, **kwargs):
        self._cli = cli
        self._resource = resource

    @property
    def cli(self):
        """
        The raw CLI object.  Will open one if none exists.
        """
        if self._cli is None:
            # TODO: Use the CLICache.
            self._cli = self._resource.cli
        return self._cli
