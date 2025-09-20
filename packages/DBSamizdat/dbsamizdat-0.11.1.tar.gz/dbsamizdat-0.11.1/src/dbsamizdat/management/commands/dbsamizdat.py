# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from argparse import Namespace

from django.core.management.base import BaseCommand

from dbsamizdat.runner import augment_argument_parser
from dbsamizdat.exceptions import SamizdatException
from dbsamizdat.const import env


class Command(BaseCommand):
    help = 'Play nice with dbsamizdat.'

    def create_parser(self, *args, **kwargs):
        return super(Command, self).create_parser(*args, **{**kwargs, **{'conflict_handler': 'resolve'}})

    def add_arguments(self, parser):
        augment_argument_parser(parser, context=env.DJANGO)

    def handle(self, *args, **options):
        try:
            options['func'](Namespace(**{'parallel': False, **options}))
        except SamizdatException as argh:
            exit(f'\n\n\nFATAL: {argh}')
        except KeyboardInterrupt:
            exit('\nInterrupted.')
