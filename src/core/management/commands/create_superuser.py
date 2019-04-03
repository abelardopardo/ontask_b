# -*- coding: utf-8 -*-

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-u', '--username',
                            default='Super User',
                            help='Super user name')

        parser.add_argument('-e', '--email',
                            default='superuser@bogus.com',
                            help='Super user email')

        parser.add_argument('-p',
                            default='boguspwd',
                            help='Super user password')

    def handle(self, *args, **options):

        user_model = get_user_model()

        if not user_model.objects.filter(email=options['email']).exists():
            user_model.objects.create_superuser(
                name=options['username'],
                email=options['email'],
                password=options['p']
            )
