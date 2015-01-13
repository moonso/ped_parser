#!/usr/bin/env python
# encoding: utf-8
"""
test_standard_trio extra daughter.py

Test the family parser when everything is correct.

#Standard trio
#FamilyID       SampleID        Father  Mother  Sex     Phenotype
healthyParentsAffectedSon       proband father  mother  1       2
healthyParentsAffectedSon       mother  0       0       2       1
healthyParentsAffectedSon       father  0       0       1       1
healthyParentsAffectedSon       daughter father  mother  2       1

Should run through smoothely...

Created by Måns Magnusson on 2014-05-08.
Copyright (c) 2014 __MyCompanyName__. All rights reserved.
"""

import sys
import os
from tempfile import NamedTemporaryFile
from ped_parser import FamilyParser


class TestIndividual(object):
    """Test class for testing how the individual class behave"""
    
    def setup_class(self):
        """Setup a standard trio."""
        trio_lines = ['#Standard trio\n', 
                    '#FamilyID\tSampleID\tFather\tMother\tSex\tPhenotype\n', 
                    'healthyParentsAffectedSon\tproband\tfather\tmother\t1\t2\n',
                    'healthyParentsAffectedSon\tmother\t0\t0\t2\t1\n', 
                    'healthyParentsAffectedSon\tfather\t0\t0\t1\t1\n',
                    'healthyParentsAffectedSon\tdaughter\tfather\tmother\t2\t1\n',
                    ]
        self.trio_file = NamedTemporaryFile(mode='w+t', delete=False, suffix='.vcf')
        self.trio_file.writelines(trio_lines)
        self.trio_file.seek(0)
        self.trio_file.close()
        
    
    def test_standard_trio_extra_daughter(self):
        """Test if the file is parsed in a correct way."""
        family_parser = FamilyParser(self.trio_file.name)
        trio_family = family_parser.families['healthyParentsAffectedSon']
        
        assert family_parser.header == [
                                    'family_id', 
                                    'sample_id', 
                                    'father_id', 
                                    'mother_id', 
                                    'sex', 
                                    'phenotype'
                                ]
        assert set(['proband', 'mother', 'father', 'daughter']) == set(family_parser.families['healthyParentsAffectedSon'].individuals.keys())
        assert set(['proband', 'mother', 'father']) in trio_family.trios
        assert set(['daughter', 'mother', 'father']) in trio_family.trios
        assert 'daughter' in trio_family.individuals['proband'].siblings
        


def main():
    pass


if __name__ == '__main__':
    main()

