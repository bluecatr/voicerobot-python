#coding:utf-8
"""
    The Base Mic class handles all interactions with the microphone and speaker.
"""
import audioop
import logging
import pyaudio
import tempfile
import threading
import wave

from robot import configuration
from robot.ear import AbstractMIC
from robot.mouth import mouth


class BaseMic(AbstractMIC):
    
    SLUG = "base-mic"

#     lock = threading.RLock()
    def __init__(self, stt_engine):
        """
        Initiates the BaseMic instance.

        Arguments:
        passive_stt_engine -- performs STT while Robot is in passive listen
                              mode
        stt_engine -- performs STT while Robot is in active listen
                            mode
        """
        self._logger = logging.getLogger(__name__)
        self.stt_engine = stt_engine
        self._logger.info("Initializing PyAudio. ALSA/Jack error messages " +
                          "that pop up during this process are normal and " +
                          "can usually be safely ignored.")
        self._audio = pyaudio.PyAudio()
        self._logger.info("Initialization of PyAudio completed.")
        

    def __del__(self):
        self._audio.terminate()

    def getScore(self, data):
        rms = audioop.rms(data, 2)
        score = rms / 3
        return score

    def fetchThreshold(self):

        # TODO: Consolidate variables from the next three functions
        THRESHOLD_MULTIPLIER = 1.8
        RATE = 16000
        CHUNK = 1024

        # number of seconds to allow to establish threshold
        THRESHOLD_TIME = 1

        # prepare recording stream
        stream = self._audio.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=RATE,
                                  input=True,
                                  frames_per_buffer=CHUNK)


        # stores the audio data
        frames = []

        # stores the lastN score values
        lastN = [i for i in range(20)]

        # calculate the long run average, and thereby the proper threshold
        for i in range(0, RATE / CHUNK * THRESHOLD_TIME):
            try:
                data = stream.read(CHUNK)
                frames.append(data)

                # save this data point as a score
                lastN.pop(0)
                lastN.append(self.getScore(data))
                average = sum(lastN) / len(lastN)

            except Exception, e:
                self._logger.warning(e)
                continue

        stream.stop_stream()
        stream.close()

        # this will be the benchmark to cause a disturbance over!
        THRESHOLD = average * THRESHOLD_MULTIPLIER

        return THRESHOLD

    def passiveListen(self,passive_stt_engine, PERSONA):
        """
        Listens for PERSONA in everyday sound. Times out after LISTEN_TIME, so
        needs to be restarted.
        
        Arguments:
        passive_stt_engine -- performs STT while Robot is in passive listen
                              mode
        """
#         self.lock.acquire(1)
        
        THRESHOLD_MULTIPLIER = 2.5
        RATE = 16000
        CHUNK = 1024

        # number of seconds to allow to establish threshold
        THRESHOLD_TIME = 1

        # number of seconds to listen before forcing restart
        LISTEN_TIME = 10
        
        # prepare recording stream
        stream = self._audio.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=RATE,
                                  input=True,
                                  frames_per_buffer=CHUNK)

        # stores the audio data
        frames = []

        # stores the lastN score values
        lastN = [i for i in range(30)]

        didDetect = False

        # calculate the long run average, and thereby the proper threshold
        for i in range(0, RATE / CHUNK * THRESHOLD_TIME):

            try:
                data = stream.read(CHUNK)
                frames.append(data)

                # save this data point as a score
                lastN.pop(0)
                lastN.append(self.getScore(data))
                average = sum(lastN) / len(lastN)

                # this will be the benchmark to cause a disturbance over!
                THRESHOLD = average * THRESHOLD_MULTIPLIER

                # save some memory for sound data
                frames = []

                # flag raised when sound disturbance detected
                didDetect = False
            except Exception, e:
                self._logger.warning(e)
                pass

        # start passively listening for disturbance above threshold
        for i in range(0, RATE / CHUNK * LISTEN_TIME):

            try:
                data = stream.read(CHUNK)
                frames.append(data)
                score = self.getScore(data)

                if score > THRESHOLD:
                    didDetect = True
                    break
            except Exception, e:
                self._logger.warning(e)
                continue

        # no use continuing if no flag raised
        if not didDetect:
            print "No disturbance detected"
            try:
                stream.stop_stream()
                stream.close()
            except Exception, e:
                self._logger.warning(e)
                pass
            return (None, None)

        # cutoff any recording before this disturbance was detected
        frames = frames[-20:]

        # otherwise, let's keep recording for few seconds and save the file
        DELAY_MULTIPLIER = 1
        for i in range(0, RATE / CHUNK * DELAY_MULTIPLIER):

            try:
                data = stream.read(CHUNK)
                frames.append(data)
            except Exception, e:
                self._logger.warning(e)
                continue

        # save the audio data
        try:
            stream.stop_stream()
            stream.close()
        except Exception, e:
            self._logger.warning(e)
            pass
        #self.lock.release()
        
        with tempfile.NamedTemporaryFile(mode='w+b') as f:
            wav_fp = wave.open(f, 'wb')
            wav_fp.setnchannels(1)
            wav_fp.setsampwidth(pyaudio.get_sample_size(pyaudio.paInt16))
            wav_fp.setframerate(RATE)
            wav_fp.writeframes(''.join(frames))
            wav_fp.close()
            f.seek(0)
            frames = []
            # check if PERSONA was said
            transcribed = passive_stt_engine.transcribe(f)

        if PERSONA in transcribed:
            return (THRESHOLD, PERSONA)


        return (False, transcribed)


    def activeListen(self, THRESHOLD=None):
        """
            Records until a second of silence or times out after 12 seconds

            Returns a list of the matching options or None
        """
        RATE = 16000
        CHUNK = 1024
        LISTEN_TIME = 12

        # check if no threshold provided
        if THRESHOLD is None:
            print "THRESHOLD is None"
            THRESHOLD = self.fetchThreshold()

        # prepare recording stream
        stream = self._audio.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=RATE,
                                  input=True,
                                  frames_per_buffer=CHUNK)
        

        self.Pixels.off()
        self.Pixels.listen()
        mouth.play(configuration.data('audio', 'beep_hi.wav'))

        frames = []
        # increasing the range # results in longer pause after command
        # generation
        lastN = [THRESHOLD * 1.2 for i in range(50)]

        for i in range(0, RATE / CHUNK * LISTEN_TIME):
            try:
                data = stream.read(CHUNK)
                frames.append(data)
                score = self.getScore(data)

                lastN.pop(0)
                lastN.append(score)

                average = sum(lastN) / float(len(lastN))

                # TODO: 0.8 should not be a MAGIC NUMBER!
                if average < THRESHOLD * 0.8:
                    break
            except Exception, e:
                self._logger.warning(e)
                continue

        mouth.play(configuration.data('audio', 'beep_lo.wav'))
        self.Pixels.off()
        
        # save the audio data
        try:
            stream.stop_stream()
            stream.close()
        except Exception, e:
            self._logger.warning(e)
            pass
        
        with tempfile.SpooledTemporaryFile(mode='w+b') as f:
            wav_fp = wave.open(f, 'wb')
            wav_fp.setnchannels(1)
            wav_fp.setsampwidth(pyaudio.get_sample_size(pyaudio.paInt16))
            wav_fp.setframerate(RATE)
            wav_fp.writeframes(''.join(frames))
            wav_fp.close()
            f.seek(0)
            frames = []
            return self.stt_engine.transcribe(f)

