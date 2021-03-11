# README for the GnomAD Allele Frequency Fetcher

## Goal:

The goal of this project was to create a commandline interface that can be used to query GnomAD's api to obtain the allele frequencies of specified variants in specified populations

## installing:

1. clone the repository

2. run the following command to install the proper version of all required packages
   `pip install -r requirements.txt`

_note_: The program was design for python 3.7 but should work for other version. You can always create a virtual environment with this version

## Running the program:

1. cd into the cloned directory and then follow the below example

`python3 main.py --var_input {path to variant file} --output {path to output files} --pop_code {population of interest}`

_Breaking down the above command:_

- **py``thon3 main.py**: just the command to run the program you could also change the program to an executable file and run ./main.py
- **--var_input**: This parameter accepts a path to an excel file containing a column called SNPs which contains the SNP id of either rsID or some illumnia array probes
- **--output**: This flag accepts a string listing the directory that the user wishes to output the files to
- **--pop_code**: This flag accepts a string for the code of the population that the user wishes to get the allele frequency of. So for Non-Finnish Europeans this would be NFE. To find these codes just look on GnomAD's website

## Note to remember:

The program will form a log file in the specified output directory. If any variant is not found within the GnomAD database then it will write this variant in the log file

## Thanks:

This code was adapted from the code provided by [ressy](https://gist.github.com/ressy/6fd7f6ee6401ac8e703dc2709399869e) and the answer from BretSnoop at [stackexchange](https://bioinformatics.stackexchange.com/questions/933/is-there-public-restful-api-for-gnomad)
