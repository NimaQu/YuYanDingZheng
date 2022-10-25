import azure.cognitiveservices.speech as sdk
import logging


class TTS:
    def __init__(self, subscription_key, region, language):
        self.speech_config = sdk.SpeechConfig(subscription=subscription_key, region=region)
        self.speech_config.speech_synthesis_language = language
        self.speech_config.set_speech_synthesis_output_format(sdk.SpeechSynthesisOutputFormat.Ogg24Khz16BitMonoOpus)
        self.speech_synthesizer = sdk.SpeechSynthesizer(speech_config=self.speech_config)

    def to_file(self, text):
        """performs speech synthesis to an mp3 file"""
        # Creates an instance of a speech config with specified subscription key and service region.
#        speech_config = sdk.SpeechConfig(subscription="01e8c21395cb450da22672aa2bc07a99", region="eastus")
        # Sets the synthesis output format.
        # The full list of supported format can be found here:
        # https://docs.microsoft.com/azure/cognitive-services/speech-service/rest-text-to-speech#audio-outputs
        # speech_config.set_speech_synthesis_output_format(sdk.SpeechSynthesisOutputFormat.Ogg24Khz16BitMonoOpus)
        # Creates a speech synthesizer using file as audio output.
        # Replace with your own audio file name.
        file_name = "tmp/" + str(hash(text))
        file_config = sdk.audio.AudioOutputConfig(filename=file_name)
        speech_synthesizer = sdk.SpeechSynthesizer(speech_config=self.speech_config, audio_config=file_config)
        result = speech_synthesizer.speak_text_async(text).get()
        # Check result
        if result.reason == sdk.ResultReason.SynthesizingAudioCompleted:
            logging.info("Speech synthesized to [{}] for text [{}]".format(file_name, text))
            return
        elif result.reason == sdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            logging.error("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == sdk.CancellationReason.Error:
                logging.error("Error details: {}".format(cancellation_details.error_details))