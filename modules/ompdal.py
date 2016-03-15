# -*- coding: utf-8 -*-

class OMPDAL:
	"""
	A rudimentary database abstraction layer for the OMP database.
	"""
	def __init__(self, db, conf):
		self.db = db
		self.conf = conf

	def getAuthors(self, submission_id):
        	"""
	       	Get all authors associated with the specified submission regardless of exact role.
        	"""
		return self.db((self.db.authors.submission_id==submission_id)).select(
					self.db.authors.first_name, 
					self.db.authors.middle_name, 
					self.db.authors.last_name, 
					orderby=self.db.authors.seq)

	def getEditors(self, submission_id):
        	"""
	       	Get all authors associated with the specified submission with editor role.
       		"""
		try:
			editor_group_id = self.conf.take('omp.editor_id')
		except:
			return []
		return self.db((self.db.authors.submission_id==submission_id) 
				& (self.db.authors.user_group_id==editor_group_id)).select(
					self.db.authors.first_name, 
					self.db.authors.middle_name, 
					self.db.authors.last_name, 
					orderby=self.db.authors.seq)

	def getChapterAuthors(self, submission_id):
       		"""
       		Get all authors associated with the specified submission with chapter author role
       		"""
		try:
			chapter_author_group_id = self.conf.take('omp.author_id')
		except:
			return []
		return self.db((self.db.authors.submission_id==submission_id) 
				& (self.db.authors.user_group_id==chapter_author_group_id)).select(
					self.db.authors.first_name, 
					self.db.authors.middle_name, 
					self.db.authors.last_name, 
					orderby=self.db.authors.seq)

        def getSubmission(self, submission_id):
		"""
		Get submission table row for a given id.
		"""
                return self.db.submissions[submission_id]

	def getSeries(self):
		"""
		Get series info.
		"""
		return self.db(self.db.series.press_id==self.conf.take("omp.press_id")).select(
					self.db.series.series_id, 
					self.db.series.path, 
					self.db.series.image)

	def getLocalizedSeriesSettings(self, series_id, locale):
		"""
		Get series settings for a given locale.
		"""
		return self.db((self.db.series_settings.series_id==series_id) 
				& (self.db.series_settings.locale==locale)).select(
					self.db.series_settings.series_id, 
					self.db.series_settings.locale, 
					self.db.series_settings.setting_name, 
					self.db.series_settings.setting_value)

        def getSeriesSettings(self, series_id):
		"""
		Get series settings.
		"""
        	return self.db(self.db.series_settings.series_id==series_id).select(
					self.db.series_settings.series_id, 
					self.db.series_settings.locale, 
					self.db.series_settings.setting_name, 
					self.db.series_settings.setting_value)

	def getLocalizedChapters(self, submission_id, locale):
		"""
		Get all chapters associated with the given submission and a given locale.
		"""
		q = ((self.db.submission_chapters.submission_id == submission_id) 
				& (self.db.submission_chapters.chapter_id == self.db.submission_chapter_settings.chapter_id)
				& (self.db.submission_file_settings.locale == locale)
				& (self.db.submission_file_settings.setting_name == "chapterID") 
				& (self.db.submission_file_settings.setting_value == self.db.submission_chapters.chapter_id) 
				& (self.db.submission_file_settings.file_id == self.db.submission_files.file_id) 
				& (self.db.submission_chapter_settings.setting_name == 'title'))

		return self.db(q).select(self.db.submission_chapters.chapter_id, 
					self.db.submission_chapter_settings.setting_value, 
					self.db.submission_files.assoc_id, 
					self.db.submission_files.submission_id, 
					self.db.submission_files.genre_id,
					self.db.submission_files.file_id, 
					self.db.submission_files.revision, 
					self.db.submission_files.file_stage, 
					self.db.submission_files.date_uploaded, 
					orderby=[self.db.submission_chapters.chapter_seq, self.db.submission_files.assoc_id], 
					groupby=[self.db.submission_chapters.chapter_id])

        def getChapters(self, submission_id):
		"""
		Get all chapters associated with the given submission.
		"""
                q = ((self.db.submission_chapters.submission_id == submission_id)
                        	& (self.db.submission_chapters.chapter_id == self.db.submission_chapter_settings.chapter_id)
                        	& (self.db.submission_file_settings.setting_name == "chapterID")
                        	& (self.db.submission_file_settings.setting_value == self.db.submission_chapters.chapter_id)
                        	& (self.db.submission_file_settings.file_id == self.db.submission_files.file_id)
                        	& (self.db.submission_chapter_settings.setting_name == 'title'))

                return self.db(q).select(self.db.submission_chapters.chapter_id,
                                	self.db.submission_chapter_settings.setting_value,
                                	self.db.submission_files.assoc_id,
                                	self.db.submission_files.submission_id,
                                	self.db.submission_files.genre_id,
                                	self.db.submission_files.file_id,
                                	self.db.submission_files.revision,
                                	self.db.submission_files.file_stage,
                                	self.db.submission_files.date_uploaded,
                                	orderby=[self.db.submission_chapters.chapter_seq, self.db.submission_files.assoc_id],
                                	groupby=[self.db.submission_chapters.chapter_id])
