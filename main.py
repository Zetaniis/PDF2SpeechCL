import math
import os
import argparse

import re

import openingFormats as oo
import speechOptions as so

from pydub import AudioSegment


class Main:
    def __init__(self):
        """input file variables"""
        self.inputFile = None

        self.inputFileLink = None
        self.inputFileDir = None
        self.inputFileName = None
        self.inputFileType = None

        """audio file variables"""
        self.audioFileLink = None
        self.audioFileName = ""
        self.audioFileType = None
        self.audioFinalLink = None
        self.audioBitrate = "96k"

        """text processing variables"""
        # parts are different chunks of text repective to input file; for pdf file part is equivalent to all content
        # from one page, for epub - one whole chapter, for txt - one line of text
        self.filePart = None

        # self.regex = r'([A-z][^.!?]*[.!?]*"?)'
        # self.match = []

        self.currentPartNum = 0
        self.partNumMax = 0
        # self.textListNum = 0
        # self.pageTextList = []
        self.finalText = ""

        self.partsToConvertCount = None
        self.startPartNum = None
        self.endPartNum = None
        # self.startListNum = None
        # self.endListNum = None

        self.partLimit = 9999999999999
        # self.charLimit = 9999999999999

        self.openingInputVariables = [self.inputFile, self.partNumMax, self.filePart]

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
        epilog = "Available text to speech generators (input only number to choose): \n"
        # getting all available voices to dictionary - {voice (string):{number (int): object}}
        for k in self.speechMethods:
            self.speechOptions[k], text = self.speechMethods.get(k).getVoices()
            epilog = "".join([epilog, " ", k, "\n", text])

        self.parser = argparse.ArgumentParser(description=description, epilog=epilog, formatter_class=argparse.RawTextHelpFormatter)

        self.parser.add_argument("input", help="link to input file")
        self.parser.add_argument("output", nargs="?", help="target path link to audio file (optional, if not inputted "
                                                                "program will use input file path link)")
        self.parser.add_argument("-p", "--part", nargs="+", help="convert one part for one argument, range for two "
                                                                 "arguments (part is equivalent to page for pdf "
                                                                 "files, chapters for epub files, lines for txt "
                                                                 "files)")
        self.parser.add_argument("-lp", "--limitp", "--limitpart", help="limit number of parts per audio file")
        self.parser.add_argument("-o", "--options", nargs="+", help="advanced options for file text extractors; please "
                                                                    "refer to https://github.com/jsvine/pdfplumber for "
                                                                    "options regarding pdf files (under extract_text)")
        self.parser.add_argument("-d", "--debug", action="store_true", default=False, help="shows raw text data from input file")
        # self.parser.add_argument("-lc", "-limitc", "-limitchar", "-limitcharacter", nargs=1, help="limit number of characters per audio file")
        self.parser.add_argument("-t", "--tspeech", choices=["pytts", "gtts"], default="pytts", help="type of audio generator")
        self.parser.add_argument("-v", "--voice", nargs="+", default=["0"], help="set a voice from the list")
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

        print("Generating " + str(math.ceil((self.partsToConvertCount / self.partLimit))) + " audio files.")

        while self.partsToConvertCount:
            self.finalText = ""
            # adding text to finalText until part limit for audio file hits
            for _ in range(self.partLimit):
                self.loadPartProcess()
                if self.args.debug:
                    print("--DEBUG--")
                    print("".join(["--PART: ", str(self.currentPartNum)]))
                    print("".join(["--CONTENTS--\n", self.filePart]))
                self.finalText = " ".join([self.finalText, self.filePart])
                self.currentPartNum += 1
                self.partsToConvertCount -= 1
                if self.partsToConvertCount < 1:
                    break
            self.finalText = self.finalText.replace('\n', " ")
            self.audioFinalLink = self.audioFileLink + "_" + str(self.currentPartNum) + "." + self.audioFileType
            print("Saving audio file to: ", self.audioFinalLink)
            # converting to integer that is used to find a list of language, accent OR passing the string or list directly
            voiceChoice = [int(self.args.voice[0])] if self.args.voice[0].isdigit() else self.args.voice
            # audio file creation
            self.speechMethod.speechProcessing(self.finalText, self.audioFinalLink, self.speechOptions.get(self.args.tspeech).get(voiceChoice[0], voiceChoice))
            self.audioConversion()

    def filePathsFormatting(self):
        """setting path links for input and output file"""
        if not self.args.input:
            raise Exception("Error: No input file")
        else:
            self.inputFileLink = self.args.input

        # getting absoulte paths to input and output file and setting path oriented variables
        self.inputFileLink = os.path.abspath(self.inputFileLink)

        self.inputFileDir = os.path.dirname(self.inputFileLink)
        file = os.path.basename(self.inputFileLink)
        self.inputFileName, self.inputFileType = os.path.splitext(file)

        if self.args.output:
            self.audioFileLink = self.args.output
        else:
            self.audioFileLink = "".join([self.inputFileDir, os.path.sep, self.inputFileName])

        self.audioFileLink = os.path.abspath(self.audioFileLink)

    def fileProcessing(self):
        """loading input file"""
        self.openingMethod = self.openingMethods.get(self.inputFileType, oo.Txt(*self.openingInputVariables))
        self.inputFile, self.partNumMax = self.openingMethod.loadFileFromLoc(self.inputFileLink)

    def otherArgsInit(self):
        """setting other arguments from command line to variables"""
        if not self.args.part:
            self.startPartNum = 0
            self.endPartNum = self.partNumMax
        elif len(self.args.part) < 2:
            self.startPartNum = int(self.args.part[0])
            self.endPartNum = int(self.args.part[0]) + 1
        else:
            self.startPartNum = int(self.args.part[0])
            self.endPartNum = int(self.args.part[1])

        self.startPartNum = max(min(self.startPartNum, self.partNumMax - 1), 0)
        self.endPartNum = max(min(self.endPartNum, self.partNumMax - 1), self.startPartNum + 1)
        self.currentPartNum = self.startPartNum

        self.speechMethod = self.speechMethods[self.args.tspeech]

        self.audioFileType = self.args.format

        if self.args.limitp:
            self.partLimit = int(self.args.limitp)

        # if self.args.limitc:
        #     self.charLimit = int(self.args.limitc[0])

        self.partsToConvertCount = self.endPartNum - self.startPartNum

        # if no partLimit inputted, one chapter per audio file is set
        if not self.args.limitp and self.inputFileType == ".epub":
            self.partLimit = 1

        self.audioBitrate = self.args.bitrate

        if self.args.options:
            tmp = "".join(self.args.options)
            for options in tmp.split(","):
                key, value = options.split("=")
                self.extractorOptions[key] = int(value)

    def loadPartProcess(self):
        """loading part of a file"""
        assert self.inputFile
        assert self.openingMethod
        self.filePart = self.openingMethod.loadPart(self.currentPartNum, self.extractorOptions)
        if not self.filePart:
            self.filePart = ""

    def audioConversion(self):
        """changing bitrate"""
        try:
            sound = AudioSegment.from_file(self.audioFinalLink)
            sound.export(self.audioFinalLink, format=self.audioFileType, bitrate=self.audioBitrate)
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
    session = Main()
