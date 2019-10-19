#!/usr/bin/env python3
import os
import sys

if __name__ == "__main__":
    # Change the DJANGO_SETTINGS_MODULE environment variable
    # for using the environment specific settings file.
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.production")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
