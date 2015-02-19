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

	mpd = {}

	def __init__(self, manifest):
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
		self.event('start', 'parsing mpd')
		self.parse_mpd(base_url, mpd)
		self.event('stop', 'parsing mpd')

	def parse_mpd(self, base_url, parent_element):
		"""Parse 'mpd' level XML."""
		self.mpd_duration = self._mpd_duration(
			parent_element.get('mediaPresentationDuration'))
		for child_element in parent_element:
			if 'BaseURL' in child_element.tag:
				base_url.mpd = child_element.text
			if 'Period' in child_element.tag:
				self.parse_period(base_url, child_element)
		base_url.mpd = ''

	def _mpd_duration(self, duration):
		"""Get the duration of playback defined in the MPD."""
		try:
			return aniso8601.parse_duration(duration).seconds
		except (TypeError, IndexError, ValueError):
			return 0

	def parse_period(self, base_url, parent_element):
		"""Parse 'period' level XML."""
		for child_element in parent_element:
			if 'BaseURL' in child_element.tag:
				base_url.period = child_element.text
			if 'AdaptationSet' in child_element.tag:
				self.mpd = self.parse_adaptation_set(base_url, child_element)
		base_url.period = ''

	def parse_adaptation_set(self, base_url, parent_element):
		"""Parse 'adaption set' level XML. Create a new template if present."""
		template = None
		representations = {}
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
					representation = self.parse_representation(base_url, bandwidth, id_,
										  child_element)
				representations = dict(list(representation.items()) + list(representations.items()))
		return representations
		base_url.adaption_set = ''

	def parse_representation(self, base_url, bandwidth, id_, parent_element):
		"""Parse 'representation' level XML without a template."""
		representation = {}
		for child_element in parent_element:
			if 'SegmentBase' in child_element.tag:
				self.parse_segment_base(base_url, bandwidth, id_, child_element)
			if 'BaseURL' in child_element.tag:
				base_url.representation = child_element.text
			if 'SegmentList' in child_element.tag:
				duration = int(child_element.attrib['duration'])
				segment_list = self.parse_segment_list(base_url=base_url,
										duration=duration,
										bandwidth=bandwidth,
										id_=id_,
										parent_element=child_element)
				for segment in segment_list:
					attributes = dict(parent_element.attrib.items() + {'duration': duration}.items())
					representation[segment] = attributes
		base_url.representation = ''
		return representation

	def parse_segment_base(self, base_url, bandwidth, id_, parent_element):
		"""
		Parse 'segment_base' level XML.

		Should be initialisation URLs.

		"""
		for child_element in parent_element:
			if 'Initialization' in child_element.tag:
				return child_element.attrib['sourceURL']

	def parse_segment_list(self, **kwargs):
		"""
		Parse 'segment_list' level XML.

		Should be source URLs, describing actual content.

		"""
		segment_list = list()
		for child_element in kwargs['parent_element']:
			if 'SegmentURL' in child_element.tag:
				segment_list.append(child_element.attrib['media'])
		return segment_list

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