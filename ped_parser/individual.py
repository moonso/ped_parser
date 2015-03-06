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

from __future__ import print_function
from __future__ import unicode_literals


import sys
import os


class Individual(object):
    """docstring for Individual"""
    def __init__(self, ind, family='0', mother='0', father='0',sex='0',phenotype='0',
        genetic_models=None, proband='.', consultand='.', alive='.'):
        
        #TODO write test to throw exceptions if malformed input.
        
        self.individual_id = ind #Individual Id STRING
        self.family = family #Family Id STRING
        self.mother = mother #Mother Id STRING
        self.father = father # Father Id STRING
        
        self.affected = False
        self.healthy = False
        self.extra_info = {}
        
        # For madeline:
        self.proband = proband
        self.consultand = consultand
        self.alive = alive
        
        try:
            self.sex = int(sex) # Sex Integer
            self.phenotype = int(phenotype) # Phenotype INTEGER 
        except ValueError:
            raise SyntaxError('Sex and phenotype have to be integers.')
            
        self.has_parents = False
        self.has_both_parents = False
        
        if self.mother != '0':
            self.has_parents = True
            if self.father != '0':
                self.has_both_parents = True
        elif self.father != '0':
            self.has_parents = True
        
        # These features will be added
        #TODO make use of family relations:
        self.siblings = set()
        self.grandparents = set()
        self.first_cousins = set()
        self.second_cousins = set()
        
        if self.phenotype == 2:
            self.affected = True
        elif self.phenotype == 1:
            self.healthy = True
            
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
    
    def get_ped(self):
        """Return the individual info in a ped formatted string."""
        return "{0}\t{1}\t{2}\t{3}\t{4}\t{5}".format(
            self.family, self.individual_id, self.father, self.mother,
            self.sex, self.phenotype
        )
    
    def get_json(self):
        """Return the individual info in a dictionary for json."""
        individual_info = {
            'family_id': self.family,
            'id':self.individual_id, 
            'sex':str(self.sex), 
            'phenotype': str(self.phenotype), 
            'mother': self.mother, 
            'father': self.father
        }
        return individual_info
    
    def get_madeline(self):
        """Return the individual info in a madeline formated string"""
        #Convert sex to madeleine type
        if self.sex == 1:
            madeline_gender = 'M'
        elif self.sex == 2:
            madeline_gender = 'F'
        else:
            madeline_gender = '.'
        #Convert father to madeleine type
        if self.father == '0':
            madeline_father = '.'
        else:
            madeline_father = self.father
        #Convert mother to madeleine type
        if self.mother == '0':
            madeline_mother = '.'
        else:
            madeline_mother = self.mother
        #Convert phenotype to madeleine type
        if self.phenotype == 1:
            madeline_phenotype = 'U'
        elif self.phenotype == 2:
            madeline_phenotype = 'A'
        else:
            madeline_phenotype = '.'
        
        return "{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}".format(
            self.family, self.individual_id, madeline_gender, 
            madeline_father, madeline_mother, madeline_phenotype,
            self.proband, self.consultand, self.alive
        )
    def __repr__(self):
        return "Individual(individual_id={0}, family={1}, mother={2}, " \
                "father={3}, sex={4}, phenotype={5})".format(
                    self.individual_id, self.family, self.mother, self.father,
                    self.sex, self.phenotype
                )
    
    def __str__(self):
        """Returns what should be printed if object is printed."""
        ind_info = ['ind_id:', self.individual_id, 
                    'family:', self.family, 
                    'mother:', self.mother, 
                    'father:', self.father,
                    'sex:', str(self.sex), 
                    'phenotype:', str(self.phenotype),
                    ]
        if len(self.siblings) > 0:
            ind_info.append('siblings:')
            ind_info.append(','.join(self.siblings))
        
        return ' '.join(ind_info)

def main():
    pass


if __name__ == '__main__':
    main()

