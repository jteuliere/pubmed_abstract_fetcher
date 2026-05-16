from re import sub


class ResultProcessor:
    """ Processes the results from the Entrez connector """
    def __init__(self, reverse=False, from_year=None, to_year=None):
        self.reverse = reverse
        self.from_year = from_year
        self.to_year = to_year

    def process_results(self, result, output_path, pattern):
        """ Processes results through the collect_data and the write_data functions
        :param result: Entrez.read(handle) parsed file from efetch
        :param output_path: output file path
        :param pattern: regular expression object from re.compile() """

        # Get abstracts records
        papers = result["PubmedArticle"]
        print(f"\n    Retrieved {len(papers)} abstracts.")
        # Initialize dictionaries and reference set
        data_dict, no_date_dict = {}, {}
        for paper in papers:
            pmid = str(paper["MedlineCitation"]["PMID"])
            data_dict, no_date_dict = self._collect_data(paper, data_dict, pmid, pattern)
        self._write_data(data_dict, no_date_dict, output_path)

    def _collect_data(self, paper, data_dict, pmid, pattern):
        """ Parses the dictionaries provided by Biopython Entrez.read(handle) function translating the Entrez XML file
        :param paper: record object from Entrez.read(handle)["PubmedArticle"] key
        :param data_dict: dictionary storing extracted data for each PMID if a publication date is retrieved
        :param pmid: current record associated PMID
        :param pattern: regular expression object from re.compile()
        :return: updated data_dict and no_date_dict (dictionary storing extracted data for each PMID
                 for which a publication date is NOT retrieved) with data corresponding to the current PMID"""

        no_date_dict = {}
        # extract article title, journal, publication year, abstract text and list of authors

        # Article title:
        title = self._format_text(paper["MedlineCitation"]["Article"]["ArticleTitle"], pattern)

        # Journal name:
        if "Title" in paper["MedlineCitation"]["Article"]["Journal"]:
            journal = paper["MedlineCitation"]["Article"]["Journal"]["Title"]
        else:
            journal = "## No journal retrieved. ##"

        # Publication date:
        if "Year" in paper["MedlineCitation"]["Article"]["Journal"]["JournalIssue"]["PubDate"]:
            date = paper["MedlineCitation"]["Article"]["Journal"]["JournalIssue"]["PubDate"]["Year"]
        else:
            date = "## No date retrieved. ##"
            # capture the PMIDs with missing date info (they can't be used to order abstracts
            # but will be added at the end of the formatted list of abstracts in the output file.)
            no_date_dict[pmid] = {}

        # Abstract itself:
        if "Abstract" in paper["MedlineCitation"]["Article"].keys():
            abstract = self._format_text("".join(paper["MedlineCitation"]["Article"]["Abstract"]["AbstractText"]), pattern)
            if abstract.startswith("Abstract"):
                abstract = abstract[8:]
        else:
            abstract = "## No abstract. ##"

        # List of authors:
        if "AuthorList" in paper["MedlineCitation"]["Article"].keys():
            authors_list = [x["LastName"] + " " + x["ForeName"][0] + "."
                            for x in paper["MedlineCitation"]["Article"]["AuthorList"]
                            if ("LastName" in x.keys() and "ForeName" in x.keys())]
            authors = self._format_authors(authors_list)
        else:
            authors = "## Unavailable authors list ##"

        # Populate dictionaries with collected data
        # When a date was found:
        if pmid not in no_date_dict:
            # initialize a subdictionary in data_dict
            data_dict[pmid] = {}
            # update data_dict with data associated with the current PMID
            data_dict[pmid]["title"] = title
            data_dict[pmid]["journal"] = journal
            data_dict[pmid]["date"] = date
            data_dict[pmid]["abstract"] = abstract
            data_dict[pmid]["authors"] = authors

        # When the date went missing:
        else:
            # update no_date_dict with data associated with the current PMID, and remove the key from data_dict
            no_date_dict[pmid]["title"] = title
            no_date_dict[pmid]["journal"] = journal
            no_date_dict[pmid]["date"] = date
            no_date_dict[pmid]["abstract"] = abstract
            no_date_dict[pmid]["authors"] = authors

        return data_dict, no_date_dict

    @staticmethod
    def _format_authors(authors_list):
        """ Simplifies authorship depending on the number of authors """

        if len(authors_list) > 2:
            authors = [authors_list[0], "et al"]
        elif len(authors_list) == 2:
            authors = [authors_list[0], "and", authors_list[1]]
        else:
            authors = authors_list
        return " ".join(authors)

    @staticmethod
    def _format_text(html_text, pattern):
        """ Removes HTML formatting from text and extra spaces artifacts (modify as needed!) """
        return sub(pattern, "", html_text)

    def _write_data(self, data_dict, no_date_dict, output_path):
        """ A wrapper for the functions create_dict_date() & filter_by_date() that writes the abstracts to output file.
        :param data_dict: dict storing extracted data for each PMID if a publication date is retrieved
        :param no_date_dict: dict storing extracted data for each PMID for which a publication date is NOT retrieved """

        # Collect date information from dictionary data_dict
        dict_date, list_date = self._create_dict_date(data_dict)
        dict_date, list_date = self._filter_by_date(dict_date, list_date)
        nb_abstract = 0
        for date, d in dict_date.items():
            nb_abstract += len(d)
        word = "abstracts"
        if nb_abstract == 1:
            word = "abstract"
        if len(list_date) == 1:
            print(f"    {nb_abstract} {word} kept, published in {list_date[0]}.")
        else:
            min_date, max_date = min(list_date), max(list_date)
            print(f"    {nb_abstract} {word} kept, published between {min_date} and {max_date}.")
        print(f"    Saving {word} to output file...")

        # First write data for abstracts with a date
        with open(output_path, "w") as f:
            # use the date order in list_date
            for date in list_date:
                # get all corresponding PMIDs from dict_date and get associated data from data_dict:
                for pmid in dict_date[date]:
                    title, journal, authors, date, abstract = self._get_data_from_dict(data_dict, pmid)
                    f.write(f"{title}\n{authors} ({date}) {journal} // PMID: {pmid}\n    {abstract}\n\n")

        # Second, add info for abstracts with no date
        if len(no_date_dict) > 0:
            with open(output_path, "a") as f:
                f.write(f"!!!    The following abstracts had no date of publication    !!!\n\n")
                for pmid in no_date_dict:
                    title, journal, authors, date, abstract = self._get_data_from_dict(no_date_dict, pmid)
                    f.write(f"{title}\n{authors} ({date}) {journal} // PMID: {pmid}\n    {abstract}\n\n")

        print("    Done.")

    @staticmethod
    def _get_data_from_dict(pmid_dict, pmid):
        """ Extracts and returns title, journal, authors, date and abstract data from PMID dict """
        res = []
        for key in ["title", "journal", "authors", "date", "abstract"]:
            res.append(pmid_dict[pmid].get(key, ""))
        return res

    def _create_dict_date(self, data_dict):
        """ Creates a dictionary {publication date: set(PMIDs)} to link ordered dates to abstracts """
        dict_date = {}
        for pmid in data_dict:
            date = data_dict[pmid].get("date", "No date retrieved.")
            if date != "No date retrieved.":
                date = int(date)
                if date not in dict_date:
                    dict_date[date] = set()
                dict_date[date].add(pmid)
        order = not self.reverse
        # order will be True if the flag is not used (reverse == False), i.e. reverse chronological order
        list_date = sorted(dict_date, reverse=order)
        return dict_date, list_date

    def _filter_by_date(self, dict_date, list_date):
        """ Filters dict_date and list_date to abstracts published in the inclusive interval (from_year, to_year)
        if provided, or from min_date or to max_date otherwise """
        min_date, max_date = min(dict_date), max(dict_date)
        if self.from_year:
            min_date = int(self.from_year)
        if self.to_year:
            max_date = int(self.to_year)
        if max_date < min_date:
            min_date, max_date = min(dict_date), max(dict_date)
        new_list_date = [d for d in list_date if d in range(min_date, max_date + 1)]
        new_dict_date = {d: data for d, data in dict_date.items() if d in new_list_date}
        return new_dict_date, new_list_date
