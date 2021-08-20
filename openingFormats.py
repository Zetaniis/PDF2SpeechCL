"""classes handling opening different file format and extracting text
shaving methods for loading file from location and accessing the some part of the file"""

import pdfplumber
from bs4 import BeautifulSoup
from ebooklib import epub
import re


class Pdf:
    def __init__(self, file, pageNumMax, filePage):
        self.file = file
        self.pageNumMax = pageNumMax
        self.filePage = filePage

    def loadFileFromLoc(self, fileLink):
        self.file = pdfplumber.open(fileLink).pages
        self.pageNumMax = len(self.file)
        return [self.file, self.pageNumMax]

    def loadPart(self, pageNum, options):
        """convert pdf page with pageNum number with additional options"""
        self.filePage = self.file[pageNum].extract_text(**options)
        if self.filePage:
            self.filePage.replace('\n', " ")
        return self.filePage


class Epub:
    def __init__(self, file, pageNumMax, filePage):
        self.file = file
        self.pageNumMax = pageNumMax
        self.filePage = filePage

    def loadFileFromLoc(self, fileLink):
        self.file = epub.read_epub(fileLink)
        self.pageNumMax = len(self.file.toc)
        result = ""
        # for x in self.file.get_items():
        #     type = x.get_type()
        #     if type == ebooklib.ITEM_DOCUMENT:
        #         soup = BeautifulSoup(x.content, 'lxml')
        #         for child in soup.find_all(
        #                 ['p', 'div', 'h1', 'h2', 'h3', 'h4']
        #         ):
        #         # print(soup.text)
        #         #     print(child.text)
        #             result = result + child.text
                # print(result)
        # print(result)
        # for x in self.file.get_items():
        #     # print(x.title, x.uid)
        #     if x.get_type() == ebooklib.ITEM_NAVIGATION:
        #
        #         # if 'html' in x.href and 'chap' in x.href:
        #         #     print("a")

        # for x in self.file.toc:
        #     a = self.file.get_item_with_href(x.href)
        #     soup = BeautifulSoup(a.content, 'lxml')
        tmp = []*len(self.file.toc)
        for x in self.file.toc:
            soup = BeautifulSoup(self.file.get_item_with_href(x.href).content, 'lxml')
            title = soup.find_all("title")
            for x in title:
                x.extract()
            # fitering out multiple newlines in text
            tmp.append(re.sub(r'\n\s*\n', '\n\n', soup.getText()))
        self.file = tmp
        self.pageNumMax = len(self.file)
        return [self.file, self.pageNumMax]

    def loadPart(self, pageNum, options):
        self.filePage = self.file[pageNum]
        return self.filePage


class Txt:
    def __init__(self, file, pageNumMax, filePage):
        self.file = file
        self.pageNumMax = pageNumMax
        self.filePage = filePage

    def loadFileFromLoc(self, fileLink):
        with open(fileLink,  encoding="utf8") as f:
            self.file = f.readlines()
        self.pageNumMax = len(self.file)
        return [self.file, self.pageNumMax]

    def loadPart(self, pageNum, options):
        return self.file[pageNum]
