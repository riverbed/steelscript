# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import sys
import os.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import pytest

from steelscript.common import factory

import math as ANY_MODULE
ANY_CONTENTS = (object, )
BASE_PKG = 'ss_fake'
SEARCH_LIST = ['four', 'three', 'two', 'one']
FEATURE = 'legacy_feature'
SERVICE = 'awesome_service'

# NOTE: These tests all use the package tree found in the test directory.
#       Instrumenting sys.modules is more trouble than it's worth.
#       I suppose we could create and delete this in fixtures.  That also
#       seems like more trouble than it's worth.
#
#       For reference, this is the expected tree and why each file is there:
#
# ss_fake/
#   __init__.py
#   unversioned.py
#   services/
#       __init__.py
#       awesome_service/
#           __init__.py
#           one/
#               __init__.py
#               model.py        # If we find this, started in wrong place.
#           two/
#               __init__.py
#               model.py        # A test tries to find this
#                   FooBar      # A test tries to find this class
#               action.py       # NOTE: Generates syntax error
#           four/
#               __init__.py
#               action.py       # If we find this, ignored start point.
#   features/
#       __init__.py
#       legacy_feature/
#           __init__.py
#           one/
#               __init__.py
#               model.py        # This can be loaded successfully, but...
#           three/
#               __init__.py
#               model.py        # NOTE: This will fail to import.
#   two/
#       __init__.py
#       weird.py                # Test for monolithic setups.


def test_monolithic():
    m = factory.get_by_standard_layout(BASE_PKG, 'weird',
                                       search_list=SEARCH_LIST)
    assert os.path.join(BASE_PKG, 'two', 'weird.py') in m.__file__


def test_monolithic_not_found():
    with pytest.raises(factory.NoModuleFound):
        factory.get_by_standard_layout(BASE_PKG, 'weird',
                                       search_list=SEARCH_LIST,
                                       search_start_value='one')


def test_feature_import_error():
    # The newest model in this path tries to import something that doesn't
    # exist, in order to genrerate an ImportError distinct from
    # a FactoryLookupError.
    with pytest.raises(ModuleNotFoundError):
        factory.get_by_standard_layout(BASE_PKG, 'model',
                                       search_list=SEARCH_LIST,
                                       feature=FEATURE)


def test_feature_start_after_error_before_expected():
    m = factory.get_by_standard_layout(BASE_PKG, 'model',
                                       search_list=SEARCH_LIST,
                                       search_start_value='two',
                                       feature=FEATURE)
    assert (os.path.join(BASE_PKG, 'features', FEATURE, 'one', 'model.py') in
            m.__file__)


def test_service_start_on_expected():
    # This test also ensures that we don't do an off-by-one indexing error
    # and skip the starting point.
    m = factory.get_by_standard_layout(BASE_PKG, 'model',
                                       search_list=SEARCH_LIST,
                                       search_start_value='two',
                                       service=SERVICE)
    assert (os.path.join(BASE_PKG, 'services', SERVICE, 'two', 'model.py') in
            m.__file__)


def test_other_error():
    # Testing an import error from within the imported file is covered above.
    # We should also allow other sorts of errors to escape unchanged.
    # TODO: Is this correct or should we convert them to FactoryLookupError?

    with pytest.raises(SyntaxError):
        factory.get_by_standard_layout(BASE_PKG, 'action',
                                       search_list=SEARCH_LIST,
                                       service=SERVICE)


def test_not_found():
    with pytest.raises(factory.NoModuleFound):
        factory.get_by_standard_layout(BASE_PKG, 'action',
                                       search_list=SEARCH_LIST,
                                       feature=FEATURE)


# ####### Exception tests ############
# pytest.raises only gives you access to py.code ExceptionInfo classes,
# which are useless for more interesting exceptions as they truncate
# the message at the first newline.

def test_exception_modules():
    try:
        raise factory.NoModuleFound(searched_modules=('one', 'two'))
    except factory.NoModuleFound as fle:
        assert 'one' in str(fle)
        assert 'two' in str(fle)


def test_exception_contents():
    try:
        raise factory.NoMatchingCallable(module=ANY_MODULE,
                                         searched_contents=('Three', 'Four'))
    except factory.FactoryLookupError as fle:
        assert str(ANY_MODULE) in str(fle)
        assert 'Three' in str(fle)
        assert 'Four' in str(fle)


def test_exception_both_real_obj():
    try:
        raise factory.NoMatchingCallable(module=ANY_MODULE,
                                         searched_contents=ANY_CONTENTS)
    except factory.NoMatchingCallable as fle:
        assert str(ANY_MODULE) in str(fle)
        for c in ANY_CONTENTS:
            assert str(c) in str(fle)


def test_exception_no_callables():
    try:
        raise factory.NoMatchingCallable(module=ANY_MODULE)
    except factory.NoMatchingCallable as fle:
        assert 'No match' in str(fle)
        assert str(ANY_MODULE) in str(fle)


def test_exception_too_many_callables():
    try:
        raise factory.TooManyCallables(matched_contents=ANY_CONTENTS,
                                       module=ANY_MODULE)
    except factory.TooManyCallables as fle:
        uni = str(fle)
        assert 'too many callables' in uni
        for c in ANY_CONTENTS:
            assert str(c) in uni
        assert str(ANY_MODULE) in uni


def test_not_found_init():
    nfe = factory.NoModuleFound(searched_modules=(ANY_MODULE,))
    assert nfe.searched_modules == (ANY_MODULE,)


def test_too_many_init():
    tmc = factory.TooManyCallables(module=ANY_MODULE,
                                   matched_contents=ANY_CONTENTS)
    assert tmc.module == ANY_MODULE
    assert tmc.matched_contents == ANY_CONTENTS


def test_no_matching():
    nmc = factory.NoMatchingCallable(module=ANY_MODULE,
                                     searched_contents=ANY_CONTENTS)
    assert nmc.module == ANY_MODULE
    assert nmc.searched_contents == ANY_CONTENTS


@pytest.fixture
def check_foobar():
    check_foobar = lambda c: type(c) is type and c.__name__ == 'FooBar'
    check_foobar.__doc__ = 'class name is "FooBar"'
    return check_foobar


def test_check(check_foobar):
    # Test to make sure we skip modules when a check is supplied.
    # In the ss_fake dir, four/model.py has no class, two/model.py has one.

    m = factory.get_by_standard_layout(BASE_PKG, 'model',
                                       search_list=SEARCH_LIST,
                                       search_start_value='four',
                                       service=SERVICE,
                                       check=check_foobar)
    assert m.__name__ == 'FooBar'
    assert m.__module__ == '.'.join((BASE_PKG, 'services', SERVICE,
                                     'two', 'model'))


def test_check_first_fail(check_foobar):
    with pytest.raises(factory.NoMatchingCallable):
        factory.get_by_standard_layout(BASE_PKG, 'model',
                                       search_list=SEARCH_LIST,
                                       search_start_value='four',
                                       service=SERVICE,
                                       check=check_foobar,
                                       first_fail=True)


def test_unversioned():
    # This form is used when a higher layer of factory calculates
    # the base package.
    m = factory.get_by_standard_layout(BASE_PKG, 'unversioned')
    assert 'unversioned' in str(m)


def test_unversioned_fail():
    with pytest.raises(factory.NoModuleFound):
        factory.get_by_standard_layout(BASE_PKG, 'doesnotexist')
