#!/usr/bin/env python3
import collections
from fuzzywuzzy import fuzz
from google import google
import logging
import operator
import re
import requests
import termcolor
import webbrowser

logging.basicConfig(format='(%(levelname)s) %(message)s', level=logging.INFO)
kInversionWords = ["not"]


class WebQuery:

    def __init__(self):
        self.results = []
        self.logger = logging.getLogger(self.__class__.__name__)
        self.inversion = False

    def search_google(self, query, pages=3, print_results=False):
        """Query google for search results
        Args:
            query (String): to send to google
            pages (Number): of pages to parse from google result
        Returns:
            (Bool): On Success or failure
        """
        self.query = query
        self.inversion = False
        # check for inversion language and mark it if found
        colored_query = query.split(" ")
        query_without_inversion = query.split(" ")
        for i, word in enumerate(colored_query):
            for inversion in kInversionWords:
                if inversion in word.lower():
                    self.inversion = True
                    colored_query[i] = termcolor.colored(
                        colored_query[i], "red")
                    # since inversions don't help in our queries,
                    # we'll just drop them
                    query_without_inversion[i] = ""

        colored_query_str = " ".join(colored_query)
        query_without_inversion_str = " ".join(query_without_inversion)
        self.logger.info("=================================")
        self.logger.info("Query: \"{}\"".format(colored_query_str))
        try:
            self.results = google.search(query_without_inversion_str, pages)
        except Exception as e:
            self.logger.error("Caught exception in google query: {}".format(e))
            return False
        self.logger.info("Got {} results from the googz".format(
            len(self.results)))
        if print_results:
            print(self.results)
        return True

    # def search_bing(self, query):
    #     url = 'https://api.cognitive.microsoft.com/bing/v7.0/composite'
    #     # query string parameters
    #     payload = {'q': query}
    #     # custom headers
    #     headers = {'Ocp-Apim-Subscription-Key': '362ffe563af5458f8818a32a1a165d1b'}
    #     # make GET request
    #     r = requests.get(url, params=payload, headers=headers)
    #     # get JSON response
    #     j=r.json()
    #     pp = pprint.PrettyPrinter(indent=4)
    #     pp.pprint(j)

    def get_answer_permutations(self, answer):
        """Finds reversed strings of the input words
        Args:
            answer (String): of a single answer
        Returns:
            (List): of answers strings to search for
        """
        answers = []
        answers.append(answer)
        if len(answer.split()) > 1:
            words = answer.split()
            words.reverse()
            new_words = " ".join(words)
            answers.append(new_words)
            self.logger.info("Adding answer permutation for {} -> {}".format(
                answer, new_words))
        return answers

    def check_counts_failure(self, counts):
        """
        Check if we got all zeros, spawn a web browser for last ditch effort
        Args:
            counts (List): of pairs containing each answer and
                           the count frequency found in query
        """
        all_zeros = True
        for c in counts:
            if c[1] != 0:
                all_zeros = False
                break
        if all_zeros:
            self.logger.info("Found all zeros, spawning chrome")
            query_split = self.query.split()
            query_pluses = "+".join(query_split)
            webbrowser.open(
                "https://www.google.com/search?q={}".format(query_pluses))

    def answer_frequency(self, answers):
        """Test frequency of occurance of each answer against the search results
        Args:
            answers (List): of strings containing each answer
        Returns:
            (OrderedDict): Dictionary of results, sorted by most probable
        """
        # stage our output counts with the origin answer counts
        counts = {}
        for answer in answers:
            counts[answer] = 0

        # iterate through each answer and count the occurances in each result
        # description test
        for answer in answers:
            # Find additonal answers to search by reversing the order of the
            # words if there are multiple words
            answer_perms = self.get_answer_permutations(answer)
            # find frequency of each answer set (including any possible
            # reversed strings)
            for result in self.results:
                r = re.compile("|".join(r"\b%s\b" % w for w in answer_perms))
                count_result = collections.Counter(
                    re.findall(r, result.description.lower()))
                # update the running counts
                for _, value in count_result.items():
                    counts[answer] = counts[answer] + value

        # sort the results depending on if an inversion is detected or not
        reverse = False if self.inversion else True
        counts = sorted(counts.items(), key=operator.itemgetter(1),
                        reverse=reverse)
        self.logger.info("=================================")
        self.logger.info("Permutation match results")
        for i, c in enumerate(counts):
            if i == 0:
                self.logger.info(termcolor.colored(
                    "{} : {} <---------------".format(c[0], c[1]), "green"))
            else:
                self.logger.info(termcolor.colored(
                    "{} : {}".format(c[0], c[1]), "red"))
        self.logger.info("=================================")

        self.check_counts_failure(counts)
        return counts

    def answer_frequency_fuzzy(self, answers):
        """Test probability (0-100) of match of each answer within each description set
        Args:
            answers (List): of strings containing each answer
        Returns:
            (OrderedDict): Dictionary of results, sorted by most probable
        """
        # stage our output counts with the origin answer counts
        counts = {}
        for answer in answers:
            counts[answer] = 0

        # iterate through each answer and count the occurances in each result
        # description test
        for answer in answers:
            # find frequency of each answer set using fuzzy techniques
            for result in self.results:
                val = fuzz.token_set_ratio(answer, result.description.lower())
                counts[answer] = counts[answer] + val

        # sort the results depending on if an inversion is detected or not
        reverse = False if self.inversion else True
        counts = sorted(counts.items(), key=operator.itemgetter(1),
                        reverse=reverse)
        self.logger.info("=================================")
        self.logger.info("Fuzzy match results")
        for i, c in enumerate(counts):
            if i == 0:
                self.logger.info(termcolor.colored(
                    "{} : {} <---------------".format(c[0], c[1]), "green"))
            else:
                self.logger.info(termcolor.colored(
                    "{} : {}".format(c[0], c[1]), "red"))
        self.logger.info("=================================")

        self.check_counts_failure(counts)
        return counts


if __name__ == "__main__":
    wb = WebQuery()
    # wb.search_google("final cut pro is apple's software for doing what?")
    # counts = wb.answer_frequency(
    #     ["editing video", "spreadsheets", "creating music"])

    wb.search_google("stradivarius was famous for making what")
    counts = wb.answer_frequency(["spotify", "violins", "hearing aids"])
    counts = wb.answer_frequency_fuzzy(["spotify", "violins", "hearing aids"])

    # wb.search_google(
    #     "L.A. ofﬁcials attended the 1956 World Series with hopes of luring\
    #      which team to the West Coast?")
    # counts = wb.answer_frequency(
    #     ["St. Louis Browns", "New York Giants", "Washington Senators"])
    # counts = wb.answer_frequency_fuzzy(
    #     ["St. Louis Browns", "New York Giants", "Washington Senators"])

    wb.search_google("What are the Bildungsroman genre of stories about")
    counts = wb.answer_frequency(
       ["roman empire", "coming of age", "unrequited love"])
    counts = wb.answer_frequency_fuzzy(
       ["roman empire", "coming of age", "unrequited love"])

    # wb.search_google("what was the most downloaded iPhone app of 2016")
    # counts = wb.answer_frequency(["snapchat", "messenger", "pokemon go"])
