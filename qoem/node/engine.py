import calendar
import math
import numpy as np
import threading
import re
import time
import state.qoemmongodb as database

class MeasurementEngine_thread(threading.Thread):
    daemon = True
    db=databse()
    def __init__(self,dbName):
        threading.Thread.__init__(self)

    def run(self):
        try:
            MeasurementEngine.update_stats(self)
            time.sleep(1)
        except Exception as e:
            print 'error: ' + str(e)

class MeasurementEngine(object):
	_stats=dict()
	def __init__(self,segmentSize,videoBitrate_list,videoResolution_list,timeStamp):
		_stats={'segmentSize':int(segmentSize),
				'min_bitrate': None,
				'max_bitrate': None,
				'avg_bitrate': None,
				'median_bitrate':None,
				'min_resolution':None,
				'max_resolution':None,
				'median_resolution':None,
				'no_changes': None,
				'noStalls':list(),
				'avg_videoQuality': None,
				'avg_switchingImpact': None,
				'videoBitrate': videoBitrate_list,
				'videoBitrate_expanded':list(),
				'videoQuality':list(),
				'videoResolution':videoResolution_list,
				'videoResolution_expanded':list(),
				'switchingImpact':list(),
				'videoTime':list(),
				'videoTime_expanded':list(), #videoTime for each seconds
				'timeStamp':timeStamp  #list of timestamp received for the urls, timeStamp[0] is for the GET to download MPD.
				# 'moving_avg_videoBitrate': list(),
				# 'moving_avg_videoQuality': list(),
				# 'moving_avg_switchingImpact': list()
				}

	def update_stats(self,database):
		"""
		:param database:
		:return:It updates the database based on the stats information in the engine object.
		"""
		self.calcStats()
		currentTime=calendar.timegm(time.gmtime())
		self._updateSwitchingImpact(self,currentTime)

		self.gets.insert(self._stats)

	def get_playback_bitrate(self, url):
		"""Parse the URL to unreliably(!) determine the playback bitrate."""
		pattern = re.compile(ur'.*\_(.*kbit).*')
		match = re.match(pattern, url)
		bitrate = int(match.group(1).replace('kbit', ''))
		return bitrate or 0

	def _calc_videoTime(self):
		"""

		:return: the video time based on the received timestamps  and segment duration time.
		It assumes that the all segments have the same size.
		"""
		for i in range(len(self._stats['timeStamp'])):
			passedTime=self._stats['segmentSize']*i
			self._stats['videoTime'].append(self._stats['timeStamp'][i]+passedTime)

	def _calc_expanded_array(self):
		for i in range(len(self._stats['timeStamp'])):
			for i in range(self._stats['segmentSize']):
				self._stats['videoTime'].append(self._stats['timeStamp'][i]+passedTime)


	def _calc_noStalls(self):
		"""

		:return: number of times stall have happened
		"""
		#If timeStamp[i+1] > videoTime[i] stall was happened, i is the segment index.
		#TODO add check for duplicate segment requests and so on.
		for i in range(1,len(self._stats['timeStamp'])-1):
			if self._stats['videoTime'][i] < self._stats['timeStamp'][i+1]:
				self._stats['noStalls'].append(1)
			else:
				self._stats['noStalls'].append(0)


	def _calcVideoQuality(self, video_resolution, video_bitrate):
		"""
		video_bitrate: Video Bitrate, shows video compression bitrate like 200kbps
		video_resolution: Video Resolution like 720p or 1080p
		Return: videoQuality.
		"""
		_videoQuality=0.0
		if video_resolution == 720 and video_bitrate < 2000 :
			_videoQuality=-4.85*math.pow(video_bitrate,-0.647)+1.011
		if video_resolution == 1080 :
			_videoQuality=-3.035*math.pow(video_bitrate,-0.5061)+1.022
		if video_resolution == 360 and video_bitrate < 1000 :
			_videoQuality=-17.53*math.pow(video_bitrate,-1.048)+0.9912
		return _videoQuality

	def calcStats(self):
		#Calculate the stats for the video bitrate
		self._stats['min_bitrate']=np.amin(self._stats['videoBitrate'])
		self._stats['max_bitrate']=np.amax(self._stats['videoBitrate'])
		self._stats['median_bitrate']=np.median(self._stats['videoBitrate'])
		#Calculate the stats for the video resolution
		self._stats['min_resolution']=np.amin(self._stats['videoResolution'])
		self._stats['max_resolution']=np.amax(self._stats['videoResolution'])
		self._stats['median_resolution']=np.median(self._stats['videoResolution'])
		#Calculate no of changes in the video bitrates looking into the video bitrate list.
		self._stats['no_changes']=self._getNoBitrateChanges(self._stats['videoBitrate'])
		#Update the videoQuality list
		self._stats['videoQuality']=list(
			self._calcVideoQuality(np.array(self._stats['videoBitrate']),np.array(self._stats['videoResolution']))
		)

		#Update the switching impact


	def _calcSwitchingImpact(self,start_time,curr_time,vq_before,vq_after):

		""" It returns the impact factor given
		the start time stamp for the switching,
		current time of the video playing(time),
		video quality before switching (vq_before)
		and video quality after switching (vq_after)."""
		return(np.absolute(vq_after-vq_before)*np.exp(-0.015*(curr_time-start_time)))

	def _updateSwitchingImpact(self,currentTime):

		br_data=self._stats['videoBitrate']
		sw_index=[]
		#find where switching is happened in the video bitrate list and return the list of index.
		for i in range(1,len(br_data)-2):
			if br_data[i+1] != br_data[i]:
				sw_index.append(i+1)

		if currentTime < long(self._stats['videoTime'][-1]):
			print "current time is not matched with the logs time"
			return
		else:
			end_time=currentTime - long(self._stats['videoTime'][-1])
			#Create an array for each switching happens in the time.
			br_impact=np.zeros((len(sw_index),end_time))
			k=0
			for i in sw_index:
				for j in range(end_time):
					if j < i:
						br_impact[k,j]=0
					else:
						br_impact[k,j]=self._calcSwitchingImpact(
							start_time=self._stats['videoTime'][i],
							curr_time=self._stats['videoTime'][i]+(j-i),
							br_before=self._stats['videoQuality'][i-1],
							br_after=self._stats['videoQuality'][i]
						)
				k=k+1
			final_data=np.zeros(end_time)
			for j in range(br_impact.shape[1]):
				for i in range(br_impact.shape[0]):
					final_data[j]+=br_impact[i][j]
			self._stats['switchingImpact']=list(final_data)


	def _getNoBitrateChanges(self):
		"""Count the number of changes in the list."""

		prev = self._status['videoBitrate'][0]
		count = 0
		for item in self._status['videoBitrate'][1:]:
			if not item == prev:
				count += 1
			prev = item
		return count
