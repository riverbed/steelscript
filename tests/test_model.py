# Copyright (c) 2014 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

from __future__ import (unicode_literals, print_function, division,
                        absolute_import)

import mock
import pytest

from steelscript.common import factory
from steelscript.common.interaction import model

import copy as ANY_MODULE_1
import math as ANY_MODULE_2

ANY_SEARCHED_MODULES = (ANY_MODULE_1, ANY_MODULE_2)


def test_check_undecorated_model():
    class NotReallyAModel(model.Model):
        pass

    assert model._check_model(NotReallyAModel) is False


def test_check_decorated_model():
    @model.model
    class ReallyAModel(model.Model):
        pass

    assert model._check_model(ReallyAModel)


def test_check_model_factory():
    @model.model
    def model_factory():
        pass

    assert model._check_model(model_factory)


class FakeModule(object):
    class ActualModel(model.Model):
        def __init__(self, resource, **kwargs):
            super(FakeModule.ActualModel, self).__init__(resource,
                                                         **kwargs)
            self.kwargs = kwargs


@pytest.yield_fixture
def patched_factory():
    with mock.patch('steelscript.common.factory.get_by_standard_layout') as \
            get_factory:

        def return_module_func(*args, **kwargs):
            if kwargs['check'] is not None:
                return FakeModule.ActualModel
            return FakeModule

        get_factory.side_effect = return_module_func
        yield get_factory


@pytest.yield_fixture
def patched_fail_factory():
    with mock.patch('steelscript.common.factory.get_by_standard_layout') as \
            get_factory:

        def return_module_func(*args, **kwargs):
            raise factory.NoModuleFound(ANY_SEARCHED_MODULES)

        get_factory.side_effect = return_module_func
        yield get_factory


@pytest.fixture
def data():
    service = 'appflow'
    codename = 'v9_0'
    codename_set = ['v9_0', 'v8_6', 'v8_5', 'v8_0']

    # reversed iterators don't compare like lists or tuples,
    # so unpack them back into lists.
    sh_kwargs = {
        'base_package': 'steelscript.steelhead',
        'module_name': 'model',
        'search_list': codename_set,
        'search_start_value': codename,
        'service': service,
        'feature': None,
        'check': model._check_model,
        'first_fail': True,
    }

    return {
        'build_info': None,  # Currently aren't reading the version/build info
        'sh_kwargs': sh_kwargs,
    }


@pytest.fixture
def resource(data):
    resource = mock.MagicMock()
    return resource


def test_factory_call(patched_factory, resource, data):
    m = model.Model.get(resource=resource,
                        service=data['sh_kwargs']['service'])
    assert type(m) is FakeModule.ActualModel
    assert m.kwargs == {}

    call_args_list = patched_factory.call_args_list
    exp_args_list = (data['sh_kwargs'],)

    for exp_args, call_args in zip(exp_args_list, call_args_list):
        # 2nd called_with tuple element is kwargs
        # Unroll reversed iterator into regular list for comparison.
        call_args[1]['search_list'] = [x for x in call_args[1]['search_list']]

        # called_args looks like (args, kwargs)
        assert len(call_args[0]) == 0
        assert call_args[1] == exp_args


def test_factory_model_kwargs(patched_factory, resource, data):
    m = model.Model.get(resource=resource,
                        service=data['sh_kwargs']['service'],
                        foo='bar')
    assert m.kwargs == {'foo': 'bar'}


def test_factory_fail(patched_fail_factory, resource, data):
    with pytest.raises(factory.NoModuleFound):
        # pytest exception objects are useless, need to
        # catch the real thing for data verification.
        try:
            model.Model.get(resource=resource,
                            service=data['sh_kwargs']['service'])
        except factory.NoModuleFound as nmf:
            assert nmf.searched_modules == ANY_SEARCHED_MODULES

            # trigger the pytest.raises
            raise


def test_model_init():
    resource = mock.Mock()
    cli = mock.Mock()
    build_info = {}

    m = model.Model(resource, cli=cli, build_info=build_info,
                    this_arg_should_not_cause_a_type_error='whatever')

    assert type(m) is model.Model
    assert m.cli is cli

    # No public accessor for resource at this time.
    assert m._resource is resource
