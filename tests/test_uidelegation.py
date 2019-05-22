# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import mock
import pytest

from steelscript.common.interaction import uidelegation


FAKE_PKG = 'ss_fake_uideleg'
FAKE_FOLDERS = [FAKE_PKG, 'services', 'appflow', 'victoria']
FAKE_MODULE = 'action'
FAKE_ACTION = """
from steelscript.common.interaction import uidelegation

class AppflowAction(uidelegation.UIDelegator):
    pass

class CLI(uidelegation.CLIDelegatee):
    pass
"""


@pytest.yield_fixture
def patched_get():
    with mock.patch('steelscript.common.interaction.uidelegation.'
                    'UIDelegator._get_ui_delegatee') as get_cli:

        get_cli.return_value = 'cli'
        yield {'cli': get_cli.return_value}


@pytest.yield_fixture
def patched_get_factory(ss_fake):
    def side_effect(**kwargs):
        check_doc = kwargs['check'].__doc__.lower()
        if 'cli' in check_doc:
            return ss_fake.CLI
        else:
            return ss_fake.AppflowAction

    with mock.patch('steelscript.common.factory.get_by_standard_layout') \
            as get_factory:

        get_factory.side_effect = side_effect
        yield get_factory


@pytest.fixture
def ss_fake(tmpdir):
    # Create a dir structure in a temp folder.
    temppath = tmpdir
    for folder in FAKE_FOLDERS:
        temppath = temppath.mkdir(folder)
        temppath.join("__init__.py").write("")
    action_path = temppath.join("%s.py" % FAKE_MODULE)
    action_path.write(FAKE_ACTION)

    # Add the temp folder to sys path, import our modules
    import sys
    sys.path.append(str(tmpdir))

    import importlib
    return importlib.import_module(".".join(FAKE_FOLDERS + [FAKE_MODULE]))


def test_uidelegator_init(patched_get):
    resource = mock.Mock()

    deleg = uidelegation.UIDelegator(resource)

    assert type(deleg) is uidelegation.UIDelegator

    # No public accessor at this time.
    assert deleg._resource is resource

    assert deleg.cli_delegatee == 'cli'

    # Note: Implementing 'rest' and 'web' is a todo:
    with pytest.raises(NotImplementedError):
        assert deleg.rest_delegatee
    with pytest.raises(NotImplementedError):
        assert deleg.web_delegatee


def test_object_properties():
    class DummyClass(object):
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    with mock.patch('steelscript.common.interaction.uidelegation.'
                    'UIDelegator._get_ui_delegatee') as get_ui:
        delegatee = DummyClass()
        get_ui.return_value = delegatee

        deleg = uidelegation.UIDelegator(resource=mock.Mock())

        assert type(deleg.cli_delegatee) is DummyClass
        assert deleg.cli_delegatee is delegatee


def test_factory_call(ss_fake, patched_get_factory):
    test_module = ss_fake

    service = 'appflow'
    codename = 'v9_0'
    codename_set = ['v9_0', 'v8_6', 'v8_5', 'v8_0']

    with mock.patch('steelscript.common.interaction.model.Model.get') \
            as get_model:
        get_model.return_value = mock.Mock()

        resource = mock.Mock()

        deleg = test_module.AppflowAction(resource=resource, service=service)
        assert type(deleg) is test_module.AppflowAction
        assert type(deleg.cli_delegatee) is test_module.CLI

        # Should be called twice once for cli, at the moment
        call_args_list = patched_get_factory.call_args_list
        assert len(call_args_list) == 1

        # reversed iterators don't compare like lists or tuples.
        # 2nd called_with tuple element is kwargs
        for call_args in call_args_list:
            call_args[1]['search_list'] = \
                [x for x in call_args[1]['search_list']]
            codename_set_in_call = [x for x in reversed(codename_set)]

        expected_with = {'base_package': FAKE_PKG,
                         'module_name': 'action',
                         'search_list': codename_set_in_call,
                         'search_start_value': codename,
                         'service': service,
                         'feature': None}

        # call_args_list looks like [(args, kwargs), (args, kwargs)]
        # Currently, only 'CLI' is grabbed.
        assert len(call_args_list[0][0]) == 0

@pytest.mark.parametrize('kwargs', [
    {},
    {'service': mock.Mock()},
    {'feature': mock.Mock()},
])
def test_cli_base(kwargs):
    resource = mock.Mock()
    service = kwargs['service'] if 'service' in kwargs else None
    feature = kwargs['feature'] if 'feature' in kwargs else None

    with mock.patch('steelscript.common.interaction.model.Model.get') \
            as get_model:
        get_model.return_value = mock.Mock()

        instance = uidelegation.CLIDelegatee(resource=resource,
                                             service=service,
                                             feature=feature)

        assert instance.model is get_model.return_value
        get_model.assert_called_once_with(resource=resource,
                                          service=service,
                                          feature=feature)
