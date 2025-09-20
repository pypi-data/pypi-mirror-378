# check for typos

import importlib
import os
from unittest import TestCase
import warnings
from zabbix_enums.z50 import *
from zabbix_enums.z52 import *
from zabbix_enums.z54 import *
from zabbix_enums.z60 import *
from zabbix_enums.z62 import *
from zabbix_enums.z64 import *
from zabbix_enums.z70 import *
from zabbix_enums.z72 import *
from zabbix_enums.z74 import *


# class TestImports(TestCase):

#     def setUp(self) -> None:
#         self.versions = filter(
#             lambda x: '.py' not in x,
#             os.listdir(os.path.join(os.path.dirname(__file__), '..', 'src', 'zabbix_enums'))
#         )
#         return super().setUp()
#     def test_wildcard_warning(self):
#         for version in self.versions:
#             with warnings.catch_warnings(record=True) as w:
#                 warnings.simplefilter("always")
#                 importlib.reload(importlib.import_module(f'zabbix_enums.{version}'))
#                 self.assertTrue(
#                     any(f"Wildcard import from 'zabbix_enums.{version}'" in str(warn.message) for warn in w),
#                     f"No warning for {version} wildcard import"
#                 )


#     def test_no_wildcard_warning_on_submodule_import(self):
#         for version in self.versions:
#             with warnings.catch_warnings(record=True) as w:
#                 warnings.simplefilter("always")
#                 module = importlib.import_module(f'zabbix_enums.{version}.host')
#                 _ = getattr(module, "HostStatus", None)
#                 self.assertFalse(
#                     any(f"Wildcard import from 'zabbix_enums.{version}'" in str(warn.message) for warn in w),
#                     f"Unexpected wildcard import warning for submodule import in {version}"
#                 )