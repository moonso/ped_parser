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
from string import whitespace
from ped_parser import individual, family

class FamilyParser(object):
    """Parses a file with family info and creates a family object with individuals."""
    def __init__(self, infile, family_type = 'ped'):
        super(FamilyParser, self).__init__()
        self.family_type = family_type
        self.families = {}
        self.header = []
        with open(infile, 'r') as f:
            line_count = 0
            for line in f:
                individual_line = line.rstrip()
                if not individual_line.startswith('#') and not all(c in whitespace for c in individual_line):
                    if family_type == 'cmms':
                        self.cmms_parser(individual_line, self.header)
                    elif family_type == 'fam':
                        self.ped_parser(individual_line)
                    elif family_type == 'ped':
                        self.ped_parser(individual_line)
                    # elif family_type == 'broad':
                    #     self.broad_parser(individual_line, line_count)
                else:
                    self.header = line[1:].split()
    
    def ped_parser(self, individual_line):
        """Parse a .ped ped file."""
        line = individual_line.split()
        if len(individual_line) < 6:
            raise SyntaxError('One of the ped lines have to few entrys %s' % individual_line)
        
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
        self.families[my_individual.family].add_individual(my_individual)


    def cmms_parser(self, individual_line, header):
        """Parse a .ped ped file."""
        
        line = individual_line.split('\t')
        if len(individual_line) < 6:
            raise SyntaxError('One of the ped lines have to few entrys\n %s' % individual_line)
        
        if len(line) > len(header):
            print(header)
            print('Header length: %s' % str(len(header)))
            print('')
            print(line)
            print('Line length: %s' % str(len(line)))
            print('')
            raise SyntaxError('One of the ped lines have more antrys than specisfied in header\n %s' % individual_line)
            
        
        info = {}
        
        for i in range(len(line)):
            if header[i] == 'Inheritance_model':
                #If inheritance model is specified it is a ';'-separated list of models
                info[header[i]] = line[i].split(';')
            else:
                info[header[i]] = line[i]
        
        fam_id = info.get('FamilyID', '0')
        
        if fam_id not in self.families:
            self.families[fam_id] = family.Family(fam_id)
        
        ind = info.get('SampleID', '0')
        father = info.get('Father', '0')
        mother = info.get('Mother', '0')
        sex = info.get('Sex', '0') # 1=male, 2=female, other=unknown
        phenotype = info.get('Phenotype', '0') # -9, 0 = missing, 1=unaffected, 2=affected
        
        #Make shure that these are allways numbers
        if sex not in ['1', '2']:
            sex == '0'
        if phenotype not in ['1', '2']:
            phenotype == '0'
        
        affection_status = ind.split('-')[-1][-1] # This in A (=affected) or U (=unaffected)
        
        
        if (affection_status == 'A' and phenotype != '2') or (affection_status == 'U' and phenotype == '2'):
            raise SyntaxError('Affection status disagrees with phenotype:\n %s' % individual_line)
        
        sex_code = int(ind.split('-')[-1][:-1])# Males allways have odd numbers and womans even
        
        if (sex_code % 2 == 0 and sex != '2') or (sex_code % 2 != 0 and sex != '1'):
            raise SyntaxError('Gender code in id disagrees with sex:\n %s' % individual_line)

        
        models_of_inheritance = info.get('Inheritance_model', 'NA')
        
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
            
        my_individual = individual.Individual(ind, fam_id, mother, father, sex, phenotype)

        self.families[my_individual.family].add_individual(my_individual)
    

def main():
    parser = argparse.ArgumentParser(description="Parse different kind of pedigree files.")
    parser.add_argument('pedigree_file', type=str, nargs=1 , help='A file with pedigree information.')
    parser.add_argument('-type', '--file_type', type=str, nargs=1, choices=['cmms', 'ped', 'fam'], 
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
