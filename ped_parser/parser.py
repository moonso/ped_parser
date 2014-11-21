#!/usr/bin/env python
# encoding: utf-8
"""
get_family.py


Parse a file with family info, this can be a .ped file, a .fam, a .txt(CMMS style) 
file or a .txt(Broad style) file.
.ped and .fam always have 6 columns, these are

Family_ID Individual_ID Paternal_ID Maternal_ID 
Sex(1=male; 2=female; other=unknown) 
Phenotype(-9 missing, 0 missing, 1 unaffected, 2 affected)

The .txt allways have two columns on the form 

Individual_ID key=value

Where keys can be fid(=Family Id), mom, dad, sex, phenotype


If a pedigree file includes information about several families this must be taken care
 of by the parser by creating several family objects and then add information about the
  familymembers to theese familys. 

Create a family object and its family members from different types of input file
Created by Måns Magnusson on 2013-01-17.
Copyright (c) 2013 __MyCompanyName__. All rights reserved.
"""

from __future__ import print_function
from __future__ import unicode_literals

import sys
import os
import argparse
from codecs import open
from string import whitespace
from ped_parser import individual, family
from pprint import pprint as pp

class FamilyParser(object):
    """Parses a file with family info and creates a family object with individuals."""
    def __init__(self, infile, family_type = 'ped'):
        super(FamilyParser, self).__init__()
        self.family_type = family_type
        self.families = {}
        self.individuals = {}
        self.header = ['FamilyID', 'SampleID', 'Father', 'Mother', 'Sex', 'Phenotype']
        with open(infile, 'r', encoding='utf-8') as family_file:
            line_count = 0
            if self.family_type in ['ped', 'fam']:
                self.ped_parser(family_file)
            elif self.family_type == 'alt':
                self.alternative_parser(family_file)
            elif self.family_type in ['cmms', 'mip']:
                self.alternative_parser(family_file)
                self.check_cmms_file(family_file, family_type)
            # elif family_type == 'broad':
            #     self.broad_parser(individual_line, line_count)
        for fam in self.families:
            self.families[fam].family_check()
            # print(self.families[family].trios)
            # print(self.families[family].duos)
    
    def get_individual(self, ind, fam_id, mother, father, sex, phenotype):
        """Takes the minimum information about an individual and returns a individual object."""
        #Make shure that these are allways numbers
        if sex not in ['1', '2']:
            sex = '0'
        if phenotype not in ['1', '2']:
            phenotype = '0'
        return individual.Individual(ind, fam_id, mother, father, sex, phenotype)
    
    def ped_parser(self, family_file):
        """Parse a .ped ped file."""
        
        for line in family_file:
            # Check if commented line or empty line:
            if not line.startswith('#') and not all(c in whitespace for c in line.rstrip()):
                splitted_line = line.rstrip().split('\t')
                if len(splitted_line) != 6:
                    splitted_line = line.rstrip().split()
                    if len(splitted_line) != 6:
                        print("""One of the ped lines have %s number of entrys:\n %s""" % (len(splitted_line), line))
                        raise SyntaxError("""One of the lines have the wrong number of entrys!""")
                fam_id = splitted_line[0]
                if fam_id not in self.families:
                    # self.families[fam_id] = family.Family(fam_id)
                    self.families[fam_id] = family.Family(fam_id, {})
                
                ind = splitted_line[1]
                father = splitted_line[2]
                mother = splitted_line[3]
                sex = splitted_line[4]
                phenotype = splitted_line[5]
                
                ind_obj = self.get_individual(ind, fam_id, mother, father, sex, phenotype)
                self.families[fam_id].add_individual(ind_obj)
    

    def alternative_parser(self, family_file):
        """This parses a ped file with more than six columns, in that case header comlumn must exist and each row must have the same amount of columns as the header. First six columns must be the same as in the ped format."""
        
        for line in family_file:
            if line.startswith('#'):
                self.header = line[1:].rstrip().split('\t')
            elif not all(c in whitespace for c in line.rstrip()):
                line = line.rstrip().split('\t')
                if len(line) != len(self.header):
                    print('Number of entrys differ from header. %s' % line)
                    raise SyntaxError()
                if len(line) > 1:
                    
                    fam_id = line[0]
                    
                    if fam_id not in self.families:
                        self.families[fam_id] = family.Family(fam_id)
                    
                    ind = line[1]
                    father = line[2]
                    mother = line[3]
                    sex = line[4]
                    phenotype = line[5]

                    ind_obj = self.get_individual(ind, fam_id, mother, father, sex, phenotype)
                    for i in range(6, len(line)):
                        ind_obj.extra_info[self.header[i]] = line[i]
                    
                    self.families[fam_id].add_individual(ind_obj)
                    
            
    
    def check_cmms_file(self, family_file, family_type):
        """Parse a .ped ped file."""
        
        family_file.seek(0)
        
        for individual_line in family_file:
            if not individual_line.startswith('#'):
                line = individual_line.rstrip().split('\t')
                info = {}
                for i in range(len(line)):
                    if self.header[i] == 'Inheritance_model':
                        #If inheritance model is specified it is a ';'-separated list of models
                        info[self.header[i]] = line[i].split(';')
                    else:
                        info[self.header[i]] = line[i]
                ind = info['SampleID']
                fam_id = info['FamilyID']
                
                # If cmms type we can check the sample names
                if family_type == 'cmms':
                    affection_status = ind.split('-')[-1][-1] # This in A (=affected) or U (=unaffected)
                    phenotype = self.families[fam_id].individuals[ind].phenotype
                    sex = self.families[fam_id].individuals[ind].sex
                    if (affection_status == 'A' and phenotype != 2 or 
                        affection_status == 'U' and phenotype != 1):
                        print('Affection status disagrees with phenotype:\n %s' % individual_line)
                        raise SyntaxError()
                    sex_code = int(ind.split('-')[-1][:-1])# Males allways have odd numbers and womans even
                    if (sex_code % 2 == 0 and sex != 2) or (sex_code % 2 != 0 and sex != 1):
                        print('Gender code in id disagrees with sex:\n %s' % individual_line)
                        raise SyntaxError()
                
                models_of_inheritance = info.get('Inheritance_model', ['NA'])
                
                correct_model_names = set()
                for model in models_of_inheritance:
                    # We need to allow typos
                    if model in ['AR', 'AR_hom']:
                        model = 'AR_hom'
                    elif model in ['AR_denovo', 'AR_hom_denovo', 'AR_hom_dn', 'AR_dn']:
                        model = 'AR_hom_dn'
                    elif model in ['AD_denovo', 'AD_dn']:
                        model = 'AD_dn'
                    elif model in ['AR_compound', 'AR_comp']:
                        model = 'AR_comp'
                    elif model in ['X', 'X_denovo']:
                        model = 'X'
                    elif model in ['NA', 'Na']:
                        model = 'NA'
                    elif model not in ['AD' , 'XR', 'XR_dn', 'XD', 'XD_dn', 'X']:
                        print('Incorrect model name: %s' % model)
                        print('Legal models: AD , AD_denovo, X, X_denovo, AR_hom, AR_hom_denovo, AR_compound, NA')
                        print('Unknown genetic model specified:\n %s' % individual_line)
                        raise SyntaxError()
                    correct_model_names.add(model)
                
                correct_model_names = list(correct_model_names)
                
                if correct_model_names != ['NA']:
                    self.families[fam_id].models_of_inheritance = correct_model_names
        
    def get_json(self):
        """Return the information from the pedigree file as a json like object.
            This will be a list with dictionaries for each family as:
            [{'id': family_id, individuals: 
                [{'id':individual_id, 'sex':gender_code, 'phenotype': phenotype_code, 
                    'mother': mother_id, father: father_id}, ...]}]
            This object can easily be converted to a json object.
            
            Yields:
                dict: family information described above
        """
        json_families = []
        for family_id in self.families:
            family = {'family_id': str(family_id),
                        'individuals': [],
                        }
            for individual_id in self.families[family_id].individuals:
                individual = {'individual_id': individual_id,
                                'sex': self.families[family_id].individuals[individual_id].sex,
                                'phenotype': self.families[family_id].individuals[individual_id].phenotype,
                                'mother': self.families[family_id].individuals[individual_id].mother,
                                'father': self.families[family_id].individuals[individual_id].father
                            }
                if len(self.families[family_id].individuals[individual_id].extra_info) > 0:
                    individual['extra_info'] = self.families[family_id].individuals[individual_id].extra_info
                family['individuals'].append(individual)
            json_families.append(family)
        
        return json_families

def main():
    parser = argparse.ArgumentParser(description="Parse different kind of pedigree files.")
    parser.add_argument('pedigree_file', type=str, nargs=1 , help='A file with pedigree information.')
    parser.add_argument('-type', '--file_type', type=str, nargs=1, choices=['cmms', 'ped', 'fam', 'mip', 'alt'], 
                        default=['ped'] , help='Pedigree file is in ped format.')
    args = parser.parse_args()
    infile = args.pedigree_file[0]
    file_type = args.file_type[0]
    my_parser = FamilyParser(infile, file_type)
    print('Families: %s' % ','.join(list(my_parser.families.keys())))
    for family in my_parser.families:
        print('Fam %s' % family)
        print('Models: %s' % my_parser.families[family].models_of_inheritance)
        print('Individuals: ')
        for individual in my_parser.families[family].individuals:
            print(my_parser.families[family].individuals[individual])
        print('Affected individuals: %s' % ','.join(my_parser.families[family].affected_individuals))
        print('')
    print('Json ped:')
    pp(my_parser.get_json())
    
        


if __name__ == '__main__':
    main()
