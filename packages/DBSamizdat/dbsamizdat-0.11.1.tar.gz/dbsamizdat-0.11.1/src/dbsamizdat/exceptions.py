# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from typing import List
from functools import partial

from .util import sqlfmt
sqlfmt_debug = partial(sqlfmt, indent_with='\t', number_lines=True)


class SamizdatException(Exception):
    def __init__(self, message, samizdat=None):
        self.message = message
        self.samizdat = samizdat

    def __str__(self):
        sd_subject = f'{repr(self.samizdat)} : ' if self.samizdat else ''
        return f'{self.__class__.__name__}: {sd_subject}{self.message}'


class InvocationError(SamizdatException):
    pass


class WrongTransactionStyleForParallelRefresh(InvocationError):
    def __init__(self, *args, **kwargs):
        self.msg = 'Parallel refresh is only possible with the "checkpoint" transaction style.'

    def __str__(self):
        return self.msg


class NameClashError(SamizdatException):
    pass


class UnsuitableNameError(SamizdatException):
    pass


class DanglingReferenceError(SamizdatException):
    pass


class TypeConfusionError(SamizdatException):
    pass


class DatabaseError(SamizdatException):
    def __init__(self, message, dberror, samizdat, sql):
        self.message = message
        self.dberror = dberror
        self.samizdat = samizdat
        self.sql = sql

    def __str__(self):
        return f'''
While executing:
{sqlfmt_debug(self.sql)}

a DB error was raised:
{self.dberror}

while we were processing the samizdat:
{repr(self.samizdat)}

furthermore:
{self.message}
'''


class DependencyCycleError(SamizdatException):
    def __init__(self, message, samizdats):
        self.message = message
        self.samizdats = samizdats

    def __str__(self):
        sd_subjects = ', '.join(self.samizdats)
        return f'{sd_subjects} : {self.message}'


class FunctionSignatureError(SamizdatException):
    def __init__(self, samizdat, candidate_arguments: List[str]):
        self.samizdat = samizdat
        self.candidate_arguments = candidate_arguments

    def __str__(self):
        sd_subject = repr(self.samizdat)
        candidate_args = '\n'.join(self.candidate_arguments)
        args_herald = f"the following candidates:\n{candidate_args}" if len(self.candidate_arguments) > 1 else f'"{candidate_args}"'
        return f'''
            After executing:
            {sqlfmt(self.samizdat.create())}

            which we did in order to create the samizdat function:
            {sd_subject}

            we were not able to identify the resulting database function via its call signature of:
            {self.samizdat.db_object_identity}

            because, we figure, that is not actually the effective call signature resulting from the function arguments, which are:
            "({self.samizdat.function_arguments})"

            We queried the database to find out what the effective call argument signature should be instead, and came up with:
            {args_herald}

            HINT: Amend the {sd_subject} .function_arguments_signature and/or .function_arguments attributes.
            For more information, consult the README.'''


class SQLTemplateException(SamizdatException):
    def __init__(self, missing, samizdats):
        message = f'Missing template variable{"s" if len(missing) > 1 else ""}: {", ".join(sorted(missing))}'
        super().__init__(message, samizdats)


class UnqualifiedModulePathException(SamizdatException):
    pass