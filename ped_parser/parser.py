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

import sys
import os
import argparse
from codecs import open#!/usr/bin/env python
from string import whitespace
from ped_parser import individual, family

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
            if family_type in ['ped', 'fam']:
                self.ped_parser(family_file)
            elif family_type == 'alt':
                self.alternative_parser(family_file)
            elif family_type in ['cmms', 'mip']:
                self.alternative_parser(family_file)
                self.check_cmms_file(family_file, family_type)
            # elif family_type == 'broad':
            #     self.broad_parser(individual_line, line_count)
        for family in self.families:
            self.families[family].family_check()
            # print(self.families[family].trios)
            # print(self.families[family].duos)
    
    def ped_parser(self, family_file):
        """Parse a .ped ped file."""
        
        for line in family_file:
            if not line.startswith('#') and not all(c in whitespace for c in line.rstrip()):
                splitted_line = line.rstrip().split('\t')
                if len(splitted_line) != 6:
                    splitted_line = line.rstrip().split()
                    if len(splitted_line) != 6:
                        raise SyntaxError("""One of the ped lines have %s number of entrys: %s""" % (line, len(splitted_line)))
                if len(splitted_line) > 1:
                    fam_id = splitted_line[0]
                    
                    if fam_id not in self.families:
                        self.families[fam_id] = family.Family(fam_id)
                    
                    ind = splitted_line[1]
                    father = splitted_line[2]
                    mother = splitted_line[3]
                    sex = splitted_line[4]
                    phenotype = splitted_line[5]
                    
                    #Make shure that these are allways numbers
                    if sex not in ['1', '2']:
                        sex == '0'
                    if phenotype not in ['1', '2']:
                        phenotype == '0'
                    my_individual = individual.Individual(ind, fam_id, mother, father, sex, phenotype)
                    self.individuals[my_individual.individual_id] = my_individual
                    self.families[my_individual.family].add_individual(my_individual)
    
    def alternative_parser(self, family_file):
        """This parses a ped file with more than six columns, in that case header comlumn must exist and each row must have the same amount of columns as the header. First six columns must be the same as in the ped format."""
        
        for line in family_file:
            if line.startswith('#'):
                self.header = line[1:].split('\t')
            elif not all(c in whitespace for c in line.rstrip()):
                line = line.rstrip().split('\t')
                if len(line) != len(self.header):
                    raise SyntaxError('Number of entrys differ from header. %s' % line)
                if len(line) > 1:
                    
                    fam_id = line[0]
                    
                    if fam_id not in self.families:
                        self.families[fam_id] = family.Family(fam_id)
                    
                    ind = line[1]
                    father = line[2]
                    mother = line[3]
                    sex = line[4]
                    phenotype = line[5]
                    
                    #Make shure that these are allways numbers
                    if sex not in ['1', '2']:
                        sex == '0'
                    if phenotype not in ['1', '2']:
                        phenotype == '0'
                    my_individual = individual.Individual(ind, fam_id, mother, father, sex, phenotype)
                    self.individuals[my_individual.individual_id] = my_individual
                    self.families[my_individual.family].add_individual(my_individual)
            
    
    def check_cmms_file(self, family_file, family_type):
        """Parse a .ped ped file."""
        
        for individual_line in family_file:
            
            line = individual_line.rstrip().split('\t')
            
            for i in range(len(line)):
                if self.header[i] == 'Inheritance_model':
                    #If inheritance model is specified it is a ';'-separated list of models
                    info[self.header[i]] = line[i].split(';')
                else:
                    info[self.header[i]] = line[i]
            ind = line[0]
            
        # If cmms type we can check the sample names
        if family_type == 'cmms':
            affection_status = ind.split('-')[-1][-1] # This in A (=affected) or U (=unaffected)
            phenotype = self.individuals[ind].phenotype
            sex = self.individuals[ind].sex
            if (affection_status == 'A' and phenotype != '2' or 
                affection_status == 'U' and phenotype != '1'):
                raise SyntaxError('Affection status disagrees with phenotype:\n %s' % individual_line)
            sex_code = int(ind.split('-')[-1][:-1])# Males allways have odd numbers and womans even
            if (sex_code % 2 == 0 and sex != 2) or (sex_code % 2 != 0 and sex != 1):
                raise SyntaxError('Gender code in id disagrees with sex:\n %s' % individual_line)
        
        models_of_inheritance = info.get('Inheritance_model', ['NA'])
        
        correct_model_names = []
        for model in models_of_inheritance:
            if model in ['AR', 'AR_hom']:
                model = 'AR_hom'
            elif model in ['AR_denovo', 'AR_hom_denovo']:
                model = 'AR_hom_denovo'
            elif model in ['NA', 'Na']:
                model = 'NA'
            elif model not in ['AD' , 'AD_denovo', 'X', 'X_denovo', 'AR_compound', 'NA', 'Na']:
                print('Incorrect model name: %s' % model)
                print('Legal models: AD , AD_denovo, X, X_denovo, AR_hom, AR_hom_denovo, AR_compound, NA')
                raise SyntaxError('Unknown genetic model specified:\n %s' % individual_line)
            correct_model_names.append(model)
        
        if correct_model_names != ['NA']:
            self.families[fam_id].models_of_inheritance = correct_model_names
        

def main():
    parser = argparse.ArgumentParser(description="Parse different kind of pedigree files.")
    parser.add_argument('pedigree_file', type=str, nargs=1 , help='A file with pedigree information.')
    parser.add_argument('-type', '--file_type', type=str, nargs=1, choices=['cmms', 'ped', 'fam', 'mip', 'alt'], 
                        default=['ped'] , help='Pedigree file is in ped format.')
    args = parser.parse_args()
    infile = args.pedigree_file[0]
    file_type = args.file_type[0]
    my_parser = FamilyParser(infile, file_type)
    print('Families:' ,my_parser.families)
    for family in my_parser.families:
        print('Fam %s' % family)
        print('Models: %s' % my_parser.families[family].models_of_inheritance)
        print('Individuals: ')
        for individual in my_parser.families[family].individuals:
            print(individual)
    
        


if __name__ == '__main__':
    main()
