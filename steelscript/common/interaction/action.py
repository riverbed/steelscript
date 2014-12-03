# Copyright (c) 2014 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

from __future__ import (unicode_literals, print_function, division,
                        absolute_import)

from steelscript.common import factory
from steelscript.common.interaction import uidelegation


def action(thing):
    """
    Decorator for flagging a class as an action.

    :param thing: A class or other callable that produces an action instance.
    """
    return factory.set_marker(thing, '_produces_action')


def _check_action(thing):
    """
    Companion to the @action decorator to keep the marking private to
    these two functions.  This function is private to this module.

    :param thing: Any object which we will check for decoration.
    """
    return factory.check_marker(thing, '_produces_action', Action)


class Action(uidelegation.UIDelegator):
    """
    Base Action class for Riverbed appliance methods

    :param resource: The resource to which this Action is attached.
    :param build_info: Pre-fetched build information, if available.
    """

    @classmethod
    def get(cls, resource, service=None, feature=None, **kwargs):
        """
        Look up an action instance for this resource based on its build info

        The location is further specified by the given service or feature.
        Either feature or service must be specified, but not both.

        :param resource: The resource for which we are looking up an action.
        :param service: The REST service, if there is a single service that
            the action represents.  Either this or `feature` must
            be specified, but not both.
        :param feature: The feature (which may be a grouping of REST services
            or a legacy non-REST area) that the action represents.  Either
            this or `service` must be specified, but not both.

        :return: An instance of the appropriate action class.

        :raises ValueError: if the version lookup returns data that this method
            does not understand.
        :raises pq_runtime.factory.FactoryLookupError: if no action can
            be found.
        :raises ImportError: if a module was found but failed to import
            properly.  Other errors that Python may raise while importing
            a module may also be raised out of this method.
        """
        # TODO: Read the build_info from the resource.  Right now 'None'
        # just means 'use the latest'.
        build_info = None

        action_callable = factory.get_by_standard_fwk_layout(
            build_info=build_info,
            module_name='action',
            service=service,
            feature=feature,
            check=_check_action,
            first_fail=True)
        return action_callable(resource, service=service, feature=feature,
                               **kwargs)
