#!/usr/bin/env python3
import collections
from google import google
import logging
import operator
import re
import termcolor
import webbrowser

logging.basicConfig(format='[%(asctime)s](%(levelname)s) %(message)s', level=logging.INFO)
kInversionWords = ["not"]

class WebQuery:

    def __init__(self):
        self.results = []
        self.logger = logging.getLogger(self.__class__.__name__)
        self.inversion = False

    def search_google(self, query, pages=5, print_results=False):
        """ 
        Query google for search results 
        @param query String to send to google
        @param pages Number of pages to parse from google result 
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
                    colored_query[i] = termcolor.colored(colored_query[i], "red")
                    # since inversions don't help in our queries, we'll just drop them
                    query_without_inversion[i] = ""
                    
        colored_query_str = " ".join(colored_query)
        query_without_inversion_str = " ".join(query_without_inversion)
        self.logger.info("=================================")
        self.logger.info("Query: \"{}\"".format(colored_query_str))
        self.results = google.search(query_without_inversion_str, pages)
        self.logger.info("Got {} results from the googz".format(len(self.results)))
        if print_results:
            print(self.results)

    def get_answer_permutations(self, answer):
        """ 
        Finds reversed strings of the input words
        @param answer String of a single answer
        returns list of answers strings to search for """
        answers = []
        answers.append(answer)
        if len(answer.split()) > 1:
            words = answer.split()
            words.reverse()
            new_words = " ".join(words)
            answers.append(new_words)
            self.logger.info("Adding answer permutation for {} -> {}".format(answer, new_words))
        return answers

    def answer_frequency(self, answers):
        """ 
        Test frequency of occurance of each answer against the search results
        @param answers List of strings containing each answer 
        """
        # stage our output counts with the origin answer counts
        counts = {}
        for answer in answers:
            counts[answer] = 0

        # iterate through each answer and count the occurances in each result descriptions
        for answer in answers:
            # Find additonal answers to search by reversing the order of the words if there are multiple words
            answer_perms = self.get_answer_permutations(answer)
            # find frequency of each answer set (including any possible reversed strings)
            for result in self.results:
                r = re.compile("|".join(r"\b%s\b" % w for w in answer_perms))        
                count_result = collections.Counter(re.findall(r, result.description.lower()))
                # update the running counts
                for _, value in count_result.items():
                    counts[answer] = counts[answer] + value

        # sort the results depending on if an inversion is detected or not
        reverse = False if self.inversion else True
        counts = sorted(counts.items(), key=operator.itemgetter(1), reverse=reverse)
        self.logger.info("=================================")
        for i,c in enumerate(counts):
            if i==0:
                self.logger.info(termcolor.colored("{} : {} <---------------".format(c[0],c[1]), "green"))
            else:
                self.logger.info(termcolor.colored("{} : {}".format(c[0],c[1]), "red"))
        self.logger.info("=================================")
        
        # check if we got all zeros, if so, spawn a web browser for last ditch effort
        all_zeros = True
        for c in counts:
            if c[1] != 0:
                all_zeros = False
                break
        if all_zeros:
            self.logger.info("Found all zeros, spawning chrome")
            query_split = self.query.split()
            query_pluses = "+".join(query_split)
            webbrowser.open("https://www.google.com/search?q={}".format(query_pluses))

        return counts


if __name__ == "__main__":
    wb = WebQuery()
    wb.search_google("final cut pro is apple's software for doing what?")
    counts = wb.answer_frequency(["editing video", "spreadsheets", "creating music"])

    wb.search_google("stradivarius was famous for making what")
    counts = wb.answer_frequency(["spotify", "violins", "hearing aids"])

    # wb.search_google("how many leaves does a lucky clover have")
    # counts = wb.answer_frequency(["three", "four", "five"])

    # wb.search_google("What are the Bildungsroman genre of stories about")
    # counts = wb.answer_frequency(["roman empire", "coming of age", "unrequited love"])

    # wb.search_google("what was the most downloaded iPhone app of 2016")
    # counts = wb.answer_frequency(["snapchat", "messenger", "pokemon go"])    
