# Generate and consume rpm lockfiles
#
# Copyright (C) 2023 Ralph Bean
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions of
# the GNU General Public License v.2, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY expressed or implied, including the implied warranties of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.  You should have received a copy of the
# GNU General Public License along with this program; if not, write to the
# Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.  Any Red Hat trademarks that are incorporated in the
# source code or documentation are not subject to the GNU General Public
# License and may only be used or replicated with the express permission of
# Red Hat, Inc.
#

import logging
import os

import dnf.cli.commands.install
import dnf.conf.substitutions
import dnf.exceptions
import hawkey
from dnf import Plugin
from dnf.cli import commands
from dnf.cli.option_parser import OptionParser
from dnf.i18n import _

logger = logging.getLogger("dnf")


class Lockfile(Plugin):
    name = "lockfile"

    def __init__(self, base, cli):
        """Initialize the plugin instance."""
        super(Lockfile, self).__init__(base, cli)
        if cli is not None:
            cli.register_command(LockfileCommand)


class LockfileCommand(commands.Command):
    nevra_forms = {
        "lockfile-n": hawkey.FORM_NAME,
        "lockfile-na": hawkey.FORM_NA,
        "lockfile-nevra": hawkey.FORM_NEVRA,
    }
    alternatives_provide = "alternative-for({})"

    aliases = ("lockfile",) + tuple(nevra_forms.keys())
    summary = _("resolve a package or packages to a lockfile")

    @staticmethod
    def set_argparser(parser):
        parser.add_argument(
            "--lockfile",
            default=f"{os.getcwd()}/rpms.txt",
            help=_("Location to write the lockfile"),
        )
        parser.add_argument(
            "--namespaced",
            action="store_true",
            default=False,
            help=_("Add namespace information to each resolved rpm"),
        )
        parser.add_argument(
            "package",
            nargs="+",
            metavar=_("PACKAGE"),
            action=OptionParser.ParseSpecGroupFileCallback,
            help=_("Package to resolve"),
        )

    def configure(self):
        """Verify that conditions are met so that this command can run.
        That there are enabled repositories with gpg keys, and that
        this command is called with appropriate arguments.
        """
        demands = self.cli.demands
        demands.sack_activation = True
        demands.available_repos = True
        demands.resolving = True
        demands.root_user = False
        commands._checkGPGKey(self.base, self.cli)
        if not self.opts.filenames:
            commands._checkEnabledRepo(self.base)

    def run(self):
        results = []
        error_pkgs = []
        error_module_specs = []

        nevra_forms = self._get_nevra_forms_from_command()

        self.cli._populate_update_security_filter(self.opts)

        skipped_grp_specs = []
        if self.opts.grp_specs:
            if dnf.base.WITH_MODULES:
                raise NotImplementedError()
            else:
                skipped_grp_specs = self.opts.grp_specs

        if self.opts.filenames and nevra_forms:
            self._inform_not_a_valid_combination(self.opts.filenames)
            if self.base.conf.strict:
                raise dnf.exceptions.Error(_("Nothing to do."))
        else:
            error_pkgs, files = self._record_files()
            results = results + files

        if skipped_grp_specs and nevra_forms:
            self._inform_not_a_valid_combination(skipped_grp_specs)
            if self.base.conf.strict:
                raise dnf.exceptions.Error(_("Nothing to do."))
        elif skipped_grp_specs:
            self._record_groups(skipped_grp_specs)

        errors, packages = self._record_packages(nevra_forms)
        results = results + packages

        if (errors or error_pkgs or error_module_specs) and self.base.conf.strict:
            raise dnf.exceptions.PackagesNotAvailableError(
                _("Unable to find a match"),
                pkg_spec=" ".join(errors),
                packages=error_pkgs,
            )

        with open(self.opts.lockfile, "w") as f:
            f.write("\n".join(sorted(results)))
        logger.info(f"Wrote {len(results)} packages to {self.opts.lockfile}")

    def _get_nevra_forms_from_command(self):
        if self.opts.command in self.nevra_forms:
            return [self.nevra_forms[self.opts.command]]
        else:
            return []

    def _inform_not_a_valid_combination(self, forms):
        for form in forms:
            msg = _("Not a valid form: %s")
            logger.warning(msg, self.base.output.term.bold(form))

    def _record_files(self):
        errors, results = [], []
        strict = self.base.conf.strict
        for pkg in self.base.add_remote_rpms(
            self.opts.filenames, strict=strict, progress=self.base.output.progress
        ):
            try:
                results.append(self._format(pkg))
            except dnf.exceptions.MarkingError:
                msg = _("No match for argument: %s")
                logger.info(msg, self.base.output.term.bold(pkg.location))
                errors.append(pkg)

        return errors, results

    def _record_groups(self, grp_specs):
        # TODO - groups.
        raise NotImplementedError()

    def _report_alternatives(self, pkg_spec):
        query = self.base.sack.query().filterm(
            provides=self.alternatives_provide.format(pkg_spec)
        )
        if query:
            msg = _('There are following alternatives for "{0}": {1}')
            logger.info(
                msg.format(
                    pkg_spec, ", ".join(sorted(set([alt.name for alt in query])))
                )
            )

    def _format(self, package):
        # TODO - lots of work to do here to experiment with formats
        nevr = f"{package.name}-{package.evr}"
        result = nevr

        if self.opts.namespaced:
            if package.reponame in package.base.repos:
                if package.repo.metalink:
                    result = result + f" @ metalink://{package.repo.metalink}"
                else:
                    result = result + f" @ id://{package.repo.id}"

        return result

    def _record_packages(self, nevra_forms):
        errors, results = [], []
        for pkg_spec in self.opts.pkg_specs:
            try:
                subj = dnf.subject.Subject(pkg_spec)
                solution = subj.get_best_solution(
                    self.base.sack, forms=nevra_forms, with_src=False
                )
                query = solution["query"]
                if not query:
                    self.base._raise_package_not_found_error(
                        pkg_spec, forms=nevra_forms, reponame=None
                    )
                for name, packages in (
                    solution["query"].available()._name_dict().items()
                ):
                    found = []
                    for package in packages:
                        found.append(self._format(package))
                    results.append(sorted(found)[-1])
            except dnf.exceptions.Error as e:
                msg = "{}: {}".format(e.value, self.base.output.term.bold(pkg_spec))
                logger.info(msg)
                self.base._report_icase_hint(pkg_spec)
                self._report_alternatives(pkg_spec)
                errors.append(pkg_spec)

        return errors, results
