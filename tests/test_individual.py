#!/usr/bin/env python
# encoding: utf-8
"""
test_indivdual.py

Test the individual class.

Created by Måns Magnusson on 2013-03-07.
Copyright (c) 2013 __MyCompanyName__. All rights reserved.
"""

import sys
import os
from ped_parser import individual


class TestIndividual(object):
    """Test class for testing how the individual class behave"""
    
    def setup_class(self):
        """Setup a simple family with family id 1, sick daughter id 1, healthy father id 2, healthy mother id 3"""
        self.daughter = individual.Individual(
                                            ind='1', 
                                            family='1', 
                                            mother='3', 
                                            father='2', 
                                            sex=2, 
                                            phenotype=2
                                        )
        self.father = individual.Individual(
                                            ind='2', 
                                            family='1', 
                                            mother='0', 
                                            father='0', 
                                            sex=1, 
                                            phenotype=1
                                        )
        self.mother = individual.Individual(
                                            ind='3', 
                                            family='1', 
                                            mother='0', 
                                            father='0', 
                                            sex=2, 
                                            phenotype=1
                                        )
        self.random_individual = individual.Individual(ind='0')
    
    def test_daughter(self):
        """Test if the information about the daughter comes out correctly."""
        assert self.daughter.affected
        assert self.daughter.has_parents
        assert self.daughter.sex == 2
    
    def test_father(self):
        """Test if the information about the father comes out correctly."""
        assert not self.father.affected
        assert not self.father.has_parents
        assert self.father.sex == 1
    
    def test_mother(self):
        """Test if the information about the mother comes out correctly."""
        assert not self.mother.affected
        assert not self.mother.has_parents
        assert self.mother.sex == 2
    
    def test_random_individual(self):
        """Test if the information about the father comes out correctly."""
        assert not self.random_individual.affected
        assert not self.random_individual.has_parents
        assert self.random_individual.sex == 0
    


def main():
    pass


if __name__ == '__main__':
    main()

