# -*- coding: utf-8 -*-

"""Command to show the configuration execution."""
from django.core.management.base import BaseCommand
from settings.base import show_configuration


class Command(BaseCommand):
    """Class implementing a command to show the configuration."""

    def handle(self, *args, **options):
        """Execute command to show the configuration.

        :param args: Arguments given to the command (None!)
        :param options: Options parsed
        :return: Nothing
        """
        show_configuration()
