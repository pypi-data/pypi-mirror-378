# Copyright Contributors to the Packit project.
# SPDX-License-Identifier: MIT

import copy
import functools
import json
from collections.abc import Mapping
from logging import getLogger
from typing import Any, Optional, Union

from marshmallow import (
    Schema,
    ValidationError,
    fields,
    post_load,
    pre_load,
    validates_schema,
)

from packit.actions import ActionName
from packit.config import (
    CommonPackageConfig,
    Config,
    Deployment,
    OshOptionsConfig,
    PackageConfig,
)
from packit.config.aliases import DEPRECATED_TARGET_MAP
from packit.config.commands import TestCommandConfig
from packit.config.common_package_config import MockBootstrapSetup
from packit.config.job_config import (
    JobConfig,
    JobConfigTriggerType,
    JobConfigView,
    JobType,
    get_default_jobs,
)
from packit.config.notifications import (
    FailureCommentNotificationsConfig,
    FailureIssueNotificationsConfig,
    NotificationsConfig,
    PullRequestNotificationsConfig,
)
from packit.config.requirements import LabelRequirementsConfig, RequirementsConfig
from packit.config.sources import SourcesItem
from packit.constants import (
    CHROOT_SPECIFIC_COPR_CONFIGURATION,
    FAST_FORWARD_MERGE_INTO_KEY,
)
from packit.sync import SyncFilesItem

logger = getLogger(__name__)


class StringOrListOfStringsField(fields.Field):
    """Field type expecting a string or a list"""

    def _serialize(self, value, attr, obj, **kwargs) -> list[str]:
        return [str(item) for item in value]

    def _deserialize(self, value, attr, data, **kwargs) -> list[str]:
        if isinstance(value, list) and all(isinstance(v, str) for v in value):
            return value
        if isinstance(value, str):
            return [value]
        raise ValidationError(f"Expected 'list[str]' or 'str', got {type(value)!r}.")


class SyncFilesItemSchema(Schema):
    """Schema for SyncFilesItem"""

    src = StringOrListOfStringsField()
    dest = fields.String()
    mkpath = fields.Boolean(dump_default=False)
    delete = fields.Boolean(dump_default=False)
    filters = fields.List(fields.String(), load_default=None)


class FilesToSyncField(fields.Field):
    """
    Field type representing SyncFilesItem

    This is needed in order to handle entries which are strings, instead
    of a dict matching SyncFilesItemSchema.
    """

    def _serialize(self, value: Any, attr: str, obj: Any, **kwargs) -> list[dict]:
        return SyncFilesItemSchema().dump(value)

    def _deserialize(
        self,
        value: Any,
        attr: Optional[str],
        data: Optional[Mapping[str, Any]],
        **kwargs,
    ) -> SyncFilesItem:
        if isinstance(value, dict):
            return SyncFilesItem(**SyncFilesItemSchema().load(value))
        if isinstance(value, str):
            return SyncFilesItem(src=[value], dest=value)
        raise ValidationError(f"Expected 'dict' or 'str', got {type(value)!r}.")


class ActionField(fields.Field):
    """
    Field class representing Action.
    """

    def _serialize(self, value: Any, attr: str, obj: Any, **kwargs):
        return {action_name.value: val for action_name, val in value.items()}

    def _deserialize(
        self,
        value: Any,
        attr: Optional[str],
        data: Optional[Mapping[str, Any]],
        **kwargs,
    ) -> dict:
        if not isinstance(value, dict):
            raise ValidationError(f"'dict' required, got {type(value)!r}.")

        self.validate_all_actions(actions=list(value))
        return {ActionName(key): val for key, val in value.items()}

    def validate_all_actions(self, actions: list) -> None:
        """
        Validates all keys and raises exception with list of all invalid keys
        """
        invalid_actions = [
            action for action in actions if not ActionName.is_valid_action(action)
        ]

        if invalid_actions:
            raise ValidationError(f"Unknown action(s) provided: {invalid_actions}")


class NotProcessedField(fields.Field):
    """
    Field class to mark fields which will not be processed, only generates warning.
    Can be passed additional message via additional_message parameter.

    :param str additional_message: additional warning message to be displayed
    """

    def _serialize(self, value: Any, attr: str, obj: Any, **kwargs):
        raise NotImplementedError

    def _deserialize(
        self,
        value: Any,
        attr: Optional[str],
        data: Optional[Mapping[str, Any]],
        **kwargs,
    ):
        logger.warning(f"{self.name!r} is no longer being processed.")
        additional_message = self.metadata.get("additional_message")
        if additional_message:
            logger.warning(f"{additional_message}")


class SourceSchema(Schema):
    """
    Schema for sources.
    """

    path = fields.String(required=True)
    url = fields.String(required=True)

    @post_load
    def make_instance(self, data, **_):
        return SourcesItem(**data)


class PullRequestNotificationsSchema(Schema):
    """Configuration of commenting on pull requests."""

    successful_build = fields.Bool(dump_default=False)

    @post_load
    def make_instance(self, data, **kwargs):
        return PullRequestNotificationsConfig(**data)


class FailureCommentNotificationsSchema(Schema):
    """Configuration of commenting on failures."""

    message = fields.String(load_default=None)

    @post_load
    def make_instance(self, data, **kwargs):
        return FailureCommentNotificationsConfig(**data)


class FailureIssueNotificationsSchema(Schema):
    """Configuration of createing issues in upstream."""

    create = fields.Bool(dump_default=True)

    @post_load
    def make_instance(self, data, **kwargs):
        return FailureIssueNotificationsConfig(**data)


class NotificationsSchema(Schema):
    """Configuration of notifications."""

    pull_request = fields.Nested(PullRequestNotificationsSchema)
    failure_comment = fields.Nested(FailureCommentNotificationsSchema)
    failure_issue = fields.Nested(FailureIssueNotificationsSchema)

    @post_load
    def make_instance(self, data, **kwargs):
        return NotificationsConfig(**data)


class TestCommandSchema(Schema):
    """Configuration of test command."""

    default_labels = fields.List(fields.String, load_default=None)
    default_identifier = fields.String(load_default=None)

    @post_load
    def make_instance(self, data, **kwargs):
        return TestCommandConfig(**data)


class LabelRequirementsSchema(Schema):
    present = fields.List(fields.String)
    absent = fields.List(fields.String)

    @post_load
    def make_instance(self, data, **kwargs):
        return LabelRequirementsConfig(**data)


class RequirementsSchema(Schema):
    """Configuration of test command."""

    label = fields.Nested(LabelRequirementsSchema, load_default=None)

    @post_load
    def make_instance(self, data, **kwargs):
        return RequirementsConfig(**data)


class ListOrDict(fields.Field):
    """Field type expecting a List[str] or Dict[str, Dict[str, Any]]
    Union is not supported by marshmallow so we have to validate manually :(
    https://github.com/marshmallow-code/marshmallow/issues/1191
    """

    def is_dict(self, value) -> bool:
        return not (
            not isinstance(value, dict)
            or not all(isinstance(k, str) for k in value)
            or not all(isinstance(v, dict) for v in value.values())
        )


class DistGitBranches(ListOrDict):
    ERR_MESSAGE = (
        "Expected 'list[str]' or 'dict[str, dict[str, list]]', got {value!r} (type {type!r})."
        '\nExample -> "dist_git_branches": '
        '{{"fedora-rawhide": {{"fast_forward_merge_into": ["f40"]}}, epel9: {{}}}}}}'
    )

    def _deserialize(
        self,
        value,
        attr,
        data,
        **kwargs,
    ) -> Union[list[str], dict[str, dict[str, list[str]]], None]:
        if not (
            (isinstance(value, list) and all(isinstance(v, str) for v in value))
            or self.is_dict(value)
        ):
            raise ValidationError(
                self.ERR_MESSAGE.format(value=value, type=type(value)),
            )
        return value

    def is_dict(self, value) -> bool:
        if not super().is_dict(value):
            return False
        if isinstance(value, dict):
            if any(
                fast_forward_merge_into
                for fast_forward_merge_into in value.values()
                if not isinstance(fast_forward_merge_into, dict)
            ):
                raise ValidationError(
                    self.ERR_MESSAGE.format(value=value, type=type(value)),
                )
            if any(
                key
                for fast_forward_merge_into in value.values()
                for key in fast_forward_merge_into
                if key != FAST_FORWARD_MERGE_INTO_KEY
            ):
                raise ValidationError(
                    self.ERR_MESSAGE.format(value=value, type=type(value)),
                )
        return True


class Targets(ListOrDict):
    def is_dict(self, value) -> bool:
        if not super().is_dict(value):
            return False
        # check the 'attributes', e.g. {'distros': ['centos-7']} or
        # {"additional_modules": "ruby:2.7,nodejs:12", "additional_packages": []}
        for attr in value.values():
            for key, value in attr.items():
                # distros is a list of str
                if key == "distros":
                    if isinstance(value, list) and all(
                        isinstance(distro, str) for distro in value
                    ):
                        return True
                    raise ValidationError(
                        f"Expected list[str], got {value!r} (type {type(value)!r})",
                    )
                # chroot-specific configuration:
                if key in CHROOT_SPECIFIC_COPR_CONFIGURATION:
                    expected_type = CHROOT_SPECIFIC_COPR_CONFIGURATION[key].__class__
                    if isinstance(value, expected_type):
                        return True
                    raise ValidationError(
                        f"Expected {expected_type}, got {value!r} (type {type(value)!r})",
                    )
                raise ValidationError(f"Unknown key {key!r} in {attr!r}")
        return True

    def _deserialize(self, value, attr, data, **kwargs) -> dict[str, dict[str, Any]]:
        targets_dict: dict[str, dict[str, Any]]
        if isinstance(value, list) and all(isinstance(v, str) for v in value):
            targets_dict = {key: {} for key in value}
        elif self.is_dict(value):
            targets_dict = value
        else:
            raise ValidationError(
                f"Expected 'list[str]' or 'dict[str,dict]', got {value!r} (type {type(value)!r}).",
            )

        for target in targets_dict:
            if target in DEPRECATED_TARGET_MAP:
                logger.warning(
                    f"Target '{target}' is deprecated. Please update your configuration "
                    f"file and use '{DEPRECATED_TARGET_MAP[target]}' instead.",
                )
        return targets_dict


class JobMetadataSchema(Schema):
    """Jobs metadata.

    TODO: to be removed after deprecation period.
          Will end also dist-git-branch and
          dist_git_branch deprecation period.
    """

    _targets = Targets(load_default=None, data_key="targets")
    timeout = fields.Integer()
    owner = fields.String(load_default=None)
    project = fields.String(load_default=None)
    dist_git_branches = DistGitBranches(load_default=None)
    branch = fields.String(load_default=None)
    scratch = fields.Boolean()
    list_on_homepage = fields.Boolean()
    preserve_project = fields.Boolean()
    use_internal_tf = fields.Boolean()
    additional_packages = fields.List(fields.String(), load_default=None)
    additional_repos = fields.List(fields.String(), load_default=None)
    bootstrap = fields.Enum(MockBootstrapSetup, load_default=None)
    fmf_url = fields.String(load_default=None)
    fmf_ref = fields.String(load_default=None)
    fmf_path = fields.String(load_default=None)
    skip_build = fields.Boolean()
    env = fields.Dict(keys=fields.String(), load_default=None)
    enable_net = fields.Boolean(load_default=False)
    tmt_plan = fields.String(load_default=None)
    tf_post_install_script = fields.String(load_default=None)
    tf_extra_params = fields.Dict(load_default=None)
    module_hotfixes = fields.Boolean()

    @pre_load
    def ordered_preprocess(self, data, **_):
        for key in ("dist-git-branch", "dist_git_branch"):
            if key in data:
                logger.warning(
                    f"Job metadata key {key!r} has been renamed to 'dist_git_branches', "
                    f"please update your configuration file.",
                )
                data["dist_git_branches"] = data.pop(key)
        for key in ("targets", "dist_git_branches"):
            if isinstance(data.get(key), str):
                # allow key value being specified as string, convert to list
                data[key] = [data.pop(key)]

        return data


def validate_repo_name(value):
    """
    marshmallow validation for a repository name. Any
    filename is acceptable: No slash, no zero char.
    """
    if any(c in "/\0" for c in value):
        raise ValidationError("Repository name must be a valid filename.")
    return True


class OshOptionsSchema(Schema):
    """
    Schema for processing additional osh options
    """

    analyzer = fields.String(load_default=None)
    config = fields.String(load_default=None)
    profile = fields.String(load_default=None)

    @post_load
    def make_instance(self, data, **_):
        return OshOptionsConfig(**data)


class CommonConfigSchema(Schema):
    """
    Common configuration options and methods for a package.
    """

    config_file_path = fields.String(load_default=None)
    specfile_path = fields.String(load_default=None)
    downstream_package_name = fields.String(load_default=None)
    upstream_project_url = fields.String(load_default=None)
    upstream_package_name = fields.String(
        load_default=None,
        validate=validate_repo_name,
    )
    paths = fields.List(fields.String())
    upstream_ref = fields.String(load_default=None)
    upstream_tag_template = fields.String()
    archive_root_dir_template = fields.String()
    dist_git_url = NotProcessedField(
        metadata={
            "additional_message": "it is generated from dist_git_base_url and "
            "downstream_package_name",
        },
        load_only=True,
    )
    dist_git_base_url = fields.String(load_default=None)
    dist_git_namespace = fields.String(load_default=None)
    allowed_gpg_keys = fields.List(fields.String(), load_default=None)
    spec_source_id = fields.Method(
        deserialize="spec_source_id_fm",
        serialize="spec_source_id_serialize",
    )
    files_to_sync = fields.List(FilesToSyncField())
    actions = ActionField(dump_default={})
    create_pr = fields.Bool(dump_default=True)
    sync_changelog = fields.Bool(dump_default=False)
    create_sync_note = fields.Bool(dump_default=True)
    patch_generation_ignore_paths = fields.List(fields.String(), load_default=None)
    patch_generation_patch_id_digits = fields.Integer(
        load_default=4,
        dump_default=4,
        validate=lambda x: x >= 0,
    )
    notifications = fields.Nested(NotificationsSchema)
    copy_upstream_release_description = fields.Bool(dump_default=False)
    sources = fields.List(fields.Nested(SourceSchema), load_default=None)
    merge_pr_in_ci = fields.Bool(dump_default=True)
    srpm_build_deps = fields.List(fields.String(), load_default=None)
    identifier = fields.String(load_default=None)
    packit_instances = fields.List(
        fields.Enum(Deployment),
        load_default=[Deployment.prod],
    )
    issue_repository = fields.String(load_default=None)
    release_suffix = fields.String(load_default=None)
    update_release = fields.Bool(dump_default=True)
    upstream_tag_include = fields.String()
    upstream_tag_exclude = fields.String()
    prerelease_suffix_pattern = fields.String()
    prerelease_suffix_macro = fields.String(load_default=None)
    upload_sources = fields.Bool(dump_default=True)
    test_command = fields.Nested(TestCommandSchema)
    require = fields.Nested(RequirementsSchema)
    status_name_template = fields.String(load_default=None)
    sync_test_job_statuses_with_builds = fields.Bool(dump_default=True)

    # Former 'metadata' keys
    _targets = Targets(load_default=None, data_key="targets")
    timeout = fields.Integer()
    owner = fields.String(load_default=None)
    project = fields.String(load_default=None)
    dist_git_branches = DistGitBranches(load_default=None)
    branch = fields.String(load_default=None)
    scratch = fields.Boolean()
    list_on_homepage = fields.Boolean()
    preserve_project = fields.Boolean()
    use_internal_tf = fields.Boolean()
    additional_packages = fields.List(fields.String(), load_default=None)
    additional_repos = fields.List(fields.String(), load_default=None)
    bootstrap = fields.Enum(MockBootstrapSetup, load_default=None)
    fmf_url = fields.String(load_default=None)
    fmf_ref = fields.String(load_default=None)
    fmf_path = fields.String(load_default=None)
    env = fields.Dict(keys=fields.String(), load_default=None)
    enable_net = fields.Boolean(load_default=False)
    allowed_pr_authors = fields.List(fields.String(), load_default=None)
    allowed_committers = fields.List(fields.String(), load_default=None)
    allowed_builders = fields.List(fields.String(), load_default=None)
    tmt_plan = fields.String(load_default=None)
    tf_post_install_script = fields.String(load_default=None)
    tf_extra_params = fields.Dict(load_default=None)
    module_hotfixes = fields.Boolean()

    # Image Builder integration
    image_distribution = fields.String(load_default=None)
    # these two are freeform so that users can immediately use IB's new features
    image_request = fields.Dict(load_default=None)
    image_customizations = fields.Dict(load_default=None)
    copr_chroot = fields.String(load_default=None)

    # Packaging tool used for interaction with lookaside cache
    pkg_tool = fields.String(load_default=None)
    sig = fields.String(load_default=None)
    version_update_mask = fields.String(load_default=None)

    parse_time_macros = fields.Dict(load_default=None)
    osh_diff_scan_after_copr_build = fields.Boolean(load_default=True)

    csmock_args = fields.String(load_default=None)
    osh_options = fields.Nested(OshOptionsSchema)

    use_target_repo_for_fmf_url = fields.Boolean(load_default=False)

    clone_repos_before_run_condition = fields.Boolean(load_default=False)

    @staticmethod
    def spec_source_id_serialize(value: CommonPackageConfig):
        return value.spec_source_id

    @staticmethod
    def spec_source_id_fm(value: Union[str, int]):
        """
        method used in spec_source_id field.Method
        If value is int, it is transformed int -> "Source" + str(int)

        ex.
        1 -> "Source1"

        :return str: prepends "Source" in case input value is int
        """
        if value:
            try:
                value = int(value)
            except ValueError:
                # not a number
                pass
            else:
                # is a number!
                value = f"Source{value}"
        return value

    @post_load
    def make_instance(self, data, **_):
        return CommonPackageConfig(**data)


class JobConfigSchema(Schema):
    """
    Schema for processing JobConfig config data.
    """

    job = fields.Enum(JobType, required=True, attribute="type")
    trigger = fields.Enum(JobConfigTriggerType, required=True)
    skip_build = fields.Boolean()
    manual_trigger = fields.Boolean()
    labels = fields.List(fields.String(), load_default=None)
    packages = fields.Dict(
        keys=fields.String(),
        values=fields.Nested(CommonConfigSchema()),
    )
    package = fields.String(load_default=None)

    # sidetag group identifier for downstream Koji builds and Bodhi updates
    sidetag_group = fields.String(load_default=None)

    # packages that depend on this downstream Koji build to be tagged into
    # a particular sidetag group
    dependents = fields.List(fields.String(), load_default=None)

    # packages whose downstream Koji builds are required to be tagged into
    # a particular sidetag group by this downstream Koji build or Bodhi update
    dependencies = fields.List(fields.String(), load_default=None)

    @pre_load
    def ordered_preprocess(self, data, **_):
        for package, config in data.get("packages", {}).items():
            for key in ("targets", "dist_git_branches"):
                if isinstance(config, dict) and isinstance(config.get(key), str):
                    # allow key value being specified as string, convert to list
                    data["packages"][package][key] = [config.pop(key)]

        return data

    @validates_schema
    def specfile_path_defined(self, data: dict, **_):
        """Check if a 'specfile_path' is specified for each package

        The only time 'specfile_path' is not required, is when the job is a
        'test' job.

        Args:
            data: partially loaded configuration data.

        Raises:
            ValidationError, if 'specfile_path' is not specified when
            it should be.
        """
        # Note: At this point, 'data' is still a dict, but values are already
        # loaded, this is why 'data["type"]' is already a JobType and not a string,
        # and the package configs below are PackageConfig objects, not dictionaries.
        if (data["type"] == JobType.tests and data.get("skip_build")) or data.get(
            "specfile_path",
        ):
            return

        errors = {}
        package: str
        config: PackageConfig
        for package, config in data.get("packages", {}).items():
            if not config.specfile_path:
                errors[package] = [
                    "'specfile_path' is not specified or "
                    "no specfile was found in the repo",
                ]
        if errors:
            raise ValidationError(errors)

    @post_load
    def make_instance(self, data, **_):
        package = data.pop("package")
        job_config = JobConfig(**data)
        return JobConfigView(job_config, package) if package else job_config


class PackageConfigSchema(Schema):
    """
    Schema for processing PackageConfig config data.

    This class is intended to handle all the logic that is internal
    to the configuration and it is possible to be done while loading
    or dumping the configuration.

    This includes, for example, setting default values which depend on
    the value of other keys, or validating key values according to the
    value of other keys.

    It does not include setting the value of keys based on context
    *external* to the config file (if there is a spec-file in the current
    path, for example).
    """

    jobs = fields.Nested(JobConfigSchema, many=True)
    packages = fields.Dict(
        keys=fields.String(),
        values=fields.Nested(CommonConfigSchema()),
    )

    # list of deprecated keys and their replacement (new,old)
    deprecated_keys: Union[None, tuple[tuple[str, str]]] = None

    @pre_load
    def ordered_preprocess(self, data: dict, **_) -> dict:
        """Rename deprecated keys, and set defaults for 'packages' and 'jobs'

        Args:
            data: configuration dictionary as loaded from packit.yaml

        Returns:
            Transformed configuration dictionary with defaults
            for 'packages' and 'jobs' set.
        """
        # Log the config before any pre-processing is done
        logger.debug(
            "Package config before pre-loading: %s",
            json.dumps(data, separators=(",", ":")),
        )

        return functools.reduce(
            lambda d, f: f(d),
            [
                self.rename_deprecated_keys,
                self._convert_to_monorepo,
                self._set_default_jobs,
                # By this point, we expect both 'packages' and 'jobs' to be
                # present in the config.
                self.rearrange_packages,
                self.rearrange_jobs,
                self.process_job_triggers,
            ],
            # Create a deepcopy(), so that loading doesn't modify the
            # dictionary received.
            copy.deepcopy(data),
        )

    def rename_deprecated_keys(self, data: dict) -> dict:
        """
        Based on tuples stored in tuple cls.deprecated_keys, reassigns old keys values to new keys,
        in case new key is None and logs warning
        :param data: conf dictionary to process
        :return: processed dictionary
        """
        if not data:  # data is None when .packit.yaml is empty
            return data

        if not self.deprecated_keys:
            return data

        for new_key_name, old_key_name in self.deprecated_keys:
            old_key_value = data.get(old_key_name)
            if old_key_value:
                logger.warning(
                    f"{old_key_name!r} configuration key was renamed to {new_key_name!r},"
                    f" please update your configuration file.",
                )
                new_key_value = data.get(new_key_name)
                if not new_key_value:
                    # prio: new > old
                    data[new_key_name] = old_key_value
                del data[old_key_name]
        return data

    @staticmethod
    def _convert_to_monorepo(data: dict) -> dict:
        """Converts the package config to the monorepo syntax, if it's
        a single-package config.

        Args:
            data: package config of either single-repo or monorepo package.

        Returns:
            Dictionary that adheres to the monorepo syntax.
        """

        # Don't use 'setdefault' in this case, as we should expect
        # downstream_package_name only if there is no 'packages' key.
        if "packages" not in data:
            package_name = data.pop("downstream_package_name")
            paths = data.pop("paths", ["./"])
            data["packages"] = {
                package_name: {
                    "downstream_package_name": package_name,
                    "paths": paths,
                },
            }
        return data

    @staticmethod
    def _set_default_jobs(data: dict) -> dict:
        """Add default jobs, if none are configured.

        Args:
            data: package config that may or may not contain any jobs defined.

        Returns:
            Dictionary with package config that contains default jobs if none
            were present.
        """
        data.setdefault("jobs", get_default_jobs())
        return data

    @staticmethod
    def rearrange_packages(data: dict) -> dict:
        """Update package objects with top-level configuration values

        Top-level keys and values are copied to each package object if
        the given key is not set in that object already.

        Remove these keys from the top-level and return a dictionary
        containing only a 'packages' and 'jobs' key.

        Args:
            data: configuration dictionary, before any of the leaves
                having been loaded.

        Returns:
            A re-arranged configuration dictionary.
        """
        # Pop 'packages' and 'jobs' in order for 'data'
        # to contain only keys other then these when it comes
        # to merging it bellow.
        packages = data.pop("packages")
        jobs = data.pop("jobs")
        for k, v in packages.items():
            # First set the defaults which are not inherited from
            # the top-level, in case they are not set yet.
            v.setdefault("downstream_package_name", k)
            # Inherit default values from the top-level.
            v.update(data | v)
        return {"packages": packages, "jobs": jobs}

    @staticmethod
    def rearrange_jobs(data: dict) -> dict:
        """Set the selected package config objects in each job, and set defaults
        according to the values specified on the level of job-objects (if any).

        Args:
            data: Configuration dict with 'packages' and 'jobs' already in place.

        Returns:
            Configuration dict where the package objects in jobs are correctly set.
        """
        packages = data["packages"]
        jobs = data["jobs"]
        errors = {}
        for i, job in enumerate(jobs):
            # Validate the 'metadata' field if there is any, and merge its
            # content with the job.
            # Do this here in order to avoid complications further in the
            # loading process.
            if metadata := job.pop("metadata", {}):
                logger.warning(
                    "The 'metadata' key in jobs is deprecated and can be removed. "
                    "Nest config options from 'metadata' directly under the job object.",
                )
                schema = JobMetadataSchema()
                if errors := schema.validate(metadata):
                    raise ValidationError(errors)
                if not_nested_metadata_keys := set(schema.fields).intersection(job):
                    raise ValidationError(
                        f"Keys: {not_nested_metadata_keys} are defined outside job metadata "
                        "dictionary. Mixing obsolete metadata dictionary and new job keys "
                        "is not possible. Remove obsolete nested job metadata dictionary.",
                    )
                job.update(metadata)

            top_keys = {}
            for key in JobConfigSchema().fields:
                if (value := job.pop(key, None)) is not None:
                    top_keys[key] = value

            selected_packages = top_keys.pop("packages", None)
            # Check that only packages which are defined on the top-level are selected.
            # Do this here b/c the code further down requires this to be correct.
            incorrect_packages = (
                set(selected_packages).difference(packages)
                if isinstance(selected_packages, (dict, list))
                else None
            )
            if incorrect_packages:
                errors[f"jobs[{i}].packages"] = (
                    f"Undefined package(s) referenced: {', '.join(incorrect_packages)}."
                )
                continue

            # There is no 'packages' key in the job, so
            # the job should handle all the top-level packages.
            if not selected_packages:
                jobs[i] = top_keys | {
                    "packages": {k: v | job for k, v in packages.items()},
                }
            # Some top-level packages are selected to be
            # handled by the job.
            elif isinstance(selected_packages, list):
                jobs[i] = top_keys | {
                    "packages": {
                        k: v | job
                        for k, v in packages.items()
                        if k in selected_packages
                    },
                }
            # Some top-level packages are selected to be
            # handled by the job AND have some custom config.
            elif isinstance(selected_packages, dict):
                jobs[i] = top_keys | {
                    "packages": {
                        k: packages[k] | job | v for k, v in selected_packages.items()
                    },
                }
            else:
                errors[f"'jobs[{i}].packages'"] = [
                    f"Type is {type(selected_packages)} instead of 'list' or 'dict'.",
                ]

        if errors:
            # This will shadow all other possible errors in the configuration,
            # as the process doesn't even get to the validation phase.
            raise ValidationError(errors)

        return data

    @staticmethod
    def process_job_triggers(data: dict) -> dict:
        """
        Expands jobs with multiple triggers.

        For example a job with `trigger: commit | koji_build` will be expanded into two jobs
        with the same options except for `trigger`; the first one will have `trigger: commit`
        and the second one will have `trigger: koji_build`.
        """
        jobs = data["jobs"]
        i = len(jobs) - 1
        while i >= 0:
            if not isinstance(job_trigger := jobs[i].get("trigger", ""), str):
                # let schema validation handle this
                i -= 1
                continue

            triggers = [t.strip() for t in job_trigger.split("|")]
            if len(triggers) <= 1:
                i -= 1
                continue
            original_job = jobs.pop(i)
            for trigger in reversed(triggers):
                job = copy.deepcopy(original_job)
                job["trigger"] = trigger
                jobs.insert(i, job)
            i -= 1
        return data

    @post_load
    def make_instance(self, data: dict, **_) -> PackageConfig:
        return PackageConfig(**data)


class UserConfigSchema(Schema):
    """
    Schema for processing Config config data.
    """

    debug = fields.Bool()
    fas_user = fields.String()
    fas_password = fields.String()
    keytab_path = fields.String()
    redhat_api_refresh_token = fields.String()
    upstream_git_remote = fields.String()
    github_token = fields.String()
    pagure_user_token = fields.String()
    pagure_fork_token = fields.String()
    github_app_installation_id = fields.String()
    github_app_id = fields.String()
    github_app_cert_path = fields.String()
    authentication = fields.Dict()
    command_handler = fields.String()
    command_handler_work_dir = fields.String()
    command_handler_pvc_env_var = fields.String()
    command_handler_image_reference = fields.String()
    command_handler_k8s_namespace = fields.String()
    command_handler_pvc_volume_specs = fields.List(fields.Dict())
    command_handler_storage_class = fields.String()
    appcode = fields.String()
    kerberos_realm = fields.String()
    package_config_path = fields.String(dump_default=None)
    koji_build_command = fields.String()
    pkg_tool = fields.String()
    repository_cache = fields.String(dump_default=None)
    add_repositories_to_repository_cache = fields.Bool(dump_default=True)
    default_parse_time_macros = fields.Dict(load_default=None)

    @post_load
    def make_instance(self, data, **kwargs):
        return Config(**data)
