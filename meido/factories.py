import factory
from meido import models
from flask import current_app


class ProjectFactory(factory.Factory):
    class Meta:
        model = models.Project

    name = 'kmbmpdc'
    stub = 'kmbmpdc'
    color = 'fb2c6e'
    description = 'macOS menubar application for controlling MPD'


class BuildFactory(factory.Factory):
    class Meta:
        model = models.Build

    number = 1
    commit = '1c66a45bb77d90f50f258d6bad89ee196d98971b'
    commit_message = 'Initial commit'
    filename = 'build-1.txt'
    downloads = 0
    project = factory.SubFactory(ProjectFactory)


class UserFactory(factory.Factory):
    class Meta:
        model = models.User

    email = 'admin@example.com'
    password = 'pretender'
    username = 'admin'
