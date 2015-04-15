#!/usr/bin/env python
# encoding: utf-8
"""
family.py

Holds the meta information of a family and its individuals.

    - has a Individual

Attributes:

individuals DICT dictionary with family members on the form {<ind_id>:<Individual_obj>}
variants DICT dictionary with all the variants that exists in the family on the form {<var_id>:<Variant_obj>}


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

        self.family_id = family_id
        self.logger.info("Initiating family with id:{0}".format(self.family_id))
         # This is a dict with individual objects
        self.individuals = individuals
        self.logger.info("Adding individuals:{0}".format(
            ','.join([ind for ind in self.individuals])
        ))
        # List of models of inheritance that should be prioritized.
        self.models_of_inheritance = models_of_inheritance 
        self.logger.info("Adding models of inheritance:{0}".format(
            ','.join(self.models_of_inheritance)
        ))
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
            self.logger.debug("Checking if individual {0} is affected".format(
                individual_id))
            if individual.affected:
                self.logger.debug("Found affected individual {0}".format(
                    individual_id)
                )
                self.affected_individuals.add(individual_id)
            
            father = individual.father
            mother = individual.mother
            
            if individual.has_parents:
                self.logger.debug("Individual {0} has parents".format(
                    individual_id))
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
                    # elif self.check_cousins(individual_id, individual_2_id):
                    #     individual.cousins.add(individual_2_id)
    
    def check_parent(self, parent_id, father = False):
        """Check if the parent info is correct. If an individual is not present in file raise exeption.
            
            Input: An id that represents a parent
                   father = True/False
            
            Raises SyntaxError if
                    The parent id is not present
                    The gender of the parent is wrong.
        """
        self.logger.info("Checking parent {0}".format(parent_id))
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
        """
        Check if two family members that are siblings.
        
        Arguments: 
            individual_1_id (str): The id of an individual
            individual_2_id (str): The id of an individual
        
        Returns: 
            bool : True if the individuals are siblings
                   False if they are not siblings
        """
        
        self.logger.info("Checking if {0} and {1} are siblings".format(
            individual_1_id, individual_2_id
        ))
        ind_1 = self.individuals[individual_1_id]
        ind_2 = self.individuals[individual_2_id]
        if ((ind_1.father != '0' and ind_1.father == ind_2.father) or 
            (ind_1.mother != '0' and ind_1.mother == ind_2.mother)):
            return True
        else:
            return False
    
    def check_cousins(self, individual_1_id, individual_2_id):
        """
        Check if two family members are cousins.
        
        If two individuals share any grandparents they are cousins.
        
        Arguments: 
            individual_1_id (str): The id of an individual
            individual_2_id (str): The id of an individual
        
        Returns: 
            bool : True if the individuals are cousins
                   False if they are not cousins
        
        """
        self.logger.info("Checking if {0} and {1} are cousins".format(
            individual_1_id, individual_2_id
        ))
        
        #TODO check if any of the parents are siblings
        pass
    
    def add_individual(self, individual_object):
        """
        Add an individual to the family.
        
        Arguments:
            individual_object (Individual)
            
        """
        ind_id = individual_object.individual_id
        self.logger.info("Trying to add {0}".format(ind_id))
        family_id = individual_object.family
        if family_id != self.family_id:
            raise PedigreeError(self.family, individual_object.individual_id,
                "Family id of individual is not the same as family id for "\
                                    "Family object!")
        else:
            self.individuals[ind_id] = individual_object
            self.logger.info("Added individual {0} to family {1}".format(
                ind_id, family_id
            ))
        return
    
    def get_phenotype(self, individual_id):
        """
        Return the phenotype of an individual
        
        If individual does not exist return 0
        
        Arguments:
            individual_id (str): Represents the individual id
        
        Returns:
            int : Integer that represents the phenotype
        """
        phenotype = 0 # This is if unknown phenotype
        if individual_id in self.individuals:
            phenotype = self.individuals[individual_id].phenotype
        
        return phenotype
    
    def get_trios(self):
        """
        Return the trios found in family
        """
        return self.trios
    
    def to_json(self):
        """
        Return the family in json format.
        
        The family will be represented as a list with dictionarys that
        holds information for the individuals.
        
        Returns:
            list : A list with dictionaries
        """
        
        return [self.individuals[ind].to_json() for ind in self.individuals]
    
    def to_ped(self, outfile=None):
        """
        Print the individuals of the family in ped format
        
        The header will be the original ped header plus all headers found in
        extra info of the individuals
        """
        
        ped_header = [
            '#FamilyID',
            'IndividualID',
            'PaternalID',
            'MaternalID', 
            'Sex',
            'Phenotype',
        ]
        
        extra_headers = [
            'InheritanceModel',
            'Proband',
            'Consultand',
            'Alive'
        ]
        
        for individual_id in self.individuals:
            individual = self.individuals[individual_id]
            for info in individual.extra_info:
                if info in extra_headers:
                    if info not in ped_header:
                        ped_header.append(info)
        
        self.logger.info("Ped headers found: {0}".format(
            ', '.join(ped_header)
        ))
        
        if outfile:
            outfile.write('\t'.join(ped_header)+'\n')
        else:
            print('\t'.join(ped_header))
        
        for individual in self.to_json():
            ped_info = []
            ped_info.append(individual['family_id'])
            ped_info.append(individual['id'])
            ped_info.append(individual['father'])
            ped_info.append(individual['mother'])
            ped_info.append(individual['sex'])
            ped_info.append(individual['phenotype'])
            
            if len(ped_header) > 6:
                for header in ped_header[6:]:
                    ped_info.append(individual['extra_info'].get(header, '.'))
            
            if outfile:
                outfile.write('\t'.join(ped_info)+'\n')
            else:
                print('\t'.join(ped_info))
    
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
    proband.extra_info['Proband'] = 'Yes'
    my_family = Family(family_id='1')
    my_family.add_individual(proband)
    my_family.add_individual(mother)
    my_family.add_individual(father)
    my_family.to_ped(outfile)
    # print(repr(proband))


if __name__ == '__main__':
    from ped_parser import logger
    from ped_parser import init_log
    init_log(logger, loglevel="DEBUG")
    cli()
