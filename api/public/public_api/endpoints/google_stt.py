from io import BytesIO

from speech_recognition import AudioFile, Recognizer

from selene.api import PublicEndpoint


class GoogleSTTEndpoint(PublicEndpoint):
    """ Endpoint to send a flac audio file with voice and get back a utterance"""
    def __init__(self):
        super(GoogleSTTEndpoint, self).__init__()
        self.google_stt_key = self.config['GOOGLE_STT_KEY']
        self.recognizer = Recognizer()

    def post(self):
        lang = self.request.args['lang']
        limit = int(self.request.args['limit'])
        audio = self.request.data
        # We need to replicate the first 16 bytes in the audio due a bug with the speech recognition library that
        # removes the first 16 bytes from the flac file we are sending
        with AudioFile(BytesIO(audio[:16] + audio)) as source:
            data = self.recognizer.record(source)
            response = self.recognizer.recognize_google(data, key=self.google_stt_key, language=lang, show_all=True)
            if isinstance(response, dict):
                alternative = response.get("alternative")
                # Sorting by confidence:
                alternative = sorted(alternative, key=lambda alt: alt['confidence'], reverse=True)
                alternative = [alt['transcript'] for alt in alternative]
                # Return n transcripts with the higher confidence. That is useful for the case when send a ambiguous
                # voice file and the correct utterance is not the utterance with highest confidence and the API client
                # is interested in test the utterances found.
                result = alternative if len(alternative) <= limit else alternative[:limit]
            else:
                result = []
        return result


