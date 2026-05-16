import os
import sys


class ArgStorage:
    """ Stores the fetching parameters and checks file and directory paths """

    def __init__(self, args):

        # paths
        self.path_query = args.path_query
        self.path_output_dir = args.path_output_dir

        # filtering by date
        self.from_year = args.time_limit_from
        self.to_year = args.time_limit_to

        # boolean flags
        self.reverse = args.reverse
        self.is_pmid = args.is_pmid_list

        # Entrez parameters
        self.address = args.email

        self._check_paths()

    def _check_paths(self):
        self._check_input_file(self.path_query)
        self._check_output_dir(self.path_output_dir)

    @staticmethod
    def _check_input_file(path):
        """ Checks if the input file does exist"""
        absolute_path = os.path.abspath(path)
        # Create output directory if parent directory exists
        if absolute_path:
            if not os.path.exists(absolute_path):
                sys.exit(f"\nEXIT: Unable to locate {absolute_path}."
                         f" Please provide a correct path to the input file/folder")

    @staticmethod
    def _check_output_dir(path_output_dir):
        """ Creates output directory if it does not exist """
        absolute_path_output_dir = os.path.abspath(path_output_dir)
        # Create output directory if parent directory exists
        if absolute_path_output_dir :
            if not os.path.exists(absolute_path_output_dir ):
                os.makedirs(absolute_path_output_dir )


