# -*- coding: utf-8 -*-
'''
Copyright (c) 2015 Heidelberg University Library
Distributed under the GNU GPL For full terms see the file
LICENSE.md
'''
import os
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
    submissions = db(query).select(db.submission_settings.ALL,orderby=db.submissions.series_position)
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

    for i in submissions:
      series_position = db(db.submissions.submission_id == i.submission_id).select(db.submissions.series_position).first()['series_position']
      if series_position:
         subs.setdefault(i.submission_id, {})['series_position'] = series_position
      authors=''
      if i.setting_name == 'abstract':
          subs.setdefault(i.submission_id, {})['abstract'] = i.setting_value
      if i.setting_name == 'subtitle':
          subs.setdefault(i.submission_id, {})['subtitle'] = i.setting_value
      if i.setting_name == 'title':
          subs.setdefault(i.submission_id, {})[
              'title'] = i.setting_value
      author_q = ((db.authors.submission_id == i.submission_id))
      authors_list = db(author_q).select(
          db.authors.first_name, db.authors.last_name)
      for j in authors_list:
          authors += j.first_name + ' ' + j.last_name + ', '
      if authors.endswith(', '):
        authors = authors[:-2]
          
      subs.setdefault(i.submission_id, {})['authors'] = authors
      series_positions = db((db.submissions.context_id == myconf.take('omp.press_id'))  &  (db.submissions.submission_id!=ignored_submissions) & (db.submissions.status == 3) & (
        db.submissions.context_id==db.series.press_id) & (db.series.path==series)  & (db.submissions.series_id==db.series.series_id) &(db.submissions.context_id==db.series.press_id)  ).select(db.submissions.submission_id,db.submissions.series_position, orderby=db.submissions.series_position)

    return dict(submissions=submissions, subs=subs, sp=series_positions, series_title=series_title, series_subtitle=series_subtitle)

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
      author_q = ((db.authors.submission_id == i.submission_id))
      authors_list = db(author_q).select(
          db.authors.first_name, db.authors.last_name)
      for j in authors_list:
          authors += j.first_name + ' ' + j.last_name + ', '
      if authors.endswith(', '):
        authors = authors[:-2]
          
      subs.setdefault(i.submission_id, {})['authors'] = authors
    return dict(submissions=submissions, subs=subs, order=order)



def book():
    abstract, authors, cleanTitle, publication_format_settings_doi, press_name, subtitle = '', '', '', '', '', ''
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

    author_q = ((db.authors.submission_id == book_id))
    authors_list = db(author_q).select(
        db.authors.first_name, db.authors.last_name)

    for i in authors_list:
        authors += i.first_name + ' ' + i.last_name + ', '
    if authors.endswith(', '):
        authors = authors[:-2]

    author_bio = db((db.authors.submission_id == book_id) & (db.authors.author_id == db.author_settings.author_id) & (
        db.author_settings.locale == locale) & (db.author_settings.setting_name == 'biography')).select(db.author_settings.setting_value).first()

    chapter_query = ((db.submission_chapters.submission_id == book_id) & (db.submission_chapters.chapter_id == db.submission_chapter_settings.chapter_id) & (db.submission_chapter_settings.locale == locale) & (db.submission_file_settings.setting_name ==
                                                                                                                                                                                                                 "chapterID") & (db.submission_file_settings.setting_value == db.submission_chapters.chapter_id) & (db.submission_file_settings.file_id == db.submission_files.file_id) & (db.submission_chapter_settings.setting_name == 'title'))

    chapters = db(chapter_query).select(db.submission_chapters.chapter_id, db.submission_chapter_settings.setting_value, db.submission_files.assoc_id, db.submission_files.submission_id, db.submission_files.genre_id,
                                        db.submission_files.file_id, db.submission_files.revision, db.submission_files.file_stage, db.submission_files.date_uploaded, orderby=[db.submission_chapters.chapter_seq, db.submission_files.assoc_id], groupby=[db.submission_chapters.chapter_id])

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
        if row['date_format'] == '20': #YYYYMMDD
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
     
    
    types=['jpg','png','gif']
    cover_image=''
    path=request.folder+'static/monographs/'+book_id+'/simple/cover.'
    for  t in types:
    	if os.path.exists(path+t):
		cover_image= URL(myconf.take('web.application'), 'static','monographs/' + book_id + '/simple/cover.'+t)

    return locals()
    #return dict(abstract=abstract, authors=authors, author_bio=author_bio, book_id=book_id, chapters=chapters, cleanTitle=cleanTitle, cover_image=cover_image, full_files=full_files, identification_codes=identification_codes,
    #            publication_formats=publication_formats, publication_format_settings_doi=publication_format_settings_doi, published_date=published_date, subtitle=subtitle, press_name=press_name, representatives=representatives)
