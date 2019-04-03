# -*- coding: utf-8 -*-

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-u', '--username',
                            default='User Name',
                            help='User name')

        parser.add_argument('-e', '--email',
                            default='user@bogus.com',
                            help='User email')

        parser.add_argument('-p',
                            default='boguspwd',
                            help='User password')

    def handle(self, *args, **options):

        user_model = get_user_model()

        if not user_model.objects.filter(email=options['email']).exists():
            if options['verbosity']:
                self.stdout.write(self.style.SUCCESS(
                    'Creating user {0} ({1})'.format(
                        options['username'],
                        options['email']
                    )
                ))
            user_model.objects.create_user(
                name=options['username'],
                email=options['email'],
                password=options['p']
            )
        else:
            if options['verbosity']:
                self.stdout.write(self.style.SUCCESS(
                    'User {0} already exists'.format( options['username'])
                ))
