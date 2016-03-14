# -*- coding: utf-8 -*-
'''
Copyright (c) 2015 Heidelberg University Library
Distributed under the GNU GPL v3. For full terms see the file
LICENSE.md
'''

from ompdal import OMPDAL

def saa_info():
	return dict()

def daidalos_info():
        return dict()

def byzanzoo_info():
        return dict()

def archber_info():
        return dict()

def dcb_info():
        return dict()

def cms_info():
        return dict()

def index():
  if session.forced_language == 'de':
    locale = 'de_DE'
  if session.forced_language == 'en':
     locale = 'en_US'

  ompdal = OMPDAL(db, myconf)
  
  series = ompdal.getSeries()
  if len(series) == 0:
    raise HTTP(200, "'invalid': no series in this press")

  setting_types = ['title','subtitle','description']
  order = []
  for s in series:
    series_info = dict()
    series_info['path'] = s.path
    series_info['image'] = s.image
    settings = ompdal.getLocalizedSeriesSettings(s.series_id, locale)
    if not settings:
      settings = ompdal.getSeriesSettings(s.series_id)
    for st in settings:
      if st.setting_name in setting_types:
	series_info[st.setting_name] = st.setting_value
    order.append(series_info)

  order.sort(key=lambda s: s.get('title', 'z'))

  return locals()
