#!/usr/bin/env python
# encoding: utf-8
"""
family.py

Holds the meta information of a family and its individuals.

    - has a Individual

Attributes:

individuals DICT dictionary with family members on the form {<ind_id>:<Individual_obj>}
variants DICT dictionary with all the variants that exists in the family on the form {<var_id>:<Variant_obj>}

    
Methods:

    - print_individuals
    - print_all_variants
    - add_variant(attach a variant objekt and also a variant id to individuals)


Created by Måns Magnusson on 2014-02-05.
Copyright (c) 2014 __MyCompanyName__. All rights reserved.
"""

import sys
import os
if sys.version_info < (2, 7):
    from ordereddict import OrderedDict
else:
    from collections import OrderedDict


class Family(object):
    """Base class for the family parsers."""
    def __init__(self, family_id, individuals = [], models_of_inheritance=['NA']):
        super(Family, self).__init__()
        self.individuals = individuals # This is a list with individual objects
        self.family_id = family_id
        self.models_of_inheritance = models_of_inheritance # List of models of inheritance that should be prioritized.
    
    def family_check(self):
        """Check if the family members break the structure of the family in any way, eg. nonexistent parent, wrong sex on parent..."""
        #TODO Make some tests for these
        pass
    
    def check_siblings(self):
        """Check which family members that are siblings."""
        pass
    
    def check_cousins(self):
        """Check which family members that are cousins"""
        pass
    
    def add_individual(self, individual_object):
        """Add an individual to the family."""
        self.individuals.append(individual_object)
    
    def get_phenotype(self, ind_id):
        """Return the phenotype of an individual or 0 if nonexisting individual."""
        phenotype = 0 # This is if unknown phenotype
        for individual in self.individuals:
            if ind_id == individual.individual_id:
                phenotype = individual.phenotype
        return phenotype
    
    def __str__(self):
        """Print the family members of this family"""
        family = [individual.individual_id for individual in self.individuals]
        return "\t".join(family)


def main():
    pass


if __name__ == '__main__':
    main()
