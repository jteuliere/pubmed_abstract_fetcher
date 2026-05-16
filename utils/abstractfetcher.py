import os
from re import compile
from pathlib import Path
from utils.resultprocessor import ResultProcessor


class AbstractFetcher:

    def __init__(self,
                 path_query=None,
                 path_output_dir=None,
                 reverse=False,
                 is_pmid=False,
                 from_year=None,
                 to_year=None,
                 connector=None):
        self.path_query = path_query
        self.path_output_dir = path_output_dir
        self.reverse = reverse
        self.is_pmid = is_pmid
        self.from_year = from_year
        self.to_year = to_year
        self.info_order = {True: "Oldest first", False: "Newest first"}
        self.info_pmid = {True: "Queries file is a list of PMID.", False: "Queries file is a list of text queries."}
        self.connector=connector
        self.processor = ResultProcessor(reverse=self.reverse, from_year=self.from_year, to_year=self.to_year)

    def fetch_abstracts(self):
        """ Queries the Pubmed database and retrieves abstracts, depending on the type of queries,
        controlled by flag 'is_pmid' """
        print(f"\nQueries file: {self.path_query}\n"
              f"Sorting order: {self.info_order[self.reverse]}\n{self.info_pmid[self.is_pmid]}")
        queries = self._get_list_queries()
        if not self.is_pmid:
            # Inputs are text queries
            self._retrieve_abstracts(queries)
        else:
            self._retrieve_abstracts_from_pmid(queries)
        print("\n")

    def _retrieve_abstracts(self, queries):
        """ Retrieves abstract data for a list of text queries """
        for query in queries:
            print(f"\nCurrent query: {query}")
            # Create output file names from queries
            output_path = self._get_output_path_query(query)
            # Retrieve a list of PMIDs using Entrez esearch
            result = self._esearch_abstracts(query)
            # PMIDs are stored at the "IdList" key
            id_list = result["IdList"]
            # PMIDs separated by commas can be given to Entrez efetch to retrieve the corresponding abstracts
            id_query = ",".join(id_list)
            result = self._efetch_abstracts(id_query)
            if result:
                self.processor.process_results(result=result, output_path=output_path, pattern=self.filter_html())
                # if multiple queries, delay them for at least 0.3 sec in order to avoid getting an API error/ban

    def _retrieve_abstracts_from_pmid(self, queries):
        """ Retrieves abstract data for a list of PMIDs """

        # Create output file name from input file name
        output_path = self._get_output_path()

        # PMIDs separated by commas can be given to Entrez efetch to retrieve the corresponding abstracts
        if all([e.isnumeric() for e in queries]):
            id_query = ",".join(list(set(queries)))
            result = self._efetch_abstracts(id_query)
            if result:
                self.processor.process_results(result=result, output_path=output_path, pattern=self.filter_html())
        else:
            print("    Invalid PMIDs in the provided list.")

    def _get_list_queries(self):
        """ Returns a list of lines (end of lines removed) from a multiline input file """
        with open(self.path_query, "r") as f:
            lines = f.readlines()
            # there are issues if there is an extra carriage return in the file,
            # so this function removes "" elements in the returned list of lines
        return [line.rstrip() for line in lines if len(line.rstrip()) > 0]

    def _get_output_path(self):
        """ Returns the path to the output file with the input file name reused as output file name """
        # remove extension from filename using pathlib.Path stem method
        filename = Path(self.path_query).stem
        return os.path.join(self.path_output_dir, f"{filename}_abstracts.txt")

    def _get_output_path_query(self, query):
        """ Returns the path to the output file with the pubmed query as file name """
        # get filename after replacing spaces by underscores in query
        filename = f"{'_'.join(query.split(' '))}"[:240]  # restricts the length of the filename to 240 characters
        return os.path.join(self.path_output_dir, f"{filename}_abstracts.txt")

    def _esearch_abstracts(self, query, retrieve_max=100000):
        """ Queries the NCBI API with esearch and returns the results (result dict object) """
        handle = self.connector.esearch(db="pubmed", term=query, retmax=retrieve_max)
        if handle:
            # read() parses the XML file and returns the result dictionary
            result = self.connector.read(handle)
            if result:
                handle.close()
                return result
            else:
                print("\n    No abstract retrieved.")
        return {}


    def _efetch_abstracts(self, id_query):
        """ Queries the NCBI API with efetch and returns the results """
        handle = self.connector.efetch(db="pubmed", id=id_query, rettype="abstract", retmod="xml")
        if handle:
            # read() parses the XML file and returns the result dictionary
            result = self.connector.read(handle)
            if result:
                handle.close()
                return result
            else:
                print("\n    No abstract retrieved.")
        return {}


    @staticmethod
    def filter_html():
        """
        Returns a regular expression object needed to filter out HTML tags
        :return: re pattern object
        """
        return compile("<[^<]+?>")
