from __future__ import unicode_literals

from django.db import models

class Repositories(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField(blank=True, null=True)
    master_branch = models.TextField(blank=True, null=True)
    clone_url = models.TextField(unique=True, blank=True, null=True)
    cloned_date = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
    	return self.name

    class Meta:
        managed = False
        db_table = 'repositories'


class ProcessedComments(models.Model):
    id = models.DecimalField(primary_key=True, unique=True, max_digits=65535, decimal_places=65535)
    repository_id = models.DecimalField(max_digits=65535, decimal_places=65535)
    file = models.ForeignKey('Files', db_column='file_id')
    file_versions_id = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    commit_hash = models.TextField(blank=True, null=True)
    comment_text = models.TextField(blank=True, null=True)
    treated_comment_text = models.TextField(blank=True, null=True)
    td_classification = models.TextField(blank=True, null=True)
    comment_type = models.TextField(blank=True, null=True)
    comment_format = models.TextField(blank=True, null=True)
    start_line = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    end_line = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    has_class_declaration = models.NullBooleanField()
    has_interface_declaration = models.NullBooleanField()
    has_enum_declaration = models.NullBooleanField()
    has_annotation_declaration = models.NullBooleanField()
    class_declaration_lines = models.TextField(blank=True, null=True)
    introduced_version_commit_hash = models.TextField(blank=True, null=True)
    is_introduced_version = models.NullBooleanField()
    introduced_version_author = models.TextField(blank=True, null=True)
    introduced_version_date = models.DateTimeField(blank=True, null=True)
    removed_version_commit_hash = models.TextField(blank=True, null=True)
    has_removed_version = models.NullBooleanField()
    removed_version_author = models.TextField(blank=True, null=True)
    removed_version_date = models.DateTimeField(blank=True, null=True)
    interval_time_to_remove = models.TextField(blank=True, null=True)
    comment_location = models.TextField(blank=True, null=True)
    func_specifier = models.TextField(blank=True, null=True)
    func_return_type = models.TextField(blank=True, null=True)
    func_name = models.TextField(blank=True, null=True)
    func_parameter_list = models.TextField(blank=True, null=True)
    func_line = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    epoch_time_to_remove = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'processed_comments'

class Files(models.Model):
    file_id = models.DecimalField(primary_key=True, max_digits=65535, decimal_places=65535, db_column='id')
    repository_id = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    extracted_date = models.DateTimeField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    file_path = models.TextField(blank=True, null=True)
    deletion_commit_hash = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'files'
        unique_together = (('repository_id', 'name', 'file_path'),)