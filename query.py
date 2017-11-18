#!/usr/bin/env python3
import collections
from google import google
import logging
import operator
import re
import termcolor

logging.basicConfig(format='[%(asctime)s](%(levelname)s) %(message)s', level=logging.INFO)
kInversionWords = ["not", "least", "non"]

class WebQuery:

    def __init__(self):
        self.results = []
        self.logger = logging.getLogger(self.__class__.__name__)
        self.inversion = False

    def search_google(self, query, pages=3, print_results=False):
        """ 
        Query google for search results 
        @param query String to send to google
        @param pages Number of pages to parse from google result 
        """
        self.inversion = False
        colored_query = query.split(" ")
        query_without_inversion = query.split(" ")
        for i, word in enumerate(colored_query):
            for inversion in kInversionWords:
                if inversion in word.lower():
                    self.inversion = True
                    colored_query[i] = termcolor.colored(colored_query[i], "red")
                    query_without_inversion[i] = ""
                    
        colored_query_str = " ".join(colored_query)
        query_without_inversion_str = " ".join(query_without_inversion)
        self.logger.info("=================================")
        self.logger.info("Query: \"{}\"".format(colored_query_str))
        self.results = google.search(query_without_inversion_str, pages)
        self.logger.info("Got {} results from the googz".format(len(self.results)))
        if print_results:
            print(self.results)


    def answer_frequency(self, answers):
        """ 
        Test frequency of occurance of each answer against the search results
        @param answers List of strings containing each answer 
        """
        counts = {}
        for answer in answers:
            counts[answer] = 0
        r = re.compile("|".join(r"\b%s\b" % w for w in answers))
        for result in self.results:
            count_result = collections.Counter(re.findall(r, result.description.lower()))
            # update the running counts
            for key, value in count_result.items():
                counts[key] = counts[key] + value
        reverse = False if self.inversion else True
        counts = sorted(counts.items(), key=operator.itemgetter(1), reverse=reverse)
        self.logger.info("=================================")
        for i,c in enumerate(counts):
            if i==0:
                self.logger.info(termcolor.colored("{} : {} <---------------".format(c[0],c[1]), "green"))
            else:
                self.logger.info(termcolor.colored("{} : {}".format(c[0],c[1]), "red"))
        self.logger.info("=================================")
        return counts


if __name__ == "__main__":
    wb = WebQuery()
    wb.search_google("stradivarius was famous for making what")
    counts = wb.answer_frequency(["spotify", "violins", "hearing aids"])

    wb.search_google("how many leaves does a lucky clover have")
    counts = wb.answer_frequency(["three", "four", "five"])

    wb.search_google("What are the Bildungsroman genre of stories about")
    counts = wb.answer_frequency(["roman empire", "coming of age", "unrequited love"])

    wb.search_google("what was the most downloaded iPhone app of 2016")
    counts = wb.answer_frequency(["snapchat", "messenger", "pokemon go"])    
