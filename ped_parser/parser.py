#!/usr/bin/env python
# encoding: utf-8
"""
parser.py


Parse a file with family info, this can be a .ped file, a .fam, a .txt(CMMS style) 
file or a .txt(Broad style) file or another ped based alternative.

.ped and .fam always have 6 columns, these are

Family_ID - '.' or '0' for unknown
Individual_ID - '.' or '0' for unknown
Paternal_ID - '.' or '0' for unknown
Maternal_ID - '.' or '0' for unknown
Sex - '1'=male; '2'=female; ['other', '0', '.']=unknown
Phenotype - '1'=unaffected, '2'=affected, ['-9', '0', '.']= missing, 

The other types must specify the columns in the header.
Header allways start with '#'.
These files allways start with the ped columns described above.

The following column names will be treated with care, which means that they will be used when outputting a madeline type of file or makes accesable variables in the parser:

'InheritanceModel' - a ';'-separated list of expected inheritance models. 
Choices are: 
['AR','AR_hom','AR_denovo','AR_hom_denovo','AR_hom_dn','AR_dn','AR_compound','AR_comp','AD','AD_dn','AD_denovo','X','X_dn','X_denovo','NA','Na','na','.']

'Proband' - 'Yes', 'No', 'Unknown' or '.'.  A proband is the first affected member of a pedigree coming to medical attention.
'Consultand' - 'Yes', 'No', 'Unknown' or '.'. A consultand is an individual who has sought genetic counseling or testing.
'Alive' - 'Yes', 'No', 'Unknown' or '.'

Create a family object and its family members from different types of input file
Created by Måns Magnusson on 2013-01-17.
Copyright (c) 2013 __MyCompanyName__. All rights reserved.
"""

from __future__ import print_function
from __future__ import unicode_literals

import sys
import os
import argparse
import json

from codecs import open
from string import whitespace
from ped_parser import individual, family
from pprint import pprint as pp

import click

class FamilyParser(object):
    """Parses a file with family info and creates a family object with individuals."""
    def __init__(self, infile, family_type = 'ped', verbose=False):
        super(FamilyParser, self).__init__()
        self.family_type = family_type
        self.verbose = verbose
        self.families = {}
        self.individuals = {}
        self.legal_ar_hom_names = ['AR', 'AR_hom']
        self.legal_ar_hom_dn_names = ['AR_denovo', 'AR_hom_denovo', 'AR_hom_dn', 'AR_dn']
        self.legal_compound_names = ['AR_compound', 'AR_comp']
        self.legal_ad_names = ['AD', 'AD_dn', 'AD_denovo']
        self.legal_x_names = ['X', 'X_dn', 'X_denovo']
        self.legal_na_names = ['NA', 'Na', 'na', '.']
        self.header = ['family_id', 'sample_id', 'father_id', 'mother_id', 'sex', 'phenotype']
        with open(infile, 'r', encoding='utf-8') as family_file:
            line_count = 0
            if self.family_type in ['ped', 'fam']:
                self.ped_parser(family_file)
            elif self.family_type == 'alt':
                self.alternative_parser(family_file)
            elif self.family_type in ['cmms', 'mip']:
                self.alternative_parser(family_file)
            # elif family_type == 'broad':
            #     self.broad_parser(individual_line, line_count)
        for fam in self.families:
            self.families[fam].family_check()
            # print(self.families[family].trios)
            # print(self.families[family].duos)
    
    def get_individual(self, family_id, sample_id, father_id, mother_id, sex, phenotype,
            genetic_models = None, proband='.', consultand='.', alive='.'):
        """Return a individual object based on the indata."""
        if sex not in ['1', '2']:
            sex = '0'
        if phenotype not in ['1', '2']:
            phenotype = '0'
        if mother_id == '.':
            mother_id = '0'
        if father_id == '.':
            father_id = '0'
        if genetic_models:
            genetic_models = genetic_models.split(';')
        
        if proband == 'Yes':
            proband = 'Y'
        elif proband == 'No':
            proband = 'N'
        else:
            proband = '.'
        
        if consultand == 'Yes':
            consultand = 'Y'
        elif consultand == 'No':
            consultand = 'N'
        else:
            consultand = '.'
        
        if alive == 'Yes':
            alive = 'Y'
        elif alive == 'No':
            alive = 'N'
        else:
            alive = '.'
        
        individual_obj = individual.Individual(sample_id, family_id, mother_id, father_id, sex, phenotype,
                        genetic_models, proband, consultand, alive)
        
        return individual_obj
    
    def check_line_length(self, splitted_line, expected_length):
        """Check if the line is correctly formated. Throw a SyntaxError if it is not."""
        if len(splitted_line) != expected_length:
            raise SyntaxError('\nWRONG FORMATED PED LINE!\n')
        return
    
    def ped_parser(self, family_file):
        """Parse a .ped ped file."""
        
        for line in family_file:
            # Check if commented line or empty line:
            if not line.startswith('#') and not all(c in whitespace for c in line.rstrip()):
                splitted_line = line.rstrip().split('\t')
                if len(splitted_line) != 6:
                    # Try to split the line on another symbol:
                    splitted_line = line.rstrip().split()
                try:
                    self.check_line_length(splitted_line, 6)
                except SyntaxError as e:
                    print(e)
                    print("""One of the ped lines have %s number of entrys:\n%s""" % (len(splitted_line), line), file=sys.stderr)
                    print("Ped lines can only have 6 entrys. "
                            "Use flag '--family_type/-t' if you are using an alternative ped file.", file=sys.stderr)
                    sys.exit(1)
                
                sample_dict = dict(zip(self.header, splitted_line))
                
                if sample_dict['family_id'] not in self.families:
                    self.families[sample_dict['family_id']] = family.Family(sample_dict['family_id'], {})
                
                ind_object = self.get_individual(**sample_dict)
                self.individuals[ind_object.individual_id] = ind_object
                self.families[ind_object.family].add_individual(ind_object)
        

    def alternative_parser(self, family_file):
        """This parses a ped file with more than six columns, in that case header comlumn must exist and each row must have the same amount of columns as the header. First six columns must be the same as in the ped format."""
        
        alternative_header = None
        
        for line in family_file:
            if line.startswith('#'):
                alternative_header = line[1:].rstrip().split('\t')
            elif not all(c in whitespace for c in line.rstrip()):
                if not alternative_header:
                    print('Alternative ped files must have headers!')
                    print('Please add a header line.')
                    print('Exiting...')
                    sys.exit(1)
                splitted_line = line.rstrip().split('\t')
                if len(splitted_line) < 6:
                    # Try to split the line on another symbol:
                    splitted_line = line.rstrip().split()
                try:
                    self.check_line_length(splitted_line, len(alternative_header))
                except SyntaxError as e:
                    print(e)
                    print('Number of entrys differ from header.', file=sys.stderr)
                    print('Header:\n%s' % '\t'.join(alternative_header), file=sys.stderr)
                    print('Length of Header: %s' % len(alternative_header), file=sys.stderr)
                    print('Ped Line:\n%s' % '\t'.join(splitted_line), file=sys.stderr)
                    print('Length of Ped line: %s' % len(splitted_line), file=sys.stderr)
                    sys.exit(1)
                if len(line) > 1:
                    
                    sample_dict = dict(zip(self.header, splitted_line[:6]))
                    
                    all_info = dict(zip(alternative_header, splitted_line))
                    
                    if sample_dict['family_id'] not in self.families:
                        self.families[sample_dict['family_id']] = family.Family(sample_dict['family_id'], {})
                    
                    sample_dict['genetic_models'] = all_info.get('InheritanceModel', None)
                    # Try other header naming:
                    if not sample_dict['genetic_models']:
                        sample_dict['genetic_models'] = all_info.get('Inheritance_model', None)
                        
                    sample_dict['proband'] = all_info.get('Proband', '.')
                    sample_dict['consultand'] = all_info.get('Consultand', '.')
                    sample_dict['alive'] = all_info.get('Alive', '.')
                    
                    
                    ind_object = self.get_individual(**sample_dict)
                    
                    self.individuals[ind_object.individual_id] = ind_object
                    self.families[ind_object.family].add_individual(ind_object)
                    
                    if sample_dict['genetic_models']:
                        for model in self.get_models(sample_dict['genetic_models']):
                            self.families[ind_object.family].models_of_inheritance.add(model)
                    
                    # We try is it is an id in the CMMS format:
                    if len(ind_object.individual_id.split('-')) == 3:
                        # If the id follow the cmms conventiion we can
                        # do a sanity check
                        if self.check_cmms_id(ind_object.individual_id):
                            if self.verbose:
                                print('Id follows CMMS convention!', file=sys.stderr)
                            if not self.check_cmms_affection_status(ind_object):
                                sys.exit(1)
                            if not self.check_cmms_gender(ind_object):
                                sys.exit(1)
                                
                    for i in range(6, len(splitted_line)):
                        ind_object.extra_info[alternative_header[i]] = splitted_line[i]
    
    def check_cmms_id(self, ind_id):
        """
        Take the ID and check if it is following the cmms standard.
        The standard is year:id-generation-indcode:affectionstatus.
        Year is two digits, id three digits, generation in roman letters
        indcode are digits and affection status are in ['A', 'U', 'X'].
        Example 11001-II-1A.
        
        Input:
            ind_obj : A individual object
        
        Returns:
            bool    : True if it is correct
        """
        ind_id = ind_id.split('-')
        # This in A (=affected), U (=unaffected) or X (=unknown)
        family_id = ind_id[0]
        try:
            int(family_id)
        except ValueError:
            return False
        affection_status = ind_id[-1][-1]
        try:
            type(affection_status.isalpha())
        except ValueError:
            return False
        
        return True
    
    def check_cmms_affection_status(self, ind_object):
        """
        Check if the affection status is correct.
        
        Args:
            ind_object  : An Individuals object
        
        Returns:
            bool : True if affection status is correct
                    False otherwise
        """
        ind_id = ind_object.individual_id.split('-')
        phenotype = ind_object.phenotype
        affection_status = ind_id[-1][-1]
        if affection_status not in ['A', 'U', 'X']:
            print('Wrong affection status %s' 
                    % ind_object.individual_id, file=sys.stderr)
            print("Affection status can be ['A', 'U', 'X']")
            print('Exiting ...', file=sys.stderr)
            return False
        
        if (affection_status == 'A' and phenotype != 2 or 
            affection_status == 'U' and phenotype != 1):
            print('Affection status disagrees with phenotype:\n%s'
                     % ind_object.individual_id, file=sys.stderr)
            print('Exiting ...', file=sys.stderr)
            return False
            
        return True
    
    def check_cmms_gender(self, ind_object):
        """
        Check if the phenotype is correct.
        
        Args:
            ind_object  : An Individuals object
        
        Returns:
            bool : True if phenotype status is correct
                    False otherwise
        """
        ind_id = ind_object.individual_id.split('-')
        sex = ind_object.sex
        sex_code = int(ind_id[-1][:-1])# Males allways have odd numbers and womans even
        if (sex_code % 2 == 0 and sex != 2) or (sex_code % 2 != 0 and sex != 1):
            print('Gender code in id disagrees with sex:\n %s' 
                    % ind_object.individual_id, file=sys.stderr)
            print('Exiting ...', file=sys.stderr)
            return False
        
        return True
        
    def get_models(self, genetic_models):
        """
        Check what genetic models that are found and return them as a set.
        
        Args:
            genetic_models  : A string with genetic models
        
        Returns:
             correct_model_names  : A set with the correct model names
        """
        correct_model_names = set()
        genetic_models = genetic_models.split(';')
        correct_model_names = set()
        for model in genetic_models:
            # We need to allow typos
            if model in self.legal_ar_hom_names:
                model = 'AR_hom'
            elif model in self.legal_ar_hom_dn_names:
                model = 'AR_hom_dn'
            elif model in self.legal_ad_names:
                model = 'AD_dn'
            elif model in self.legal_compound_names:
                model = 'AR_comp'
            elif model in self.legal_x_names:
                model = 'X'
            elif model in self.legal_na_names:
                model = 'NA'
            else:
                print('Incorrect model name: %s' % model, file=sys.stderr)
                print('Legal models: %s' % ','.join(self.legal_ar_hom_names+
                                                    self.legal_ar_hom_dn_names+
                                                    self.legal_ad_names+
                                                    self.legal_compound_names+
                                                    self.legal_x_names+
                                                    self.legal_na_names), file=sys.stderr)
                print('Exiting..')
                sys.exit(1)
            correct_model_names.add(model)
        return correct_model_names
    
    def to_json(self, outfile):
        """
        Print the information from the pedigree file as a json like object.
        This is a list with lists that represents families, families have
        dictionaries that represents individuals like
            [ 
                [
                    {
                        'family_id:family_id',
                        'id':individual_id, 
                        'sex':gender_code, 
                        'phenotype': phenotype_code, 
                        'mother': mother_id, 
                        'father': father_id
                    }, 
                    {
                        ...
                    }
                ],
                [
                    
                ]
            ]
        This object can easily be converted to a json object.
        
        Arguments:
          outfile
          
        """
        json_families = []
        for family_id in self.families:
            family = []
            for individual_id in self.families[family_id].individuals:
                individual = self.families[family_id].individuals[individual_id]
                family.append(individual.get_json())
                
            json_families.append(family)
        
        if outfile:
            outfile.write(json.dumps(json_families))
        else: 
            print(json.dumps(json_families))
        return
    
    def to_madeline(self, outfile=None):
        """
        Produce output in madeline format. If no outfile is given print to 
        screen.
        """
        
        madeline_header = [
            'FamilyID', 
            'IndividualID', 
            'Gender', 
            'Father', 
            'Mother', 
            'Affected',
            'Proband',
            'Consultand',
            'Alive'
        ]
        if outfile:
            outfile.write('\t'.join(madeline_header) + '\n')
        else:
            print('\t'.join(madeline_header))
        
        for family_id in self.families:
            for individual_id in self.families[family_id].individuals:
                individual = self.families[family_id].individuals[individual_id]
                if outfile:
                    outfile.write(individual.get_madeline()+'\n')
                else:
                    print(individual.get_madeline())
        return 
    
    def to_ped(self, outfile=None):
        """
        Produce output in ped format. If no outfile is given print to 
        screen.
        """
        
        ped_header = [
            '#FamilyID', 
            'IndividualID', 
            'PaternalID', 
            'MaternalID', 
            'Sex', 
            'Phenotype',
        ]
        if outfile:
            outfile.write('\t'.join(ped_header) + '\n')
        else:
            print('\t'.join(ped_header))
        
        for family_id in self.families:
            for individual_id in self.families[family_id].individuals:
                individual = self.families[family_id].individuals[individual_id]
                if outfile:
                    outfile.write(individual.get_ped()+'\n')
                else:
                    print(individual.get_ped())
        return 
    

@click.command()
@click.argument('family_file', 
                    nargs=1, 
                    type=click.Path(),
                    metavar='<family_file>'
)
@click.option('-t', '--family_type',
                    type=click.Choice(['ped', 'alt', 'cmms', 'mip']),
                    default='ped',
                    help='If the analysis use one of the known setups, please specify which one. Default is ped'
)
@click.option('--to_json',
                    is_flag=True,
                    help='Print the ped file in json format'
)
@click.option('--to_madeline',
                    is_flag=True,
                    help='Print the ped file in madeline format'
)
@click.option('--to_ped',
                    is_flag=True,
                    help='Print the ped file in ped format with headers'
)
@click.option('-o', '--outfile',
                type=click.File('a')
                )
def cli(family_file, family_type, to_json, to_madeline, to_ped, outfile):
    """Cli for testing the ped parser."""
    
    my_parser = FamilyParser(family_file, family_type)
    
    if to_json:
        my_parser.to_json(outfile)
    elif to_madeline:
        my_parser.to_madeline(outfile)
    elif to_ped:
        my_parser.to_ped(outfile)
    
        


if __name__ == '__main__':
    cli()
