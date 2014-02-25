#!/usr/bin/env python
# encoding: utf-8
"""
test_family.py

Tests for the family class

Created by Måns Magnusson on 2013-03-13.
Copyright (c) 2013 __MyCompanyName__. All rights reserved.
"""

import sys
import os
from ped_parser import family, individual



class TestFamily(object):
    """Test class for testing how the individual class behave"""
    
    def setup_class(self):
        """Setup a simple family with family id 1, sick daughter id 1, healthy father id 2, healthy mother id 3"""
        # Create a family
        self.family = family.Family(family_id = '1') 
        # Create a sick daughter:
        self.daughter = individual.Individual(ind = '1', family = '1', mother = '3', father = '2', sex = 2, phenotype = 2)
        # Create a healthy son:
        self.son = individual.Individual(ind = '4', family = '1', mother = '3', father = '2', sex = 1, phenotype = 1)        
        # Create a healthy father 
        self.father = individual.Individual(ind = '2', family = '1', mother = '0', father = '0', sex = 1, phenotype = 1)
        # Create a healthy mother
        self.mother = individual.Individual(ind = '3', family = '1', mother = '0', father = '0', sex = 2, phenotype = 1)
        self.family.add_individual(self.daughter)
        self.family.add_individual(self.son)
        self.family.add_individual(self.father)
        self.family.add_individual(self.mother)
        self.family.family_check()
    
    def test_individuals(self):
        """Test if all individuals are at place"""
        assert self.daughter.individual_id in self.family.individuals
        assert self.son.individual_id in self.family.individuals
        assert self.mother.individual_id in self.family.individuals
        assert self.father.individual_id in self.family.individuals
        assert not '5' in self.family.individuals

    def test_family_relations(self):
        """Test if the family reöations are correct"""
        assert self.daughter.individual_id in self.son.siblings
        assert self.son.individual_id in self.daughter.siblings
        # Mother and father should not be siblings in this case:
        assert not self.father.individual_id in self.mother.siblings


def main():
    pass


if __name__ == '__main__':
    main()

