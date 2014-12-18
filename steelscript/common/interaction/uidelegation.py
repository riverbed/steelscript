# Copyright (c) 2014 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

from __future__ import (unicode_literals, print_function, division,
                        absolute_import)

from steelscript.common import factory


class UIDelegator(object):
    """
    Base for a Delegator class which delegates to multiple UI types:  REST,
    CLI, and/or Web.
    """

    def __init__(self, resource, service=None, feature=None):
        """
        Initializes self and all the delegatee instances.
        """
        self._resource = resource
        self._service = service
        self._feature = feature

        # Initialize Delegatees
        self._cli_delegatee = self._get_ui_delegatee(class_hint='CLI')

    def __getattr__(self, name):
        """
        Delegates unknown methods to a Delegatee class.

        Uses Depth-First Search style lookup using the preference order.
        """
        # TODO: Delegate to all of CLI, REST, and Web.  Only CLI is currently
        # supported.
        return getattr(self.cli_delegatee, name)

    def _get_ui_delegatee(self, class_hint, module_name=None):
        # Factory lookup to get all the delegatee classes (REST/CLI/Web)
        if module_name is None:
            # The UI classes share the same module as the delegator class, so
            # use self.__module__ to default the module name.
            module_name = self.__module__.split('.')[-1]

        check_class = lambda c: type(c) is type and c.__name__ == class_hint
        check_class.__doc__ = 'class name is "%s"' % class_hint

        # TODO: Read the build_info from the resource.  Right now 'None'
        # just means 'use the latest'.
        build_info = None

        ui_class = factory.get_by_standard_fwk_layout(
            build_info=build_info,
            module_name=module_name,
            service=self._service,
            feature=self._feature,
            check=check_class)
        return ui_class(resource=self._resource,
                        service=self._service,
                        feature=self._feature)

    @property
    def cli_delegatee(self):
        return self._cli_delegatee

    @property
    def rest_delegatee(self):
        raise NotImplementedError

    @property
    def web_delegatee(self):
        raise NotImplementedError


class CLIDelegatee(object):
    """
    Base class for all CLI Delegatees, such as with Action and Verification
    classes.

    The primary purpose of this class is to establish common resources and
    how to access them, namely access to the 'model' class.
    """
    def __init__(self, resource, service=None, feature=None):
        self._resource = resource
        self._service = service
        self._feature = feature
        self._model = None

    @property
    def model(self):
        """
        Lazily gets a handle to the corresponding model class.
        """
        if self._model is None:
            from steelscript.common.interaction.model import Model

            # Will raise as error if anything goes wrong.
            self._model = Model.get(resource=self._resource,
                                    service=self._service,
                                    feature=self._feature)
        return self._model
