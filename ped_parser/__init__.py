# -*- coding: utf-8 -*-
from __future__ import print_function

import logging

logger = logging.getLogger(__name__)
__version__ = '1.6.3'

from ped_parser.individual import Individual
from ped_parser.family import Family
from ped_parser.parser import FamilyParser
from ped_parser.log import init_log

