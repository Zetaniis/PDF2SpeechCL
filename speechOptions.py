"""classes handling audio generation and return information on all available voices"""
import pyttsx3
import gtts


class SpeechOptions:
    class Pyttsx3:
        def __init__(self):
            self.engine = pyttsx3.init()

        def speechProcessing(self, finalText, voiceFile, option):
            self.engine.setProperty("voice", option)
            self.engine.save_to_file(finalText, voiceFile)
            self.engine.runAndWait()

        def closeSpeech(self):
            pass

        def getVoices(self):
            voices = self.engine.getProperty('voices')
            voicesStr = ""
            speechOptions = dict()
            for i, v in enumerate(voices):
                voicesStr = "".join([voicesStr, "   ", str(i), ": ", v.name, "\n"])
                speechOptions[i] = v.id
            return [speechOptions, voicesStr]

    class GTTS:
        def __init__(self):
            pass

        def speechProcessing(self, finalText, voiceFile, option):
            if len(option) > 1:
                tts = gtts.gTTS(finalText, lang=option[0], tld=option[1])
            else:
                tts = gtts.gTTS(finalText, lang=option[0])
            tts.save(voiceFile)

        def closeSpeech(self):
            pass

        def getVoices(self):
            voicesStr = "Input language id from: " \
                        + str(gtts.lang.tts_langs()) + '\n' + \
                        "From https://gtts.readthedocs.io/en/latest/module.html#languages-gtts-lang: \n" \
                        "For a given language, Google Translate text-to-speech can speak in different local ‘accents’ " \
                        "depending on the Google domain (google.<tld>) of the request \n" \
                        "Some voices that are proven to work (input only number from table below): \n" \
                        "   0: English (United States) (default)\n" \
                        "   1: English (Australia) \n" \
                        "   2: English (United Kingdom) \n" \
                        "   3: English (Canada) \n" \
                        "   4: English (India) \n" \
                        "   5: English (Ireland) \n" \
                        "   6: English (South Africa) \n" \
                        "   7: French (Canada) \n" \
                        "   8: French (France)  \n" \
                        "   9: Mandarin (China Mainland) \n" \
                        "   10: Portuguese (Brazil) \n" \
                        "   11: Portuguese (Portugal) \n" \
                        "   12: Spanish (Mexico) \n" \
                        "   13: Spanish (Spain) \n"

            speechOptions = {
                0: ["en", "com"],
                1: ["en", "com"],
                2: ["en", "co.uk"],
                3: ["en", "ca"],
                4: ["en", "co.in"],
                5: ["en", "ie"],
                6: ["en", "co.za"],
                7: ["fr", "ca"],
                8: ["fr", "fr"],
                9: ["zh-CN", "any"],
                10: ["pt", "com.br"],
                11: ["pt", "pt"],
                12: ["es", "com.mx"],
                13: ["es", "es"]
            }
            return [speechOptions, voicesStr]
