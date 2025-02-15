import wave
import pyaudio
import threading
import sys

CHUNK = 1024

def play_audio(audio_file, channel_map):
	stream_info = pyaudio.PaMacCoreStreamInfo(
			flags=pyaudio.PaMacCoreStreamInfo.paMacCorePlayNice,
			channel_map=channel_map)

	with wave.open(audio_file, 'rb') as wf:
		p = pyaudio.PyAudio()

		stream = p.open(format=p.get_format_from_width(wf.getsampwidth()), channels=wf.getnchannels(), rate=wf.getframerate(), output_host_api_specific_stream_info=stream_info, output=True)
		while len(data := wf.readframes(CHUNK)):
			stream.write(data)

		stream.close()
		p.terminate()

class StoppableThread(threading.Thread):
  def __init__(self, *args, **keywords):
    threading.Thread.__init__(self, *args, **keywords)
    self.killed = False

  def start(self):
    self.__run_backup = self.run
    self.run = self.__run      
    threading.Thread.start(self)

  def __run(self):
    sys.settrace(self.globaltrace)
    self.__run_backup()
    self.run = self.__run_backup

  def globaltrace(self, frame, event, arg):
    if event == 'call':
      return self.localtrace
    else:
      return None

  def localtrace(self, frame, event, arg):
    if self.killed:
      if event == 'line':
        raise SystemExit()
    return self.localtrace

  def kill(self):
    self.killed = True