from threading import Timer, Thread

class Session(object):

	def __init__(self, mpd, start_time):
		self.mpd = mpd
		self.start_time = start_time
		self.elapsed_time = 0
		#self.timer()

	def timer(self):
		self.elapsed_time += 1
		t = Timer(1.0, self.timer)
		t.start()