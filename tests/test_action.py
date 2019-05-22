# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

from __future__ import (unicode_literals, print_function, division,
                        absolute_import)

import mock
import pytest

from steelscript.common.interaction import action


FAKE_PKG = 'ss_fake_action'
FAKE_FOLDERS = [FAKE_PKG, 'services', 'appflow', 'victoria']
FAKE_ACTION = """
from steelscript.common.interaction import action

@action.action
class AppflowAction(action.Action):
    pass

class CLI(object):
    pass
"""


@pytest.yield_fixture
def patched_get():
    with mock.patch('steelscript.common.interaction.uidelegation.'
                    'UIDelegator._get_ui_delegatee') as get_cli:

        get_cli.return_value = mock.Mock()
        yield {'cli': get_cli.return_value}


@pytest.fixture
def ss_fake(tmpdir):
    # Create a dir structure in a temp folder.
    temppath = tmpdir
    for folder in FAKE_FOLDERS:
        temppath = temppath.mkdir(folder)
        temppath.join("__init__.py").write("")
    action_path = temppath.join("action.py")
    action_path.write(FAKE_ACTION)

    # Add the temp folder to sys path, import our modules
    import sys
    sys.path.append(str(tmpdir))

    import importlib
    return importlib.import_module(".".join(FAKE_FOLDERS + ['action']))


def test_object_properties(patched_get):
    actor = action.Action(resource=mock.Mock())

    assert type(actor) is action.Action

    assert hasattr(actor, 'cli_delegatee')
    assert hasattr(actor.cli_delegatee, 'model')
    assert actor.cli_delegatee.model


def test_factory_call(ss_fake, patched_get):
    test_module = ss_fake

    service = 'appflow'
    codename = 'v9_0'
    codename_set = ['v9_0', 'v8_6', 'v8_5', 'v8_0']

    with mock.patch('steelscript.common.factory.get_by_standard_layout') \
            as get_factory:

        get_factory.return_value = test_module.AppflowAction
        resource = mock.Mock()

        actor = action.Action.get(resource=resource, service=service)
        assert type(actor) is test_module.AppflowAction
        assert actor.cli_delegatee is patched_get['cli']

        # Should be called only once because we mocked the calls for cli/rest
        call_args = get_factory.call_args

        # reversed iterators don't compare like lists or tuples.
        # 2nd called_with tuple element is kwargs
        call_args[1]['search_list'] = [x for x in call_args[1]['search_list']]

        expected_with = {'base_package': 'steelscript.steelhead',
                         'module_name': 'action',
                         'search_list': codename_set,
                         'search_start_value': codename,
                         'check': action._check_action,
                         'service': service,
                         'feature': None,
                         'first_fail': True}

        # called_args looks like (args, kwargs)
        assert len(call_args[0]) == 0
        assert call_args[1] == expected_with
