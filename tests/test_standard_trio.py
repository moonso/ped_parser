#!/usr/bin/env python
# encoding: utf-8
"""
test_standard_trio.py

Test the family parser when everything is correct.

#Standard trio
#FamilyID       SampleID        Father  Mother  Sex     Phenotype
healthyParentsAffectedSon       proband father  mother  1       2
healthyParentsAffectedSon       mother  0       0       2       1
healthyParentsAffectedSon       father  0       0       1       1

Should run through smoothely...

Created by Måns Magnusson on 2014-05-08.
Copyright (c) 2014 __MyCompanyName__. All rights reserved.
"""

import sys
import os
from tempfile import NamedTemporaryFile
from ped_parser import parser


class TestTrio(object):
    """Test class for testing how the individual class behave"""
    
    def setup_class(self):
        """Setup a standard trio."""
        trio_lines = ['#Standard trio\n', 
                    '#FamilyID\tSampleID\tFather\tMother\tSex\tPhenotype\n', 
                    'healthyParentsAffectedSon\tproband\tfather\tmother\t1\t2\n',
                    'healthyParentsAffectedSon\tmother\t0\t0\t2\t1\n', 
                    'healthyParentsAffectedSon\tfather\t0\t0\t1\t1\n'
                    ]
        self.trio_file = NamedTemporaryFile(mode='w+t', delete=False, suffix='.vcf')
        self.trio_file.writelines(trio_lines)
        self.trio_file.seek(0)
        self.trio_file.close()
        
    
    def test_standard_trio(self):
        """Test if the file is parsed in a correct way."""
        family_parser = parser.FamilyParser(open(self.trio_file.name, 'r'))
        assert family_parser.header == [
                                    'family_id', 
                                    'sample_id', 
                                    'father_id', 
                                    'mother_id', 
                                    'sex', 
                                    'phenotype'
                                    ]
        assert 'healthyParentsAffectedSon' in family_parser.families
        assert set(['proband', 'mother', 'father']) == set(family_parser.families['healthyParentsAffectedSon'].individuals.keys())
        assert set(['proband', 'mother', 'father']) == set(family_parser.families['healthyParentsAffectedSon'].trios[0])


def main():
    pass


if __name__ == '__main__':
    main()

