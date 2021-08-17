import math
import os
import argparse

import re

import openingFormats as oo
import speechOptions as so

from pydub import AudioSegment

# TODO: improve choosing speech type for google text to speech
# TODO: add more voices from pyttsx3 (sapi5)
# TODO: decide how to handle stripping newlines from text


class main:

    def __init__(self):
        """init"""

        """input file variables"""
        self.inputFile = None

        self.inputFileLink = None
        self.inputFileDir = None
        self.inputFileName = None
        self.inputFileType = None

        """audio file variables"""
        self.voiceFileLink = None
        self.voiceFileName = ""
        self.voiceFileType = None
        self.voiceFinalLink = None
        self.voiceBitrate = "96k"

        """text processing variables"""
        self.filePage = None

        # self.regex = r'([A-z][^.!?]*[.!?]*"?)'
        # self.match = []

        self.currentPageNum = 0
        self.pageNumMax = 0
        # self.textListNum = 0
        # self.pageTextList = []
        self.finalText = ""

        self.pagesToConvertCount = None
        self.startPageNum = None
        self.endPageNum = None
        # self.startListNum = None
        # self.endListNum = None

        self.pageLimit = 99999999
        self.charLimit = 99999999

        self.openingInputVariables = [self.inputFile, self.pageNumMax, self.filePage]

        self.openingMethods = {".pdf": oo.Pdf(*self.openingInputVariables),
                               ".txt": oo.Txt(*self.openingInputVariables),
                               ".epub": oo.Epub(*self.openingInputVariables)}

        self.openingMethod = None
        self.extractorOptions = dict()

        self.speechMethods = {"pytts": so.SpeechOptions.Pyttsx3(),
                              "gtts": so.SpeechOptions.GTTS()}

        self.speechMethod = None
        self.speechOptions = dict()

        """parser init"""
        description = "Program generating speech audio files from txt, pdf and epub files. Currently supporting " \
                      "Google Text to Speech (gtts) and local text to speech generators (pytts) "
        epilog = "Available text to speech generators: \n"
        for k in self.speechMethods:
            self.speechOptions[k], text = self.speechMethods.get(k).getVoices()
            epilog = "".join([epilog, " ", k, "\n", text])

        self.parser = argparse.ArgumentParser(description=description, epilog=epilog, formatter_class=argparse.RawTextHelpFormatter)

        self.parser.add_argument("source", help="link to input file")
        self.parser.add_argument("destination", nargs="?", help="target link to audio file (optional, if not inputted "
                                                                "program will use source link)")
        # self.parser.add_argument("-vl", "--voicelist", action=self.returnVoiceListAction(self.speechMethods), default=1, help="list all available voices")
        self.parser.add_argument("-p", "--part", nargs="+", help="convert one part for one argument, range for two "
                                                                 "arguments (part is equivalent to page for pdf "
                                                                 "files, chapters for epub files, lines for txt "
                                                                 "files)")
        self.parser.add_argument("-lp", "--limitp", "--limitpage", help="limit number of parts per audio file")
        self.parser.add_argument("-o", "--options", nargs="+", help="advanced options for file text extractors; please "
                                                                    "refer to https://github.com/jsvine/pdfplumber for "
                                                                    "options regarding pdf files (under extract_text)")
        self.parser.add_argument("-d", "--debug", action="store_true", default=False, help="shows raw text data from source file")
        # self.parser.add_argument("-lc", "-limitc", "-limitchar", "-limitcharacter", nargs=1, help="limit number of characters per audio file")
        self.parser.add_argument("-t", "--tspeech", choices=["pytts", "gtts"], default="pytts", help="type of audio generator")
        self.parser.add_argument("-v", "--voice", default=0, help="set a voice from the list")
        # self.parser.add_argument("-c", "-chapters", help="split audio files by chapters (epub only)")
        self.parser.add_argument("-f", "--format", choices=["mp3", "wav"], default="mp3", help="set audio file format")
        self.parser.add_argument("-b", "--bitrate", default="96k", help="set audio file bitrate")
        
        try:
            self.args = self.parser.parse_args()
        except ValueError as a:
            if "invalid nargs value" in a.__str__():
                print("Value error: wrong number of input arguments")

        self.programLoop()

    def programLoop(self):
        """loop for generating audio files from designated part with regarding to part limit"""
        self.filePathsFormatting()
        try:
            self.fileProcessing()
        except FileNotFoundError as a:
            print("FileNotFoundError: No such file or directory: " + self.inputFileLink)
            exit()
        self.otherArgsInit()

        print("Generating " + str(math.ceil((self.pagesToConvertCount/self.pageLimit))) + " audio files.")

        while self.pagesToConvertCount:
            self.finalText = ""
            for _ in range(self.pageLimit):
                self.loadPageProcess()
                if self.args.debug:
                    print("--DEBUG--")
                    print("".join(["--PAGE (CHAPTER): ", str(self.currentPageNum)]))
                    print("".join(["--CONTENTS--\n", self.filePage]))
                self.finalText = " ".join([self.finalText, self.filePage])
                self.currentPageNum += 1
                self.pagesToConvertCount -= 1
                if self.pagesToConvertCount < 1:
                    break
            self.finalText = self.finalText.replace('\n', " ")
            # print(self.finalText)
            self.voiceFinalLink = self.voiceFileLink + "_" + str(self.currentPageNum) + "." + self.voiceFileType
            print("Saving audio file to: ", self.voiceFinalLink)
            # print(self.args.tspeech, self.args.voice, self.speechOptions.get(self.args.tspeech), self.speechOptions.get(self.args.tspeech).get(int(self.args.voice)))
            self.speechMethod.speechProcessing(self.finalText, self.voiceFinalLink, self.speechOptions.get(self.args.tspeech).get(int(self.args.voice)))
            self.audioConversion()
            # self.audioConversion(self.args.format)

    def filePathsFormatting(self):
        """setting path links for source and destination file"""
        if not self.args.source:
            raise Exception("Error: No input file")
        else:
            self.inputFileLink = self.args.source

        print(os.getcwd())
        self.inputFileLink = os.path.abspath(self.inputFileLink)

        self.inputFileDir = os.path.dirname(self.inputFileLink)
        file = os.path.basename(self.inputFileLink)
        self.inputFileName, self.inputFileType = os.path.splitext(file)

        # print(self.inputFileDir, self.inputFileName, self.inputFileType)

        if self.args.destination:
            self.voiceFileLink = self.args.destination
        else:
            self.voiceFileLink = "".join([self.inputFileDir, os.path.sep, self.inputFileName])

        # print(self.voiceFileLink)
        self.voiceFileLink = os.path.abspath(self.voiceFileLink)
        # print(self.voiceFileName)

    def fileProcessing(self):
        """loading input file"""
        self.openingMethod = self.openingMethods.get(self.inputFileType, oo.Txt(*self.openingInputVariables))
        self.inputFile, self.pageNumMax = self.openingMethod.loadFileFromLoc(self.inputFileLink)

    def otherArgsInit(self):
        """setting other arguments from command line to variables"""
        if not self.args.part:
            self.startPageNum = 0
            self.endPageNum = self.pageNumMax
        elif len(self.args.part) < 2:
            self.startPageNum = int(self.args.part[0])
            self.endPageNum = int(self.args.part[0]) + 1
        else:
            self.startPageNum = int(self.args.part[0])
            self.endPageNum = int(self.args.part[1])

        self.startPageNum = max(min(self.startPageNum, self.pageNumMax - 1), 0)
        self.endPageNum = max(min(self.endPageNum, self.pageNumMax - 1), self.startPageNum + 1)
        self.currentPageNum = self.startPageNum

        # print(self.startPageNum, self.endPageNum)

        self.speechMethod = self.speechMethods[self.args.tspeech]

        self.voiceFileType = self.args.format

        if self.args.limitp:
            self.pageLimit = int(self.args.limitp)

        # if self.args.limitc:
        #     self.charLimit = int(self.args.limitc[0])

        self.pagesToConvertCount = self.endPageNum - self.startPageNum

        if not self.args.limitp and self.inputFileType == ".epub":
            self.pageLimit = 1

        self.voiceBitrate = self.args.bitrate

        if self.args.options:
            tmp = "".join(self.args.options)
            for options in tmp.split(","):
                key, value = options.split("=")
                self.extractorOptions[key] = int(value)

    def loadPageProcess(self):
        """loading part of a file"""
        assert self.inputFile
        assert self.openingMethod
        self.filePage = self.openingMethod.loadPage(self.currentPageNum, self.extractorOptions)
        if not self.filePage:
            self.filePage = ""

    def audioConversion(self):
        """changing bitrate"""
        try:
            sound = AudioSegment.from_file(self.voiceFinalLink)
            sound.export(self.voiceFinalLink,  format=self.voiceFileType, bitrate=self.voiceBitrate)
        except RuntimeError as err:
            if "Couldn't find ffmpeg" in err.__str__():
                print("Warning: ffmpeg not installed, direct audio manipulation omitted. To resolve this warning, "
                      "install ffpmeg and add it to PATH")
            else:
                raise err

    # """NOT USED FOR NOW"""
    # """data formatting"""
    # def extractSentences(self):
    #     """split text into list of sentences"""
    #     self.pageTextList = re.findall(self.regex, self.filePage)
    #
    # def joinToCharLimit(self):
    #     """split strings of length self.charLimit characters and concatenate neighbouring strings of length self.charLimit characters
    #     after concatenation"""
    #
    #     temp = [x[i:i + self.charLimit].replace('\n', ' ') for x in self.pageTextList for i in range(0, len(x), self.charLimit)]
    #     self.pageTextList = temp
    #
    #     if not len(self.pageTextList) <= 1:
    #         temp = []
    #         nextEl = ""
    #         final = False
    #         generator = iter(self.pageTextList)
    #         for x in generator:
    #             if not final:
    #                 element = x
    #                 try:
    #                     nextEl = next(generator)
    #                 except StopIteration as a:
    #                     pass
    #             else:
    #                 element = nextEl
    #                 nextEl = x
    #             while len(" ".join([element, nextEl])) < self.charLimit:
    #                 element = " ".join([element, nextEl])
    #                 try:
    #                     nextEl = next(generator)
    #                 except StopIteration as a:
    #                     break
    #             final = True
    #             temp.append(element)
    #         self.pageTextList = temp


if __name__ == "__main__":
    session = main()
