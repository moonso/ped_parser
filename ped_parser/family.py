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

from __future__ import print_function, unicode_literals

import sys
import os
import logging
import click

from ped_parser.exceptions import PedigreeError

class Family(object):
    """Base class for the family parsers."""
    def __init__(self, family_id, individuals = {}, models_of_inheritance=set([]),
                logger=None, logfile=None, loglevel=None):
        super(Family, self).__init__()
        
        self.logger = logging.getLogger(__name__)
        
         # This is a dict with individual objects
        self.individuals = individuals
        self.family_id = family_id
        # List of models of inheritance that should be prioritized.
        self.models_of_inheritance = models_of_inheritance 
        self.trios = [] #Trios are a list of sets with trios.
        self.duos = [] #Duos are a list of sets with trios.
        self.no_relations = True
        self.affected_individuals = set() # Set of affected individual id:s
    
    def family_check(self):
        """
        Check if the family members break the structure of the family. 
        eg. nonexistent parent, wrong sex on parent etc. 
        Also extracts all trios found, this is of help for many at the moment 
        since GATK can only do phasing of trios and duos."""
        #TODO Make some tests for these
        self.logger.info("Checking family relations for {0}".format(
            self.family_id)
        )
        for individual_id in self.individuals:
            self.logger.debug("Checking individual {0}".format(individual_id))
            individual = self.individuals[individual_id]
            if individual.affected:
                self.logger.debug("Found affected individuals {0}".format(
                    individual_id)
                )
                self.affected_individuals.add(individual_id)
            
            father = individual.father
            mother = individual.mother
            
            if individual.has_parents:
                self.no_relations = False
                try:
                    self.check_parent(father, father=True)
                    self.check_parent(mother, father=False)
                except PedigreeError as e:
                    self.logger.error(e.message)
                    raise e
                # Check if there is a trio
                if individual.has_both_parents:
                    self.trios.append(set([individual_id, father, mother]))
                elif father != '0':
                    self.duos.append(set([individual_id, father]))
                else:
                    self.duos.append(set([individual_id, mother]))
                # self.check_grandparents(individual)
            # Annotate siblings:
            for individual_2_id in self.individuals:
                if individual_id != individual_2_id:
                    if self.check_siblings(individual_id, individual_2_id):
                        individual.siblings.add(individual_2_id)
    
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
                raise PedigreeError(self.family_id, parent_id, 
                                    'Parent is not in family.')
            if father:
                if self.individuals[parent_id].sex != 1:
                    raise PedigreeError(self.family_id, parent_id, 
                                        'Father is not specified as male.')
            else:
                if self.individuals[parent_id].sex != 2:
                    raise PedigreeError(self.family_id, parent_id, 
                                        'Mother is not specified as female.')
        return
    
    def check_siblings(self, individual_1_id, individual_2_id):
        """Check if two family members that are siblings.
            
            Input: Two individual id:s (individual_1_id, individual_2_id)
            
            Returns: True if the individuals are related
                     False if they are not related
        """
        
        ind_1 = self.individuals[individual_1_id]
        ind_2 = self.individuals[individual_2_id]
        if ((ind_1.father != '0' and ind_1.father == ind_2.father) or 
            (ind_1.mother != '0' and ind_1.mother == ind_2.mother)):
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
        if individual_object.family != self.family_id:
            raise PedigreeError(self.family, individual_object.individual_id,
                "Family id of individual is not the same as family id for "\
                                    "Family object!")
        else:
            self.individuals[individual_object.individual_id] = individual_object
        return
    
    def get_phenotype(self, individual_id):
        """Return the phenotype of an individual or 0 if nonexisting individual."""
        phenotype = 0 # This is if unknown phenotype
        if individual_id in self.individuals:
            phenotype = self.individuals[individual_id].phenotype
        
        return phenotype
    
    def get_trios(self):
        """Print the trios found as pedigree files"""
        return self.trios
    
    def to_ped(self, outfile=None):
        """Print the individuals of the family in ped format"""
        for individual in self.individuals:
            ped_line = self.individuals[individual].get_ped()
            if outfile:
                outfile.write(ped_line+'\n')
            else:
                print(ped_line)
    
    def __repr__(self):
        return "Family(family_id={0}, individuals={1}, " \
                "models_of_inheritance={2}".format(
                    self.family_id, self.individuals.keys(), 
                    self.models_of_inheritance
                    )
        
    def __str__(self):
        """Print the family members of this family"""
        family = list(self.individuals.keys())
        return "\t".join(family)

@click.command()
@click.option('-o', '--outfile',
                type=click.File('a')
                )
def cli(outfile):
    from ped_parser.individual import Individual
    proband = Individual('proband', family='1', mother='mother', father='father',sex='1',phenotype='2')
    mother = Individual('mother', family='1', mother='0', father='0',sex='2',phenotype='1')
    father = Individual('father', family='1', mother='0', father='0',sex='1',phenotype='1')
    my_family = Family(family_id='1')
    my_family.add_individual(proband)
    my_family.add_individual(mother)
    my_family.add_individual(father)
    my_family.to_ped(outfile)
    # print(repr(proband))


if __name__ == '__main__':
    cli()
