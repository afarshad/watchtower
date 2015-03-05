import calendar
import math
import numpy as np
import threading
import re
import time
# input data from the manager to the engine: timestamp,duration,bitrate,width,height

def handle_this_method_call(_dictionary):
    print 'engine is being called'
    print _dictionary


def add_videoTime(_stats):
    """
    :return: A list of the
    the video time based on the received timestamps and segment duration time.
    It assumes that the all segments have the same size.
    """
    passedTime = 0
    for i in range(0, len(_stats), 1):
        if i is 0:
            passedTime = 0
        else:
            passedTime += _stats[i]['duration']
        _stats[i]['videoTime'] = _stats[i]['timestamp'] + passedTime
    return (_stats)


def test_add_videoTime(_stats):
    _new_stats = add_videoTime(_stats)
    print "New Stats:"
    print  _new_stats


def calc_noStalls(_stats):
    """
    :input: _stats with the video time

    :return: number of times stall have happened
    """
    # If timeStamp[i+1] > videoTime[i] stall was happened, i is the segment index.

    #TODO add check for duplicate segment requests and so on.
    noStalls = 0
    for i in range(1, len(_stats) - 1):
        if _stats[i]['videoTime'] < _stats[i + 1]['timestamp']:
            noStalls += 1
    return noStalls


def calc_videoQuality(_stats):
    """
    video_bitrate: Video Bitrate, shows video compression bitrate like 200kbps
    video_resolution: Video Resolution like 720p or 1080p
    Return: videoQuality.
    """
    _videoQuality = 0.0
    for i in range(0, len(_stats)):
        if _stats[i]['height'] == 720 and _stats[i]['bitrate'] < 2000:
            _videoQuality = -4.85 * math.pow(int(_stats[i]['bitrate']), -0.647) + 1.011

        if _stats[i]['height'] == 1080:
            _videoQuality = -3.035 * math.pow(int(_stats[i]['bitrate']), -0.5061) + 1.022

        if _stats[i]['height'] == 360 and _stats[i]['bitrate'] < 1000:
            _videoQuality = -17.53 * math.pow(int(_stats[i]['bitrate']), -1.048) + 0.9912

    return _videoQuality


def test_calc_videoQuality(_stats):
    print calc_videoQuality(_stats)


def get_minVideoBitrate(_stats):
    """

    :param _stats: It is the list of parameters passed to calculate stats
    :return: minimum video bitrate in the list
    """
    if len(_stats) > 0:
        _minBitrate = min(_stats[:]['bitrate'])
    else:
        _minBitrate = 0
    return _minBitrate


def get_maxVideoBitrate(_stats):
    """

    :param _stats: It is the list of parameters passed to calculate stats
    :return: maximum video bitrate in the list
    """
    if len(_stats) > 0:
        _maxBitrate = max(_stats[:]['bitrate'])
    else:
        _maxBitrate = 0
    return _maxBitrate


def get_noBitrateChanges(_stats):
    """
    :param _stats:
    :return: the number of changes in the video bitrate.
    """
    if len(_stats) <= 0:
        return 0
    prev = _stats[0]['bitrate']
    count = 0
    for i in range(1, len(_stats)):
        if _stats[i]['bitrate'] is not prev:
            count += 1
            prev = _stats[i]['bitrate']
    return count


def calc_weightedAvgBitrate(_stats):
    """

    :param _stats: It gets _stats with updated videoTimestamp
    :return: weighted avgBitrate based on the playback time duration.

    """
    _avgBitrate = 0
    _sumBitrate = 0
    _totalTime = _stats[-1]['videoTime'] - _stats[0]['videoTime']
    for i in range(0, len(_stats)-1):
        _sumBitrate += (_stats[i+1]['videoTime']-_stats[i]['videoTime'])*_stats[i]['bitrate']

    _avgBitrate=_sumBitrate/_totalTime
    return _avgBitrate  # def _calcSwitchingImpact(self,start_time,curr_time,vq_before,vq_after):

def test_calc_weightedAvgBitrate(_stats):
    """

    :param _stats:
    :return: test the calc_weightedAvgBitrate
    """
    _stats_w_videoTime=add_videoTime(_stats)
    _wAvgBitrate=calc_weightedAvgBitrate(_stats_w_videoTime)
    print _wAvgBitrate



# 		""" It returns the impact factor given
# 		the start time stamp for the switching,
# 		current time of the video playing(time),
# 		video quality before switching (vq_before)
# 		and video quality after switching (vq_after)."""
# 		return(np.absolute(vq_after-vq_before)*np.exp(-0.015*(curr_time-start_time)))

# 	def _updateSwitchingImpact(self,currentTime):

# 		br_data=self._stats['videoBitrate']
# 		sw_index=[]
# 		#find where switching is happened in the video bitrate list and return the list of index.
# 		for i in range(1,len(br_data)-2):
# 			if br_data[i+1] != br_data[i]:
# 				sw_index.append(i+1)

# 		if currentTime < long(self._stats['videoTime'][-1]):
# 			print "current time is not matched with the logs time"
# 			return
# 		else:
# 			end_time=currentTime - long(self._stats['videoTime'][-1])
# 			#Create an array for each switching happens in the time.
# 			br_impact=np.zeros((len(sw_index),end_time))
# 			k=0
# 			for i in sw_index:
# 				for j in range(end_time):
# 					if j < i:
# 						br_impact[k,j]=0
# 					else:
# 						br_impact[k,j]=self._calcSwitchingImpact(
# 							start_time=self._stats['videoTime'][i],
# 							curr_time=self._stats['videoTime'][i]+(j-i),
# 							br_before=self._stats['videoQuality'][i-1],
# 							br_after=self._stats['videoQuality'][i]
# 						)
# 				k=k+1
# 			final_data=np.zeros(end_time)
# 			for j in range(br_impact.shape[1]):
# 				for i in range(br_impact.shape[0]):
# 					final_data[j]+=br_impact[i][j]
# 			self._stats['switchingImpact']=list(final_data)


