# -*- coding: utf-8 -*-

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-u', '--username',
                            default='User Name',
                            help='User name')

        parser.add_argument('-e', '--email',
                            default='user@bogus.com',
                            help='User email')

        parser.add_argument('-i', '--instructor',
                            action='store_true',
                            help='Include in instructor group')

        parser.add_argument('-p',
                            default='boguspwd',
                            help='User password')

    def handle(self, *args, **options):

        user_model = get_user_model()

        user = user_model.objects.filter(email=options['email']).first()
        if not user:
            if options['verbosity']:
                self.stdout.write(self.style.SUCCESS(
                    'Creating user {0} ({1})'.format(
                        options['username'],
                        options['email']
                    )
                ))
            user = user_model.objects.create_user(
                name=options['username'],
                email=options['email'],
                password=options['p']
            )
        else:
            if options['verbosity']:
                self.stdout.write(self.style.SUCCESS(
                    'User {0} already exists'.format(options['username'])
                ))

        if not options['instructor']:
            # No need to check if member of instructor group
            return

        group = Group.objects.filter(name='instructor').first()
        if not group:
            self.stdout.write(self.style.ERROR(
                'Instructor group does not exist. Initialize the DB first.'
            ))
            return

        user.groups.add(group)
        user.save()
