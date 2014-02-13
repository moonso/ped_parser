#!/usr/bin/env python
# encoding: utf-8
"""
Individual.py

Holds the information of an individual

Attributes:

ind STRING Can be any id unique within the family
family STRING Can be any unique id within the cohort
mother STRING The ind_id of the mother or [0,-9] if info is missing
father STRING ---------||------ father --------------||---------------
sex INT 1=male 2=female 0=unknown
phenotype INT 1=unaffected, 2=affected, missing = [0,-9]
genotypes DICT Container with genotype information on the form {<variant_id>: <Genotype>}
phasing BOOL If the genotype information includes phasing for this individual

Created by Måns Magnusson on 2012-10-31.
Copyright (c) 2012 __MyCompanyName__. All rights reserved.
"""

import sys
import os


class Individual(object):
    """docstring for Individual"""
    def __init__(self, ind, family='0', mother='0', father='0',sex='0',phenotype='0'):
        
        #TODO write test to throw exceptions if malformed input.
        
        self.individual_id = ind #Individual Id STRING
        self.family = family #Family Id STRING
        self.mother = mother #Mother Id STRING
        self.father = father # Father Id STRING
        self.sex = int(sex) # Sex Integer
        self.phenotype = int(phenotype) # Phenotype INTEGER 
        self.phasing = False # If we have phasing info for this individual BOOL
        
        if self.mother == '0' and self.father == '0':
            self.has_parents = False
        else:
            self.has_parents = True
        
        self.siblings = {}
        self.grandparents = {}
        self.first_cousins = {}
        self.second_cousins = {}
            
    def affected(self):
        """Returns true is affected and false if healthy or unknown(?)"""
        if self.phenotype == 2:
            return True
        else:
            return False
    
    def check_grandparents(self, mother = None, father = None):
        """Check if there are any grand parents."""
        if mother:
            if mother.mother != '0':
                self.grandparents[mother.mother] =  ''
            elif mother.father != '0':
                self.grandparents[mother.father] = ''
        if father:
            if father.mother != '0':
                self.grandparents[father.mother] =  ''
            elif father.father != '0':
                self.grandparents[father.father] = ''
        return
    
    def check_relations(self, individual):
        """Check the relations that this individual have eith another individual."""
        if (self.mother == individual.mother) or (self.father == individual.father):
            self.siblings[individual.individual_id] = ''
            individual.siblings[individual_id] = ''
            return
        
        # TODO write checks for the other types
    
    def __str__(self):
        """Returns what should be printed if object is printed."""
        ind_info = ['ind:', self.individual_id, 'family:', self.family, 'mother:', self.mother, 'father:', self.father,
                     'sex:', str(self.sex), 'phenotype:', str(self.phenotype)]
        return ' '.join(ind_info)

def main():
    pass


if __name__ == '__main__':
    main()

