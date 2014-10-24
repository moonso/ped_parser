#PEDIGREE PARSER#


A small tool for parsing files in the pedigree (.ped) format.
The parser will create a family object for each family found in the pedigree file and a individual object for each individual found.

##Installation##

    pip install ped_parser

##Usage##
Example:

Family file 'my_family.ped':


    \#Standard trio
    \#FamilyID       SampleID        Father  Mother  Sex     Phenotype
    1       proband father  mother  1       2
    1       mother  0       0       2       1
    1       father  0       0       1       1
    1       daughter father  mother  2       1

    In [1]: from ped_parser import parser
    In [2]: my_parser = parser.FamilyParser('my_family.ped')
    In [3]: my_parser.individuals 
    Out[3]:
    {'father': <ped_parser.individual.Individual at 0x10a18d490>,
     'mother': <ped_parser.individual.Individual at 0x10a098f50>,
     'proband': <ped_parser.individual.Individual at 0x10a18d2d0>,
     'daughter': <ped_parser.individual.Individual at 0x10a18d510>}
    
    In [5]: my_parser.individuals['proband'].siblings
    Out[5]:
    {'daughter': <ped_parser.individual.Individual at 0x10a18d510>}
    In [6]: my_parser.families['1'].trios
    Out[6]: [{'father', 'mother', 'proband'}, {'daughter', 'father', 'mother'}]

When parsing the .ped file the following will be checked:

- That the family bindings are consistent and that all mandatory values exist and have correct values. Exceptions are raised if the number of columns differ between individuals
- That mother and father have correct gender, if not an exception is raised
- If two individuals are siblings
- Identify all trios (or duos) found in the pedigree


##Alternative .ped files##

ped\_parser does also support modified .ped files (some users want to store extra family and/or individual information in the pedigree file). In this case ped\_parser will look at the first 6 columns and work as described above.
In this case use:

    In [1]: my_parser = parser.FamilyParser('my_family.ped', 'alt')


##Methods##

	my_parser.get_json()

returns the families in a list of dictionaries that can be made to json object. Looks like:

````
[
	{'family_id': '1',
  	 'individuals': [
		 		{'father': '0',
                   'individual_id': 'mother',
                   'mother': '0',
                   'phenotype': 1,
                   'sex:': 2
			   	},
                  {'father': 'father',
                   'individual_id': 'daughter',
                   'mother': 'mother',
                   'phenotype': 2,
                   'sex:': 1
			    },
                  {'father': '0',
                   'individual_id': 'father',
                   'mother': '0',
                   'phenotype': 1,
                   'sex:': 1
			    },
                  {'father': 'father',
                   'individual_id': 'proband',
                   'mother': 'mother',
                   'phenotype': 2,
                   'sex:': 1
			   }
			  ]
 	}
]```