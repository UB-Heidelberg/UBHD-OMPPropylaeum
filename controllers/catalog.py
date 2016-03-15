# -*- coding: utf-8 -*-
'''
Copyright (c) 2015 Heidelberg University Library
Distributed under the GNU GPL For full terms see the file
LICENSE.md
'''
import os
from operator import itemgetter
from ompdal import OMPDAL

def series():
    abstract, author, cleanTitle, subtitle = '', '', '', ''
    locale = 'de_DE'
    if session.forced_language == 'en':
        locale = 'en_US'
    ignored_submissions =  myconf.take('omp.ignore_submissions') if myconf.take('omp.ignore_submissions') else -1
    
    if request.args == []:
      redirect( URL('home', 'index'))
    series=''
    if request.args[0]:
  	 series = request.args[0]
    
    query = ((db.submissions.context_id == myconf.take('omp.press_id'))  &  (db.submissions.submission_id!=ignored_submissions) & (db.submissions.status == 3) & (
        db.submission_settings.submission_id == db.submissions.submission_id) & (db.submission_settings.locale == locale) & (db.submissions.context_id==db.series.press_id) & (db.series.path==series)  & (db.submissions.series_id==db.series.series_id) &(db.submissions.context_id==db.series.press_id))
    submissions = db(query).select(db.submission_settings.ALL,orderby=db.submissions.series_position|~db.submissions.date_submitted)
    subs = {}

    series_title = ""
    series_subtitle = ""
    rows = db(db.series.path == series).select(db.series.series_id)
    if len(rows) == 1:
        series_id = rows[0]['series_id']
    	rows = db((db.series_settings.series_id == series_id) & (db.series_settings.setting_name == 'title') & (db.series_settings.locale == locale)).select(db.series_settings.setting_value)
	if rows:
	    series_title=rows[0]['setting_value']
	rows = db((db.series_settings.series_id == series_id) & (db.series_settings.setting_name == 'subtitle') & (db.series_settings.locale == locale)).select(db.series_settings.setting_value)
        if rows:
            series_subtitle=rows[0]['setting_value']

    series_positions = {}
    order = []
    for i in submissions:
      if not i.submission_id in order:
	order.append(i.submission_id)
      series_position = db.submissions(db.submissions.submission_id==i.submission_id).series_position
      if series_position:
         subs.setdefault(i.submission_id, {})['series_position'] = series_position
	 pos_counter = 0
         try:
	   int_pos = int(series_position)
	   series_positions[i.submission_id] = int_pos
	 except:
	   series_positions[i.submission_id] = pos_counter
	   pos_counter += 1
      authors=''
      if i.setting_name == 'abstract':
          subs.setdefault(i.submission_id, {})['abstract'] = i.setting_value
      if i.setting_name == 'subtitle':
          subs.setdefault(i.submission_id, {})['subtitle'] = i.setting_value
      if i.setting_name == 'title':
          subs.setdefault(i.submission_id, {})[
              'title'] = i.setting_value
      
      authors = db((db.authors.submission_id==i.submission_id)).select(
            db.authors.first_name, db.authors.middle_name, db.authors.last_name, orderby=db.authors.seq)
      editors = []
      # check, if submission is an edited volume
      if db.submissions(db.submissions.submission_id==i.submission_id).edited_volume == 1:
        try:
	   # look for editors using group ids
          editors = db( (db.authors.submission_id==i.submission_id) & (db.authors.user_group_id==myconf.take('omp.editor_id')) ).select(
            db.authors.first_name, db.authors.middle_name, db.authors.last_name, orderby=db.authors.seq)
          authors = db( (db.authors.submission_id==i.submission_id) & (db.authors.user_group_id==myconf.take('omp.author_id')) ).select(
            db.authors.first_name, db.authors.middle_name, db.authors.last_name, orderby=db.authors.seq)
        except:
	  # editor_id and/or author_id not set
	  pass
      subs.setdefault(i.submission_id, {})['authors'] = authors
      subs.setdefault(i.submission_id, {})['editors'] = editors
      if series_positions != {}:
        order = [e[0] for e in sorted(series_positions.items(), key=itemgetter(1), reverse=True)]

    return locals()

def index():
    abstract, author, cleanTitle, subtitle = '', '', '', ''
    locale = 'de_DE'
    if session.forced_language == 'en':
        locale = 'en_US'
    query = ((db.submissions.context_id == myconf.take('omp.press_id'))  & (db.submissions.status == 3) & (
        db.submission_settings.submission_id == db.submissions.submission_id) & (db.submission_settings.locale == locale))
    submissions = db(query).select(db.submission_settings.ALL,orderby=~db.submissions.date_submitted)
    subs = {}
    order = []
    for i in submissions:
      if not i.submission_id in order:
	order.append(i.submission_id)
      authors=''
      if i.setting_name == 'abstract':
          subs.setdefault(i.submission_id, {})['abstract'] = i.setting_value
      if i.setting_name == 'subtitle':
          subs.setdefault(i.submission_id, {})['subtitle'] = i.setting_value
      if i.setting_name == 'title':
          subs.setdefault(i.submission_id, {})[
              'title'] = i.setting_value

      ompdal = OMPDAL(db, myconf)

      subs.setdefault(i.submission_id, {})['authors'] = ompdal.getAuthors(i.submission_id)
      subs.setdefault(i.submission_id, {})['editors'] = ompdal.getEditors(i.submission_id)
          
    return locals() 

def book():
    abstract, cleanTitle, publication_format_settings_doi, press_name, subtitle = '', '', '', '', ''
    locale = ''
    if session.forced_language == 'en':
        locale = 'en_US'

    if session.forced_language == 'de':
        locale = 'de_DE'
    book_id = request.args[0] if request.args else redirect(
        URL('home', 'index'))

    query = ((db.submission_settings.submission_id == int(book_id))
             & (db.submission_settings.locale == locale))
    book = db(query).select(db.submission_settings.ALL)

    #if len(book) == 0:
    #    redirect(URL('catalog', 'index'))

    ompdal = OMPDAL(db, myconf)

    authors = ompdal.getAuthors(book_id)
    editors = ompdal.getEditors(book_id)

    author_bio = db((db.authors.submission_id == book_id) & (db.authors.author_id == db.author_settings.author_id) & (
        db.author_settings.locale == locale) & (db.author_settings.setting_name == 'biography')).select(db.author_settings.setting_value).first()

    chapters = ompdal.getLocalizedChapters(book_id, locale)
    if not chapters:
      chapters = ompdal.getChapters(book_id)

    pub_query = (db.publication_formats.submission_id == book_id) & (db.publication_format_settings.publication_format_id == db.publication_formats.publication_format_id) & (
        db.publication_format_settings.locale == locale)

    publication_formats = db(pub_query & (db.publication_format_settings.setting_value != myconf.take('omp.ignore_format'))).select(db.publication_format_settings.setting_name, db.publication_format_settings.setting_value,
                                                                                                                                    db.publication_formats.publication_format_id, groupby=db.publication_formats.publication_format_id, orderby=db.publication_formats.publication_format_id)

    press_settings = db(db.press_settings.press_id == myconf.take('omp.press_id')).select(
        db.press_settings.setting_name, db.press_settings.setting_value)

    publication_format_settings = db((db.publication_format_settings.setting_name == 'name') & (db.publication_format_settings.locale == locale) & (db.publication_formats.submission_id == book_id) & (
        db.publication_formats.publication_format_id == db.publication_format_settings.publication_format_id)).select(db.publication_format_settings.publication_format_id, db.publication_format_settings.setting_value)

    if publication_format_settings:
        publication_format_settings_doi = db((db.publication_format_settings.setting_name == 'pub-id::doi') & (db.publication_format_settings.publication_format_id == publication_format_settings.first(
        )['publication_format_id']) & (publication_format_settings.first()['setting_value'] == myconf.take('omp.doi_format_name'))).select(db.publication_format_settings.setting_value).first()

    identification_codes = {}
    identification_codes_publication_formats = db(
        db.publication_formats.submission_id == book_id).select(
        db.publication_formats.publication_format_id)

    for i in identification_codes_publication_formats:
        name = db(
            (db.publication_format_settings.locale == locale) & (
                db.publication_format_settings.publication_format_id == i['publication_format_id']) & (
                db.publication_format_settings.setting_name == 'name') & (
                db.publication_format_settings.setting_value != myconf.take('omp.xml_category_name'))) .select(
                    db.publication_format_settings.setting_value).first()
        identification_code = db(
            (db.identification_codes.publication_format_id == i['publication_format_id']) & (
                db.identification_codes.code == 15)).select(
            db.identification_codes.value).first()
        if name and identification_code:
            identification_codes[
                identification_code['value']] = name['setting_value']
    date_pub_query =  (db.publication_formats.submission_id == book_id) & (db.publication_format_settings.publication_format_id == db.publication_formats.publication_format_id)
    publication_dates = db(date_pub_query & (db.publication_format_settings.setting_value == myconf.take('omp.doi_format_name')) & (
        db.publication_dates.publication_format_id == db.publication_format_settings.publication_format_id)).select(db.publication_dates.date, db.publication_dates.role, db.publication_dates.date_format)

    published_date = None
    print_published_date = None
    publication_year = ""
    for row in publication_dates:
        if row['date_format'] == '00': #YYYYMMDD
		published_date = row['date']
		publication_year = published_date[:4]
	if row['date_format'] == '05' and row['role'] == '19': #YYYY, original date
		print_published_date = row['date']

    representatives = db(
        (db.representatives.submission_id == book_id) & (
            db.representatives.representative_id_type == myconf.take('omp.representative_id_type'))).select(
        db.representatives.name,
        db.representatives.url,
        orderby=db.representatives.representative_id)
    full_files = db((db.submission_files.submission_id == book_id) & (db.submission_files.genre_id == myconf.take('omp.monograph_type_id'))& (db.submission_files.file_stage > 5)& (db.submission_files.assoc_id==db.publication_formats.publication_format_id) ).select(db.submission_files.original_file_name, db.submission_files.submission_id, db.submission_files.genre_id, db.submission_files.file_id, db.submission_files.revision, db.submission_files.file_stage, db.submission_files.date_uploaded , orderby=db.submission_files.file_id,)

    press_location = ""
    for j in press_settings:
        if j.setting_name == 'name':
            press_name = j.setting_value
	if j.setting_name == 'location':
	    press_location = j.setting_value

    for i in book:
        if i.setting_name == 'abstract':
            abstract = i.setting_value
        if i.setting_name == 'subtitle':
            subtitle = i.setting_value
        if i.setting_name == 'title':
            cleanTitle = i.setting_value

    sub = ompdal.getSubmission(book_id)
    series_info = {}
    if sub.series_id:
       series_settings = ompdal.getLocalizedSeriesSettings(sub.series_id, locale)
       if not series_settings:
               ompdal.getSeriesSettings(sub.series_id)
       for r in series_settings:
               if r.setting_name == "title":
                       series_info["series_title"] = r.setting_value
               elif r.setting_name == "subtitle":
                       series_info["series_subtitle"] = r.setting_value
       series_info["series_position"] = sub.series_position
    
    types=['jpg','png','gif']
    cover_image=''
    path=request.folder+'static/monographs/'+book_id+'/simple/cover.'
    for  t in types:
    	if os.path.exists(path+t):
		cover_image= URL(myconf.take('web.application'), 'static','monographs/' + book_id + '/simple/cover.'+t)

    return locals()
