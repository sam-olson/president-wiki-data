import requests
import re
import urllib
import urllib.request

from bs4 import BeautifulSoup
import pandas as pd

from utils import *


class President:
    '''
    Class for obtaining presidential data from Wikipedia.
    The class can be run with a BeautifulSoup object representing the HTML
    of the president's Wikipedia page stored in a variable, or alternatively there are class methods for
    obtaining the HTML from a text file or directly from the web

    Parameters
    ----------
    soup: BeautifulSoup object representing the HTML of the president's Wikipedia page

    '''

    def __init__(self, soup):
        # extracting the infobox table
        self._soup = soup.find("table", class_="infobox vcard")
        self._name = self.parse_name()              # president's name
        self._job_list = self.compile_jobs()        # compiled job list
        self._party = self.parse_party()            # political party
        self._born, self._died = self.parse_birth_death()   # bith and death dates
        self._num = re.findall(
            "^(\d+)", self._job_list[0]["title"])[0]  # president number

    @classmethod
    def from_wiki(cls, name):
        '''
        Class method for creating an instance by downloading the HTML from Wikipedia

        Parameters
        ----------
        name: name of president as a string (i.e. "Barack Obama")
        '''

        try:
            r = requests.get(to_url(name))
            soup = BeautifulSoup(r.text, features="lxml")
            return cls(soup)
        except:
            print("[ERROR] Cannot find Wikipedia URL for {}".format(name))

    @classmethod
    def from_text_file(cls, fpath):
        '''
        Class method for creating an instance by importing the HTML from a text file

        Parameters
        ----------
        fpath: file path to text file
        '''

        with open(fpath, "r") as f:
            soup = BeautifulSoup(f.read(), features="lxml")
        return cls(soup)

    def parse_name(self):
        '''
        Method for parsing the name of the president from the HTML
        '''

        name = self._soup.find("div", class_="fn").text.strip()
        return name

    def parse_jobs(self):
        '''
        Method for parsing the government positions held by the president from the HTML
        '''

        jobs = self._soup.findAll("th",
                                  colspan="2",
                                  style="text-align:center;background:lavender;line-height:normal;padding:0.2em 0.2em")
        return [clean_extra_spaces(i.text) for i in jobs]

    def parse_jobs_dates(self):
        '''
        Method for parsing the start and end dates of the government positions held by the president from the HTML
        '''

        dates = self._soup.findAll("td",
                                   colspan="2",
                                   style="text-align:center;border-bottom:none")
        return [extract_dates(i.text) for i in dates]

    def parse_party(self):
        '''
        Method for parsing the party of the president from the HTML 
        '''

        header = self._soup.find(
            "th", text=re.compile("\s*(Political party)\s*"))
        party = header.findNextSibling(name="td").text.strip()
        return re.findall("([A-Za-z]+)", party)[0]

    def parse_birth_death(self):
        '''
        Method for parsing the the birth date and death date of the president from the HTML 
        '''

        b_header = self._soup.find("th", text=re.compile("\s*(Born)\s*"))
        born = b_header.findNextSibling(name="td").text.strip()
        born = re.findall("([A-Za-z]+\s\d+,\s\d{4})", born)[0]

        d_header = self._soup.find("th", text=re.compile("\s*(Died)\s*"))
        if d_header:
            died = d_header.findNextSibling(name="td").text.strip()
            died = re.findall("([A-Za-z]+\s\d+,\s\d{4})", died)[0]

        # return None if president is still alive
        else:
            died = None
        return born, died

    def compile_jobs(self):
        '''
        Method for creating a list of objects representing government jobs held by the president
        '''

        govt_jobs = self.parse_jobs()
        govt_jobs_dates = self.parse_jobs_dates()
        job_list = []
        for i in range(len(govt_jobs)):
            try:
                job_list.append({
                    "title": govt_jobs[i],
                    "start": govt_jobs_dates[i][0],
                    "end": govt_jobs_dates[i][1]
                })
            except:
                pass
        return job_list

    def download_image(self, fpath):
        '''
        Method for downloading the presidential portrait from the HTML 

        Parameters
        -----------
        fpath: file path to save image to
        '''

        base = self._soup.findAll("img")[0].attrs["src"]
        url = "https://" + re.findall("upload.+jpg", base)[0]
        urllib.request.urlretrieve(url, fpath)

    def compile_president(self):
        '''
        Method that returns a dictionary containing pertinent presidential information
        '''

        return {
            "number": self._num,
            "name": self._name,
            "party": self._party,
            "born": self._born,
            "died": self._died,
            "jobs": self._job_list
        }
