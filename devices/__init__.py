# Licence: GNU General Public License version 2 (GPLv2)
# (C) 2019-2021 Matthias H. Richter

import os
import importlib

available_driver = []

for module in os.listdir(os.path.dirname(__file__)):
    if module == '__init__.py' or module[-3:] != '.py':
        continue
    available_driver.append(module[4:-3])
    importlib.import_module('.%s' % module[:-3], package=__name__)
del module

