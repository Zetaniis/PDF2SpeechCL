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
            tts = gtts.gTTS(finalText, lang=option[0], tld=option[1])
            tts.save(voiceFile)

        def closeSpeech(self):
            pass

        def getVoices(self):
            voicesStr = "   0: English (United States) (default)\n" \
                        "   1: English (Australia) \n" \
                        "   2: English (United Kingdom) \n" \
                        "   3: English (Canada) \n" \
                        "   4: English (India) \n" \
                        "   5: English (Ireland) \n" \
                        "   6: English (South Africa) \n"
            speechOptions = {
                0: ["en", "com"],
                1: ["en", "com"],
                2: ["en", "co.uk"],
                3: ["en", "ca"],
                4: ["en", "co.in"],
                5: ["en", "ie"],
                6: ["en", "co.za"]
            }
            return [speechOptions, voicesStr]
