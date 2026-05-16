# pubmed_abstract_fetcher
A simple command line tool to retrieve lists of NCBI Pubmed abstracts as human and LLM-readable text.

This script is a simple wrapper around BioPython Entrez API to retrieve formatted Pubmed abstracts for the provided queries or for a list of PMIDs. It allows filtering and ordering by date.

Resuirements:
Python > 3.10
Biopython (https://biopython.org/ , install: pip install biopython)

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Usage:

python pubmed_abstract_fetcher.py -i [PATH TO QUERY FILE] -o [PATH TO OUTPUT DIRECTORY] -email [AN EMAIL ADRESS TO SIGN INTO ENTREZ DB]

Optional parameters

-from [YEAR]
-to [YEAR]

Optional flag
-r : reverse chronological order
-p:  the query file is a PMID list

Help:

python pubmed_abstract_fetcher.py -h

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Input file format:
Text file with input queries using Pubmed query syntax (use double-quotes for exact expression matching) or PMIDs (one query or PMID per line)

Output files:
If the input file contains Pubmed queries, the script outputs one text file, containing formatted abstract text, per query (the filename is the query, with a limit of 240 characters). If the input file is a PMID list, the script creates only one output text file with the corresponding formatted abstracts.
