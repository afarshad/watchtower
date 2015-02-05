
def getVideoQuality(videoResolution):

#720p video res.

# f(x)=(x < 2000)? -4.85*(x**-0.647)+1.011:1/0
#1080p video res.
# g(x)=-3.035*(x**-0.5061)+1.022
#360p video res.
# h(x)=(x < 1000)? -17.53*(x**-1.048)+0.9912:1/0
#set y2tics

def sw_impact(start_time,curr_time,br_before,br_after):

    """ It returns the impact factor given
    the start time stamp for the switching,
    current time of the video playing(time),
    video bitrate before switching (br_before)
    and video bitrate after switching (br_after)."""

    return(np.absolute(br_after-br_before)*np.exp(-0.015*(curr_time-start_time)))
