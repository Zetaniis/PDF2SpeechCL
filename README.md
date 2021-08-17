# PDF2SpeechCL

## Desc
Program generating speech audio files from input files. Command line version

## Features
- choose input file anywhere
- generate audio file anywhere
- limit the amount of content extracted
- limit the number of parts generated for every audio file
- choose audio generator and voice
- choose audio file format
- modify bitrate of an audio file
- support for english language only, you can try to run other languages with pytts 

#### Supported input files: 
- PDF
- EPUB
- TXT (utf-8 encoding)

#### Available text to speech generators:
- Google text to speech - featuring english only with accents
- Pyttsx3 - featuring voices installed locally on the machine

## Example usage
Use _test.pdf_ and generate audio file in the same folder with default arguments. Caution: this command will generate whole file to one audio file. To limit the pages per audio file, use _-lp_
```BASH
PDF2Speech test.pdf
```
Use _test.pdf_ file contained in the _files_ folder and generate audio file in the same directory as input file. Use only first 5 pages and change format of audio file to _wav_.
```
PDF2Speech ".\files\test.pdf" -p 0 5 -f wav
```
Use file _test.pdf_ and generate audio file in _audio_ folder named _test_. Use _gtts_ generator and use voice number _4_.
```
PDF2Speech "test.pdf" ".\audio\test" -t gtts -v 4
```
Use quotation marks for input and audio file if the program returns file not found error.
If you prefer to use python files rather than release version, substitute:
```
PDF2Speech
```
to
```
python main.py
```
## Arguments breakdown:
Also shown with --help argument
```
positional arguments:
  source                link to input file
  destination           target link to audio file (optional, if not inputted program will use source link) 

optional arguments:
  -h, --help            show this help message and exit
  -p PART [PART ...], --part PART [PART ...]
                        convert one part for one argument, range for two arguments (part is equivalent to page for pdf files, chapters for epub files, lines for txt files)
  -lp LIMITP, --limitp LIMITP, --limitpart LIMITP
                        limit number of parts per audio file
  -o OPTIONS [OPTIONS ...], --options OPTIONS [OPTIONS ...]
                        advanced options for file text extractors; please refer to https://github.com/jsvine/pdfplumber for options regarding pdf files(under extract_text)
  -d, --debug           shows raw text data from source file
  -t {pytts,gtts}, --tspeech {pytts,gtts}
                        type of audio generator
  -v VOICE, --voice VOICE
                        set a voice from the list
  -f {mp3,wav}, --format {mp3,wav}
                        set audio file format
  -b BITRATE, --bitrate BITRATE
                        set audio file bitrate
```


## Additional pdf options:
While extracting data from pdf file, text can lose some readability. If any problems arise while listening to audio file eg. the speaker makes long pauses for every letter spoken or speaks without breaks, use _-d_ (debug) to find out about the state of raw text that is prepared for speech generation. Use _-o_ (option) argument to modify the extraction of text from pdf file so that the text looks readable.
Current supported options come from pdf extractor, pdfplumber:
- x_tolerance (default 3)
- y_tolerance (default 3)

For more information and all supported options see https://github.com/jsvine/pdfplumber (under extract_text)


## Release
[All releases](https://github.com/Zetaniis/PDF2SpeechCL/releases)

Requirements:
- Microsoft Visual C redistributable

Optional:
- [ffmpeg](https://www.ffmpeg.org/download.html) - for bitrate modification (be sure to add it to PATH)

## Packages
Main packages used in this application:
- [pdfplumber](https://github.com/jsvine/pdfplumber)
- [beautifulsoup4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [ebooklib](https://github.com/aerkalov/ebooklib)
- [pyttsx3](https://pypi.org/project/pyttsx3/)
- [gtts](https://gtts.readthedocs.io/en/latest/)
- [pydub](https://github.com/jiaaro/pydub)
 
