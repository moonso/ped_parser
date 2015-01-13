#!/usr/bin/env python
# encoding: utf-8
"""
test_standard_trio_extra_col_for_son.py

Test the family parser when an extra column is missing.

FAM file looks like:

#Standard trio
#FamilyID       SampleID        Father  Mother  Sex     Phenotype
healthyParentsAffectedSon       proband father  mother  0       1       2
healthyParentsAffectedSon       mother  0       0       2       1
healthyParentsAffectedSon       father  0       0       1       1

Should raise exception since there is an extra columnn in the proband line.

Created by Måns Magnusson on 2014-05-08.
Copyright (c) 2014 __MyCompanyName__. All rights reserved.
"""

import sys
import os
from tempfile import NamedTemporaryFile
import pytest
from ped_parser import parser


class TestIndividual(object):
    """Test class for testing how the individual class behave"""
    
    def setup_class(self):
        """Setup a standard trio with extra column in the 'proband' row."""
        trio_lines = ['#Standard trio\n', 
                    '#FamilyID\tSampleID\tFather\tMother\tSex\tPhenotype\n', 
                    'healthyParentsAffectedSon\tproband\tfather\tmother\t0\t1\t2\n',
                    'healthyParentsAffectedSon\tmother\t0\t0\t2\t1\n', 
                    'healthyParentsAffectedSon\tfather\t0\t0\t1\t1\n'
                    ]
        self.trio_file = NamedTemporaryFile(mode='w+t', delete=False, suffix='.vcf')
        self.trio_file.writelines(trio_lines)
        self.trio_file.seek(0)
        self.trio_file.close()
        
    
    def test_standard_trio_proband_extra_column(self):
        """Test if the file is parsed in a correct way."""
        with pytest.raises(SystemExit):
            family_parser = parser.FamilyParser(self.trio_file.name)


def main():
    pass


if __name__ == '__main__':
    main()

