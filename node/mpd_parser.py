#!/usr/bin/env python2.7

""" Parse MPDS """

from lxml import etree
import aniso8601
import os
import Queue
import random
import re
import requests
import threading
import time
import multiprocessing
import pprint
from pymediainfo import MediaInfo

class Parser(object):

    media = {'representations': None, 'initialisations': None}
    max_seg_duration = 0
    max_bandwidth = 0

    medy = {}

    def __init__(self, manifest):
        self.media['representations'] = list()
        self.media['initialisations'] = list()
        self.load_mpd(manifest)

    def event(self, thing_1, thing_2):
        print '[%s] %s' % (thing_1, thing_2)

    def load_mpd(self, manifest):
        manifest = open(manifest)
        document = etree.parse(manifest)
        mpd = document.getroot()
        origin = ''
        base_url = self.BaseURL(origin)
        self.min_buffer = int(float(mpd.attrib['minBufferTime'][2:-1]))
        self.parse_mpd(base_url, mpd)
        sorted(self.media['representations'], key=lambda representation:
                representation['bandwidth'])
        self.event('stop', 'parsing mpd')

    def parse_mpd(self, base_url, parent_element):
        """Parse 'mpd' level XML."""
        try:
            self._set_mpd_duration(
                parent_element.get('mediaPresentationDuration'))
        except (TypeError, IndexError, ValueError):
            self.mpd_duration = 0
        for child_element in parent_element:
            if 'BaseURL' in child_element.tag:
                base_url.mpd = child_element.text
            if 'Period' in child_element.tag:
                self.parse_period(base_url, child_element)
        base_url.mpd = ''

    def _set_mpd_duration(self, duration):
        """Set the duration of playback defined in the MPD."""
        self.mpd_duration = aniso8601.parse_duration(duration).seconds

    def parse_period(self, base_url, parent_element):
        """Parse 'period' level XML."""
        for child_element in parent_element:
            if 'BaseURL' in child_element.tag:
                base_url.period = child_element.text
            if 'AdaptationSet' in child_element.tag:
                self.parse_adaptation_set(base_url, child_element)
        base_url.period = ''

    def parse_adaptation_set(self, base_url, parent_element):
        """Parse 'adaption set' level XML. Create a new template if present."""
        template = None
        all_thingys = {}
        for child_element in parent_element:
            if 'BaseURL' in child_element.tag:
                base_url.adaption_set = child_element.text
            if 'SegmentTemplate' in child_element.tag:
                template = self.Template(child_element)
            elif 'Representation' in child_element.tag:
                bandwidth = int(child_element.attrib['bandwidth'])
                try:
                    id_ = str(child_element.attrib['id'])
                except KeyError:
                    print 'id not found, generating random number'
                    id_ = str(random.randint(0, 1000))
                if template:
                    self.parse_templated_representation(template, base_url, child_element)
                else:
                    thingy = self.parse_representation(base_url, bandwidth, id_,
                                          child_element)
                all_thingys = dict(list(thingy.items()) + list(all_thingys.items()))
        self.medy = all_thingys
        base_url.adaption_set = ''

    def parse_representation(self, base_url, bandwidth, id_, parent_element):
        """Parse 'representation' level XML without a template."""
        thingy = {}
        for child_element in parent_element:
            if 'SegmentBase' in child_element.tag:
                self.parse_segment_base(
                    base_url,
                    bandwidth,
                    id_,
                    child_element)
            if 'BaseURL' in child_element.tag:
                base_url.representation = child_element.text
            if 'SegmentList' in child_element.tag:
                duration = int(child_element.attrib['duration'])
                self._max_values(duration, bandwidth)
                segment_list = self.parse_segment_list(base_url=base_url,
                                        duration=duration,
                                        bandwidth=bandwidth,
                                        id_=id_,
                                        parent_element=child_element)
                for segment in segment_list:
                    thingy[segment] = parent_element.attrib
        base_url.representation = ''
        return thingy

    def parse_segment_base(self, base_url, bandwidth, id_, parent_element):
        """
        Parse 'segment_base' level XML.

        Should be initialisation URLs.

        """
        for child_element in parent_element:
            if 'Initialization' in child_element.tag:
                try:
                    media_range = child_element.attrib['range'].split('-')
                except KeyError:
                    media_range = (0, 0)
                self.media['initialisations'].append(child_element.attrib['sourceURL'])
                #return child_element.attrib['sourceURL']

    def parse_segment_list(self, **kwargs):
        """
        Parse 'segment_list' level XML.

        Should be source URLs, describing actual content.

        """
        queue = Queue.Queue()
        segment_list = list()
        for child_element in kwargs['parent_element']:
            if 'SegmentURL' in child_element.tag:
                try:
                    media_range = child_element.attrib['mediaRange'] \
                        .split('-')
                except KeyError:
                    media_range = (0, 0)
                queue.put({'duration': kwargs['duration'],
                           'url': kwargs['base_url'].resolve() +
                           child_element.attrib['media'],
                           'bytes_from': int(media_range[0]),
                           'bytes_to': int(media_range[1])})
                segment_list.append(child_element.attrib['media'])
        return segment_list



    def _max_values(self, duration, bandwidth):
        """Find maximum values for duration and bandwidth in the MPD."""
        if duration > self.max_seg_duration:
            self.max_seg_duration = duration
        if bandwidth > self.max_bandwidth:
            self.max_bandwidth = bandwidth

    class BaseURL(object):

        """
        Used to resolve the current level of base URL.

        Determines a prefix on the source URL if found.

        """

        representation = None
        adaption_set = None
        period = None
        mpd = None
        origin = None

        def __init__(self, origin):
            """Initialise base URL object by clearing all values."""
            self.clear()
            self.origin = origin

        def clear(self):
            """Clear all values with an empty string."""
            self.representation = ''
            self.adaption_set = ''
            self.period = ''
            self.mpd = ''
            self.origin = ''

        def resolve(self):
            """Return the correct base URL."""
            if self.representation != str(''):
                return self.representation
            elif self.adaption_set != str(''):
                return self.adaption_set
            elif self.period != str(''):
                return self.period
            elif self.mpd != str(''):
                return self.mpd
            else:
                return self.origin