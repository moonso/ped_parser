# PEDIGREE PARSER #

[![Build Status](https://travis-ci.org/moonso/ped_parser.svg)](https://travis-ci.org/moonso/ped_parser)

A small tool for parsing files in the [pedigree (.ped) format](http://pngu.mgh.harvard.edu/~purcell/plink/data.shtml#ped).
The parser will create a family object for each family found in the pedigree file and a individual object for each individual found.
The tool can be used to access information from ped files or convert the data to [madeline2](http://eyegene.ophthy.med.umich.edu/madeline/index.php) format for drawing pedigree trees.
Also it is possible to create family objects and individual object and print the in ped and madeline formats.

## Installation ##

    pip install ped_parser


## General ##

Parse a file with family info, this can be a .ped file, a .fam, a .txt(alternative ped style) 
file or another ped based alternative.

.ped and .fam always have 6 columns, these are

```
Family_ID - '.' or '0' for unknown
Individual_ID - '.' or '0' for unknown
Paternal_ID - '.' or '0' for unknown
Maternal_ID - '.' or '0' for unknown
Sex - '1'=male; '2'=female; ['other', '0', '.']=unknown
Phenotype - '1'=unaffected, '2'=affected, ['-9', '0', '.']= missing
```

The other types must specify the columns in the header.
Header always start with '#'.
These files always start with the ped columns described above.

The following column names will be treated with care, which means that they will be used when outputting a madeline type of file or makes accesable variables in the parser.

```InheritanceModel``` - a ';'-separated list of expected inheritance models.

Choices are

```
['AR','AR_hom','AR_denovo','AR_hom_denovo','AR_hom_dn','AR_dn','AR_compound','AR_comp','AD','AD_dn','AD_denovo','X','X_dn','X_denovo','NA','Na','na','.']
```

A proband is the first affected member of a pedigree coming to medical attention. They are annotated with:
```Proband - 'Yes', 'No', 'Unknown' or '.'```
A consultand is an individual who has sought genetic counseling or testing.
```Consultand - 'Yes', 'No', 'Unknown' or '.'```
```Alive - 'Yes', 'No', 'Unknown' or '.'```



## Usage ##

ped_parser can be used as a standalone command line tool to convert ped files and ped like files to json or madeline2 format.
Or just to get information about the content of a pedigree file.

When installed, try:

    ped_parser --help

for more information.

When parsing the .ped file the following will be checked:

- That the family bindings are consistent and that all mandatory values exist and have correct values. Exceptions are raised if the number of columns differ between individuals
- That mother and father have correct gender, if not an exception is raised
- If two individuals are siblings
- Identify all trios (or duos) found in the pedigree


## Alternative .ped files ##

ped\_parser does also support modified .ped files (some users want to store extra family and/or individual information in the pedigree file). In this case ped\_parser will look at the first 6 columns and work as described above.
In this case use:

    ped_parser infile.ped --family_type alt

### Madeline2 conversion ###


[Madeline2](http://eyegene.ophthy.med.umich.edu/madeline/index.php) is an excellent tool to draw pedigrees but they use there own input formats. ped_parser can now produce madeline2 input files from ped files by using

    ped_parser input.ped --to_madeline [-o output.txt]

The following columns will be added to the madeline file:

'FamilyID', 'IndividualID', 'Gender', 'Father', 'Mother', 'Affected', 'Proband', 'Consultand', 'Alive'

Since only the first six of these columns are the standard ped format columns ped parser allows for alternative pedigree files with the following rules:


### json conversion ###



    ped_parser input.ped --to_json [-o output.txt]

This is a list with lists that represents families, families have
dictionaries that represents individuals like

 ```json
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
```

### Create ped like objects ###

Ped like objects can be created from within a python program and convert them to ped, json or madeline output like this

```python
    
    >from ped_parser import Individual, Family
    
    >outfile = open('my_family.ped','a')
    >my_individuals = []
    >my_individuals.append(Individual(
                                        'proband', 
                                        family='1', 
                                        mother='mother', 
                                        father='father',
                                        sex='1',
                                        phenotype='2'
                                      )
                            )
    >my_individuals.append(Individual(
                                        'mother', 
                                        family='1', 
                                        mother='0', 
                                        father='0',
                                        sex='2',
                                        phenotype='1'
                                      )
                            )
    >my_individuals.append(Individual(
                                        'father', 
                                        'family'='1', 
                                        'mother'='0', 
                                        'father'='0',
                                        'sex'='1',
                                        'phenotype'='1'
                                      )
                            )
    >my_family = Family(family_id='1')
    >for individual in my_individuals:
        my_family.add_individual(individual)
    >my_family.to_ped(outfile)

```
