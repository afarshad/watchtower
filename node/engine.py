import numpy as np
import re

class MeasurementEngine(object):
	_stats=dict()
	videoQuality=float()

	def __init__(self):
		_stats={'min_bitrate': None,
				'max_bitrate': None,
				'avg_bitrate': None,
				'avg_videoQuality': None,
				'avg_switchingImpact': None,
				'no_changes': None,
				'moving_avg_videoBitrate': list(),
				'moving_avg_videoQuality': list(),
				'moving_avg_switchingImpact': list(),
				'videoBitrate': list()
		}
		videoQuality=0.0


	def _getVideoQuality(self, video_resolution, video_bitrate):
		"""
			video_bitrate: Video Bitrate, shows video compression bitrate like 200kbps
			video_resolution: Video Resolution like 720p or 1080p
			Return: videoQuality based on the work."""

		if video_resolution == 720 and video_bitrate < 2000 :
			self.videoQuality=-4.85*power(video_bitrate,-0.647)+1.011
		if video_resolution == 1080 :
			self.videoQuality=-3.035*power(video_bitrate,-0.5061)+1.022
		if video_resolution == 360 and video_bitrate < 1000 :
			self.videoQuality=-17.53*power(video_bitrate,-1.048)+0.9912
		return

	def calculate_stats(self):
		self._stats['min_bitrate']=np.amin(slef._stats['videoBitrate'])

	def _getSwitchingImpact(self,start_time,curr_time,br_before,br_after):

		""" It returns the impact factor given
		the start time stamp for the switching,
		current time of the video playing(time),
		video bitrate before switching (br_before)
		and video bitrate after switching (br_after)."""

		return(np.absolute(br_after-br_before)*np.exp(-0.015*(curr_time-start_time)))

	 # def get_changes(self, list_):
		# """Count the number of changes in a list object."""
		# prev = list_[0]
		# count = 0
		# for item in list_[1:]:
		# 	if not item == prev:
		# 		count += 1
		# 	prev = item
		# return count
