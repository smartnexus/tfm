import wave
import pyaudio
import threading
import sys
import time
import numpy as np

CHUNK = 1024

def input(stream, data_list, rate, seconds):
  for _ in range(0, int(rate / CHUNK * seconds)):
    data_list.append(stream.read(CHUNK))

def stream_audio(seconds, delay):
  WIDTH = 2
  CHANNELS = 1
  RATE = 44100

  p = pyaudio.PyAudio()

  stream = p.open(format=p.get_format_from_width(WIDTH), channels=CHANNELS, rate=RATE, input=True, output=True, frames_per_buffer=CHUNK)

  data_list = []
  in_thread = threading.Thread(target=input, args=(stream, data_list, RATE, seconds))
  in_thread.start()

  time.sleep(delay)

  for i in range(0, int(RATE / CHUNK * seconds)):
    stream.write(data_list[i], CHUNK)  

  stream.stop_stream()
  stream.close()

  p.terminate()

def play_audio_with_error(audio_file, channel_map, error_prob):
  stream_info = pyaudio.PaMacCoreStreamInfo(
      flags=pyaudio.PaMacCoreStreamInfo.paMacCorePlayNice,
      channel_map=channel_map)

  with wave.open(audio_file, 'rb') as wf:
    loop_count = wf.getnframes() // CHUNK
    distrib = np.random.binomial(1, 1 - error_prob, loop_count)
    p = pyaudio.PyAudio()

    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()), channels=wf.getnchannels(), rate=wf.getframerate(), output_host_api_specific_stream_info=stream_info, output=True)

    for i in range(loop_count):
      data = wf.readframes(CHUNK)
      if distrib[i] == 1:
        stream.write(data)
      else:
        stream.write(b'\x00' * len(data))

    stream.close()
    p.terminate()

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