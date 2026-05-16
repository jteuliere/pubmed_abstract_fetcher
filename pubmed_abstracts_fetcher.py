#!/usr/local/bin/python3
import argparse
from Bio import Entrez
from utils.abstractfetcher import AbstractFetcher
from utils.argstorage import ArgStorage


def cl_parser():
    """
    Parses the command line.
    :return: argparse.ArgumentParser object
    """
    parser = argparse.ArgumentParser(description="This script returns formatted abstracts from either"
                                                 " a list of Pubmed database queries, or a list of PMID.")
    parser.add_argument("-i", "--path_query", type=str,
                        help="Path to the input queries (use double-quotes for exact expression matching) "
                             "or PMID file (one query or PMID per line)")
    parser.add_argument("-o", "--path_output_dir", type=str,
                        help="Path to the output directory (default: current directory ./)", default="./")
    parser.add_argument("-from", "--time_limit_from", type=int, default=0,
                        help="Optional filter for year lower limit: from which year to retrieve abstract"
                             " (if the specified lower limit is later than the upper time limit, "
                             "this filter will not be applied)")
    parser.add_argument("-to", "--time_limit_to", type=int, default=0,
                        help="Optional filter for year upper limit: up to which year to retrieve abstract"
                             " (if the specified upper limit is earlier than the lower time limit, "
                             "this filter will not be applied)")
    parser.add_argument("-r", "--reverse", action="store_true",
                        help="Optional flag: if used, reverses the order "
                             "of the abstracts to retrieve them in chronological order, from oldest to newest"
                             " (default = from newest to oldest)")
    parser.add_argument("-p", "--is_pmid_list", action="store_true",
                        help="Optional flag: to use if the query file is a list of PMIDs")
    parser.add_argument("-email", "--email", type=str,
                        help="Optional: Email address to connect to Entrez (by default will use my old MNHN address",
                        default="")
    args = parser.parse_args()
    return args


def main():
    args = cl_parser()
    arg_storage = ArgStorage(args)
    # email and tool are required parameters for Entrez API
    Entrez.email = arg_storage.address
    Entrez.sleep_between_tries = 5  # only wait 5 seconds between retries (limit is 3 retries, default parameter value)
    print(arg_storage.address)
    Entrez.tool = "biopython_entrez"
    fetcher = AbstractFetcher(path_query=arg_storage.path_query,
                              path_output_dir=arg_storage.path_output_dir,
                              reverse=arg_storage.reverse,
                              is_pmid=arg_storage.is_pmid,
                              from_year=arg_storage.from_year,
                              to_year=arg_storage.to_year,
                              connector=Entrez)
    fetcher.fetch_abstracts()


if __name__ == "__main__":
    main()
