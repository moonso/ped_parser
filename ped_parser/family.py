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

from __future__ import print_function
from __future__ import unicode_literals


import sys
import os

class Family(object):
    """Base class for the family parsers."""
    def __init__(self, family_id, individuals = {}, models_of_inheritance=['NA']):
        super(Family, self).__init__()
        self.individuals = individuals # This is a dict with individual objects
        self.family_id = family_id
        self.models_of_inheritance = models_of_inheritance # List of models of inheritance that should be prioritized.
        self.trios = [] #Trios are a list of sets with trios.
        self.duos = [] #Duos are a list of sets with trios.
        self.no_relations = True
        self.affected_individuals = set() # Set of affected individual id:s
    
    def family_check(self):
        """Check if the family members break the structure of the family in any way, eg. nonexistent parent, 
            wrong sex on parent... Also extracts all trios found, this i of help for many at the moment since 
            GATK can only do phasing of trios and duos."""
        #TODO Make some tests for these
        for individual in self.individuals:
            
            if self.individuals[individual].affected:
                self.affected_individuals.add(individual)
            
            father = self.individuals[individual].father
            mother = self.individuals[individual].mother
            if self.individuals[individual].has_parents:
                self.no_relations = False
                self.check_parent(father, father=True)
                self.check_parent(mother, father=False)
                # Check if there is a trio
                if self.individuals[individual].has_both_parents:
                    self.trios.append(set([individual, father, mother]))
                elif father != '0':
                    self.duos.append(set([individual, father]))
                else:
                    self.duos.append(set([individual, mother]))
                # self.check_grandparents(individual)
            # Annotate siblings:
            for individual_2 in self.individuals:
                if individual != individual_2:
                    if self.check_siblings(individual, individual_2):
                        self.individuals[individual].siblings.add(individual_2)
    
    def check_parent(self, parent_id, father = False):
        """Check if the parent info is correct. If an individual is not present in file raise exeption.
            
            Input: An id that represents a parent
                   father = True/False
            
            Raises SyntaxError if
                    The parent id is not present
                    The gender of the parent is wrong.
        """
        
        if parent_id != '0':
            if parent_id not in self.individuals:
                raise SyntaxError('Parent %s is not in family.' % parent_id)
            if father:
                if self.individuals[parent_id].sex != 1:
                    raise SyntaxError('Father %s is not specified as male.' % parent_id)
            else:
                if self.individuals[parent_id].sex != 2:
                    raise SyntaxError('Mother %s is not specified as female.' % parent_id)
        return
    
    def check_siblings(self, individual_1, individual_2):
        """Check if two family members that are siblings.
            
            Input: Two individual id:s (individual_1, individual_2)
            
            Returns: True if the individuals are related
                     False if they are not related
        """
        
        if ((self.individuals[individual_1].father != '0' and 
                self.individuals[individual_1].father == self.individuals[individual_2].father) or 
            (self.individuals[individual_2].mother != '0' and 
                self.individuals[individual_1].mother == self.individuals[individual_2].mother)):
            return True
        else:
            return False
    
    def check_cousins(self, individual_1, individual_2):
        """Check which family members that are cousins. 
            If two individuals share any grandparents they are cousins.
            
            Input: Two individuals
            
            Returns: True if they share any grandparents
                     False if not.
        """
        #TODO check if any of the parents are siblings
        pass
    
    def add_individual(self, individual_object):
        """Add an individual to the family.
            
            Input: An individual object
                
                Adds the individual object to the family.
        """
        
        self.individuals[individual_object.individual_id] = individual_object
        return
    
    def get_phenotype(self, individual_id):
        """Return the phenotype of an individual or 0 if nonexisting individual."""
        phenotype = 0 # This is if unknown phenotype
        if individual_id in self.individuals:
            phenotype = self.individuals[individual_id].phenotype
        return phenotype
    
    def print_trios(self):
        """Print the trios found as pedigree files"""
        for trio in self.trios:
            print(trio)
    
    def __str__(self):
        """Print the family members of this family"""
        family = list(self.individuals.keys())
        return "\t".join(family)


def main():
    pass


if __name__ == '__main__':
    main()
