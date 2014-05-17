# Copyright (c) 2014 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


from steelscript.common.jsondict import JsonDict

import unittest
import logging
import datetime

try:
    from testconfig import config
except ImportError:
    if __name__ != '__main__':
        raise
    config = {}

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s [%(levelname)-5.5s] %(msg)s")

class JsonDictTest(unittest.TestCase):

    def test_init_dict1(self):
        j = JsonDict(dict={'first' : 'John',
                           'last' : 'Doe',
                           'age' : 1})
        self.assertEqual(j.first, 'John')
        self.assertEqual(j.last, 'Doe')
        self.assertEqual(j.age, 1)
        self.assertEqual(j.first, j['first'])

        j.first = 'Judy'
        self.assertEqual(j.first, 'Judy')
        self.assertEqual(j.last, 'Doe')

    def test_init_dict2(self):
        j = JsonDict(dict={'name' : {'first' : 'John',
                                     'last' : 'Doe'},
                           'age' : 1})
        self.assertEqual(j.name.first, 'John')
        self.assertEqual(j.name.last, 'Doe')
        self.assertEqual(j.age, 1)
        self.assertEqual(j.name, {'first' : 'John', 'last' : 'Doe'})

        j.name.first = 'Joe'
        j.name.last = 'Blow'
        self.assertEqual(j.name, {'first' : 'Joe', 'last' : 'Blow'})
        self.assertEqual(j.age, 1)

    def test_init_kw1(self):
        j = JsonDict(first='John', last='Doe', age=1)
        self.assertEqual(j.first, 'John')
        self.assertEqual(j.last, 'Doe')
        self.assertEqual(j.age, 1)

    def test_init_kw2(self):
        j = JsonDict(name__first='John', name__last='Doe', age=1)
        self.assertEqual(j.name.first, 'John')
        self.assertEqual(j.name.last, 'Doe')
        self.assertEqual(j.age, 1)

    def test_bad_key(self):
        def try_foo(obj):
            return obj.foo

        j = JsonDict(first='John', last='Doe', age=1)
        self.assertRaises(KeyError, try_foo, j)

    def test_class_default1(self):
        class Widget(JsonDict):
            _default = {'name': None,
                        'width': 100,
                        'height': 200}

        w1 = Widget(name='Box')
        self.assertEqual(w1.name, 'Box')
        self.assertEqual(w1.width, 100)
        self.assertEqual(w1.height, 200)

        w1.width = 150
        w1.height = 250
        self.assertEqual(w1.width, 150)
        self.assertEqual(w1.height, 250)

        w2 = Widget(name='Rect', width=120)
        self.assertEqual(w2.name, 'Rect')
        self.assertEqual(w2.width, 120)
        self.assertEqual(w2.height, 200)

    def test_class_default2(self):
        class Widget(JsonDict):
            _default = {'name': None,
                        'size' : {'width': 100,
                                  'height': 200}}

        w1 = Widget(name='Box')
        self.assertEqual(w1.name, 'Box')
        self.assertEqual(w1.size.width, 100)
        self.assertEqual(w1.size.height, 200)

        w1.size.width = 150
        w1.size.height = 250
        self.assertEqual(w1.size.width, 150)
        self.assertEqual(w1.size.height, 250)

        w2 = Widget(name='Rect', size__width=120)
        self.assertEqual(w2.name, 'Rect')
        self.assertEqual(w2.size.width, 120)
        self.assertEqual(w2.size.height, 200)

    def test_class_required1(self):
        class Widget(JsonDict):
            _default = {'name': None,
                        'size' : {'width': 100,
                                  'height': 200}}
            _required = ['name']

        def try_create():
            w = Widget()

        self.assertRaises(KeyError, try_create)
        w = Widget(name='Box')
        self.assertEqual(w.name, 'Box')
        
    def test_class_required2(self):
        class Widget(JsonDict):
            _default = {'name': None,
                        'size' : {'width': None,
                                  'height': 200}}
            _required = ['name',
                         'size__width']

        def try_create():
            w = Widget(name='Foo')

        self.assertRaises(KeyError, try_create)
        w = Widget(name='Box', size__width=100)
        self.assertEqual(w.name, 'Box')
        self.assertEqual(w.size.width, 100)
        self.assertEqual(w.size.height, 200)

if __name__ == '__main__':
    unittest.main()
