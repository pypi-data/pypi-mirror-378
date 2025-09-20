"""Submodule defining the available update operations and lint checks."""

__all__ = [
    "ACTIONS",
    "ASSETS",
    "Metadata",
    "Rename",
    "Replace",
    "Translate",
]

import dataclasses
import logging
from collections.abc import Callable
from pathlib import Path
from typing import Literal

from ocpiupdate.version import V2_4_7, Version


@dataclasses.dataclass
class Metadata:
    """TODO."""

    dry_run: bool
    logger: logging.Logger
    to_version: Version
    workers_with_proxies: set[str]


@dataclasses.dataclass
class Action:
    """TODO."""

    identifier: str
    minimum_version_target: Version


@dataclasses.dataclass
class Replace(Action):
    """TODO."""

    identifier_to_search: str
    text_to_replace: list[str]
    text_to_substitute: list[str]

    def run(
        self,
        path: Path,
        metadata: Metadata,
    ) -> bool:
        """Replace any matching text in a given file."""
        if metadata.logger is not None:
            for text_to_replace, text_to_substitute in zip(
                self.text_to_replace,
                self.text_to_substitute,
                strict=True,
            ):
                metadata.logger.debug(
                    "replace(%s, %s, %s)",
                    path,
                    text_to_replace,
                    text_to_substitute,
                )
        with path.open("r", encoding="utf-8") as file:
            lines = file.readlines()
        changed_something = False
        for i, line in enumerate(lines):
            for text_to_replace, text_to_substitute in zip(
                self.text_to_replace,
                self.text_to_substitute,
                strict=True,
            ):
                if text_to_replace in line:
                    lines[i] = line.replace(text_to_replace, text_to_substitute)
                    if metadata.logger is not None:
                        metadata.logger.info(
                            "Replaced '%s' with '%s' on line %d of '%s'",
                            text_to_replace,
                            text_to_substitute,
                            i,
                            path,
                        )
                    changed_something = True
                    break
        if changed_something and not metadata.dry_run:
            with path.open("w", encoding="utf-8") as file:
                file.writelines(lines)
        return changed_something


@dataclasses.dataclass
class Rename(Action):
    """TODO."""

    from_glob: str
    to_path: Callable[[Path], Path]
    is_excluded: Callable[[Path, Metadata], bool] | None = None
    search_types: list[str] | None = None
    search_from: Callable[[Path], list[str]] | None = None
    search_to: Callable[[Path], str] | None = None

    def run(
        self,
        project: Path,
        metadata: Metadata,
    ) -> list[tuple[Path, Path]]:
        """Rename matching files in the given project."""
        if metadata.logger is not None:
            metadata.logger.debug(
                "rename(%s, %s)",
                project,
                self.from_glob,
            )
        files_moved = []
        for from_file_path in project.glob(self.from_glob):
            if self.is_excluded is not None and self.is_excluded(
                from_file_path,
                metadata,
            ):
                metadata.logger.debug("File '%s' is excluded", from_file_path)
                continue
            to_file_path = self.to_path(from_file_path)
            to_file_path.parent.mkdir(parents=True, exist_ok=True)
            if not metadata.dry_run:
                from_file_path.rename(to_file_path)
            if metadata.logger is not None:
                metadata.logger.info("Moved '%s' to '%s'", from_file_path, to_file_path)
            files_moved.append((from_file_path, to_file_path))
        return files_moved

    def generate_replace_actions(self, from_path: Path, to_path: Path) -> list[Replace]:
        """Generate replace actions relating to this rename action."""
        if (
            self.search_types is None
            or self.search_from is None
            or self.search_to is None
        ):
            return []
        text_from = self.search_from(from_path)
        text_to = self.search_to(to_path)
        return [
            Replace(
                identifier=self.identifier,
                minimum_version_target=self.minimum_version_target,
                identifier_to_search=search_type,
                text_to_replace=text_from,
                text_to_substitute=[text_to] * len(text_from),
            )
            for search_type in self.search_types
        ]


@dataclasses.dataclass
class Translate(Action):
    """TODO."""

    from_format: Literal["makefile"] = "makefile"
    to_format: Literal["xml"] = "xml"


ACTIONS: dict[str, Action] = {
    # See https://opencpi.dev/t/broken-hdl-worker-search-path-on-slave-attributes/105
    "rename_hdl_owds_to_hyphen_hdl": Rename(
        identifier="protocol",
        minimum_version_target=V2_4_7,
        from_glob="**/*.hdl/*.xml",
        to_path=lambda file: file.parent / f"{file.stem}-hdl.xml",
        is_excluded=lambda file, metadata: file.stem != file.parent.stem
        or (
            metadata.to_version <= V2_4_7
            and file.parent.stem in metadata.workers_with_proxies
        ),
    ),
    "rename_rcc_owds_to_hyphen_rcc": Rename(
        identifier="protocol",
        minimum_version_target=V2_4_7,
        from_glob="**/*.rcc/*.xml",
        to_path=lambda file: file.parent / f"{file.stem}-rcc.xml",
        is_excluded=lambda file, metadata: file.stem != file.parent.stem
        or (
            metadata.to_version <= V2_4_7
            and file.parent.stem in metadata.workers_with_proxies
        ),
    ),
    "rename_spec_to_comp_in_components": Rename(
        identifier="component",
        minimum_version_target=V2_4_7,
        from_glob="components/**/specs/*[-_]spec.xml",
        to_path=lambda file: file.parent.parent
        / f"{file.stem[:-5]}.comp"
        / f"{file.stem[:-5]}-comp.xml",
        search_types=["hdl-worker", "rcc-worker"],
        search_from=lambda file: [file.name, file.stem],
        search_to=lambda file: file.stem[:-5],
    ),
    "rename_spec_to_comp_in_hdl": Rename(
        identifier="component",
        minimum_version_target=V2_4_7,
        from_glob="hdl/**/specs/*[-_]spec.xml",
        to_path=lambda file: file.parent.parent
        / f"{file.stem[:-5]}.comp"
        / f"{file.stem[:-5]}-comp.xml",
        search_types=["hdl-worker", "rcc-worker"],
        search_from=lambda file: [file.name, file.stem],
        search_to=lambda file: file.stem[:-5],
    ),
    "rename_protocol_to_prot": Rename(
        identifier="protocol",
        minimum_version_target=V2_4_7,
        from_glob="**/specs/*[-_]protocol.xml",
        to_path=lambda file: file.parent / f"{file.stem[:-9]}-prot.xml",
        search_types=["component", "hdl-worker", "rcc-worker"],
        search_from=lambda file: [file.name, file.stem],
        search_to=lambda file: file.stem,
    ),
    "rename_underscore_prot_to_hyphen_prot": Rename(
        identifier="protocol",
        minimum_version_target=V2_4_7,
        from_glob="**/specs/*_prot.xml",
        to_path=lambda file: file.parent / f"{file.stem[:-5]}-prot.xml",
        search_types=["component", "hdl-worker", "rcc-worker"],
        search_from=lambda file: [file.name, file.stem],
        search_to=lambda file: file.stem,
    ),
    "translate_applications_from_makefile_to_xml": Translate(
        identifier="applications",
        minimum_version_target=V2_4_7,
    ),
    "translate_hdl_adapters_from_makefile_to_xml": Translate(
        identifier="hdl-adapters",
        minimum_version_target=V2_4_7,
    ),
    "translate_hdl_assemblies_from_makefile_to_xml": Translate(
        identifier="hdl-assemblies",
        minimum_version_target=V2_4_7,
    ),
    "translate_hdl_cards_from_makefile_to_xml": Translate(
        identifier="hdl-cards",
        minimum_version_target=V2_4_7,
    ),
    "translate_hdl_device_from_makefile_to_xml": Translate(
        identifier="hdl-device",
        minimum_version_target=V2_4_7,
    ),
    "translate_hdl_platforms_from_makefile_to_xml": Translate(
        identifier="hdl-platforms",
        minimum_version_target=V2_4_7,
    ),
    "translate_hdl_primitives_from_makefile_to_xml": Translate(
        identifier="hdl-primitives",
        minimum_version_target=V2_4_7,
    ),
    "translate_hdl_worker_from_makefile_to_xml": Translate(
        identifier="hdl-worker",
        minimum_version_target=V2_4_7,
    ),
    "translate_project_from_makefile_to_xml": Translate(
        identifier="project",
        minimum_version_target=V2_4_7,
    ),
    "translate_rcc_worker_from_makefile_to_xml": Translate(
        identifier="rcc-worker",
        minimum_version_target=V2_4_7,
    ),
}


@dataclasses.dataclass
class Paths:
    """TODO."""

    makefiles: list[str] = dataclasses.field(default_factory=list)
    xml: str | Callable[[Path], Path] | None = None


@dataclasses.dataclass
class Treesitter:
    """TODO."""

    fragments_to_ignore: list[str] = dataclasses.field(default_factory=list)
    types_to_ignore: list[str] = dataclasses.field(default_factory=list)

    def __post_init__(self) -> None:
        """TODO."""
        self.fragments_to_ignore.extend(
            [
                "$(if $(realpath $(OCPI_CDK_DIR)),,\\\n"
                "\t$(error The OCPI_CDK_DIR environment variable is not set correctly.))\n",  # noqa: E501
                "$(if $(OCPI_CDK_DIR),,$(error The OCPI_CDK_DIR environment variable must be set for this Makefile.))\n",  # noqa: E501
            ],
        )
        self.types_to_ignore.extend(["comment"])


@dataclasses.dataclass
class Variables:
    """TODO."""

    accepted: list[str] = dataclasses.field(default_factory=list)
    not_recommended: dict[str, str] = dataclasses.field(default_factory=dict)
    recommended: dict[str, str] = dataclasses.field(default_factory=dict)
    translations: dict[str, str] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class Asset:
    """TODO."""

    name: str
    tag: str
    paths: Paths = dataclasses.field(default_factory=Paths)
    treesitter: Treesitter = dataclasses.field(default_factory=Treesitter)
    variables: Variables = dataclasses.field(default_factory=Variables)


_LIBRARY_VARIABLES = Variables(
    accepted=[
        "tests",
        "workers",
    ],
    not_recommended={
        "hdllibraries": (
            "`hdllibraries` imports a list of primitive libraries for "
            "all assets in this component library. This import should "
            "be performed on each worker as necessary not on the "
            "collection as a whole"
        ),
        "package": (
            "`package` directs the asset to pretend it is located "
            "somewhere else. If this is intended, the asset should be "
            "moved to that other location. If its inclusion is "
            "redundant (e.g. the asset is already located in the place "
            "that matches `package`), then `package` should be removed"
        ),
    },
    recommended={},
)


ASSETS = {
    "applications": Asset(
        name="applications",
        paths=Paths(
            makefiles=["applications/Makefile"],
            xml="applications/applications.xml",
        ),
        tag="applications",
        treesitter=Treesitter(
            fragments_to_ignore=[
                "include $(OCPI_CDK_DIR)/include/applications.mk\n",
            ],
        ),
        variables=Variables(
            accepted=[
                "applications",
            ],
        ),
    ),
    "hdl-adapters": Asset(
        name="hdl-adapters",
        paths=Paths(
            makefiles=["hdl/adapters/Library.mk", "hdl/adapters/Makefile"],
            xml="hdl/adapters/adapters.xml",
        ),
        tag="library",
        treesitter=Treesitter(
            fragments_to_ignore=[
                "include $(OCPI_CDK_DIR)/include/library.mk\n",
            ],
        ),
        variables=_LIBRARY_VARIABLES,
    ),
    "hdl-assemblies": Asset(
        name="hdl-assemblies",
        paths=Paths(
            makefiles=["hdl/assemblies/Makefile"],
            xml="hdl/assemblies/assemblies.xml",
        ),
        tag="assemblies",
        treesitter=Treesitter(
            fragments_to_ignore=[
                "include $(OCPI_CDK_DIR)/include/hdl/hdl-assemblies.mk\n",
            ],
        ),
        variables=Variables(
            accepted=[
                "assemblies",
            ],
            not_recommended={
                "componentlibraries": (
                    "`componentlibraries` should be set as a top level "
                    "attribute inside the specific assemblies that the import "
                    "is required for. Setting it at the `assemblies` level is "
                    "not recommended."
                ),
            },
        ),
    ),
    "hdl-cards": Asset(
        name="hdl-cards",
        paths=Paths(
            makefiles=["hdl/cards/Library.mk", "hdl/cards/Makefile"],
            xml="hdl/cards/cards.xml",
        ),
        tag="library",
        treesitter=Treesitter(
            fragments_to_ignore=[
                "include $(OCPI_CDK_DIR)/include/library.mk\n",
            ],
        ),
        variables=_LIBRARY_VARIABLES,
    ),
    "hdl-device": Asset(
        name="hdl-device",
        paths=Paths(
            makefiles=[
                "hdl/adapters/*.hdl/Makefile",
                "hdl/cards/*.hdl/Makefile",
                "hdl/devices/*.hdl/Makefile",
            ],
            xml=lambda file: file.parent / f"{file.parent.stem}.xml"
            if (file.parent / f"{file.parent.stem}.xml").exists()
            else file.parent / f"{file.parent.stem}-hdl.xml",
        ),
        tag="hdldevice",
        treesitter=Treesitter(
            fragments_to_ignore=[
                "include $(OCPI_CDK_DIR)/include/worker.mk\n",
            ],
        ),
        variables=Variables(
            accepted=[
                "excludeplatforms",
                "excludetargets",
                "hdlexactpart",
                "hdlplatforms",
                "language",
                "libraries",
                "onlyplatforms",
                "onlytargets",
                "sourcefiles",
                "version",
            ],
            recommended={
                "language": (
                    "`language` defaults to 'verilog' if not defined, for "
                    "backwards compatibility with very early versions of "
                    "OpenCPI which didn't feature multiple languages. To avoid "
                    "accidentally creating a Verilog Worker, always define "
                    '`language="vhdl"`'
                ),
                "version": (
                    "`version` defaults to '1' if not defined, for backwards "
                    "compatibility with versions of OpenCPI before ~v1.4. To "
                    "avoid accidentally using the older data flow paradigm, "
                    'always define `version="2"`'
                ),
            },
            translations={"hdllibraries": "libraries"},
        ),
    ),
    "hdl-devices": Asset(
        name="hdl-devices",
        paths=Paths(
            makefiles=["hdl/devices/Library.mk", "hdl/devices/Makefile"],
            xml="hdl/devices/devices.xml",
        ),
        tag="library",
        treesitter=Treesitter(
            fragments_to_ignore=[
                "include $(OCPI_CDK_DIR)/include/library.mk\n",
            ],
        ),
        variables=_LIBRARY_VARIABLES,
    ),
    "hdl-platforms": Asset(
        name="hdl-platforms",
        paths=Paths(
            makefiles=["hdl/platforms/Makefile"],
            xml="hdl/platforms/platforms.xml",
        ),
        tag="hdlplatforms",
        treesitter=Treesitter(
            fragments_to_ignore=[
                "include $(OCPI_CDK_DIR)/include/hdl/hdl-platforms.mk\n",
            ],
        ),
    ),
    "hdl-primitives": Asset(
        name="hdl-primitives",
        paths=Paths(
            makefiles=["hdl/primitives/Makefile"],
            xml="hdl/primitives/primitives.xml",
        ),
        tag="hdlprimitives",
        treesitter=Treesitter(
            fragments_to_ignore=[
                "include $(OCPI_CDK_DIR)/include/hdl/hdl-primitives.mk\n",
            ],
        ),
        variables=Variables(
            accepted=[
                "libraries",
            ],
            recommended={
                "libraries": (
                    "`libraries` is used to determine the order of compilation "
                    "of primitive libraries. If you have any dependencies "
                    "between libraries, you should define it."
                ),
            },
            translations={"primitivelibraries": "libraries"},
        ),
    ),
    "hdl-worker": Asset(
        name="hdl-worker",
        paths=Paths(
            makefiles=[
                "components/*.hdl/Makefile",
                "components/*/*.hdl/Makefile",
            ],
            xml=lambda file: file.parent / f"{file.parent.stem}.xml"
            if (file.parent / f"{file.parent.stem}.xml").exists()
            else file.parent / f"{file.parent.stem}-hdl.xml",
        ),
        tag="hdlworker",
        treesitter=Treesitter(
            fragments_to_ignore=[
                "include $(OCPI_CDK_DIR)/include/worker.mk\n",
            ],
        ),
        variables=Variables(
            accepted=[
                "excludeplatforms",
                "excludetargets",
                "hdlexactpart",
                "hdlplatforms",
                "language",
                "libraries",
                "onlyplatforms",
                "onlytargets",
                "sourcefiles",
                "version",
            ],
            recommended={
                "language": (
                    "`language` defaults to 'verilog' if not defined, for "
                    "backwards compatibility with very early versions of "
                    "OpenCPI which didn't feature multiple languages. To avoid "
                    "accidentally creating a Verilog Worker, always define "
                    '`language="vhdl"`'
                ),
                "version": (
                    "`version` defaults to '1' if not defined, for backwards "
                    "compatibility with versions of OpenCPI before ~v1.4. To "
                    "avoid accidentally using the older data flow paradigm, "
                    'always define `version="2"`'
                ),
            },
            translations={"hdllibraries": "libraries"},
        ),
    ),
    "library": Asset(
        name="library",
        paths=Paths(),  # TODO: does this need to be filled in?
        tag="library",
        treesitter=Treesitter(
            fragments_to_ignore=[
                "include $(OCPI_CDK_DIR)/include/library.mk\n",
            ],
        ),
        variables=_LIBRARY_VARIABLES,
    ),
    "project": Asset(
        name="project",
        paths=Paths(
            makefiles=["Project.mk", "Makefile"],
            xml="Project.xml",
        ),
        tag="project",
        treesitter=Treesitter(
            fragments_to_ignore=[
                "include $(OCPI_CDK_DIR)/include/project.mk\n",
            ],
        ),
        variables=Variables(
            accepted=[
                "packageprefix",
                "packagename",
                "projectdependencies",
            ],
            not_recommended={
                "componentlibraries": (
                    "`componentlibraries` should be specified on the "
                    "particular asset that requires the library to be "
                    "imported, not on collections"
                ),
            },
            recommended={
                "packageprefix": (
                    "`packageprefix` defaults to 'local' if not defined. If "
                    "this is intended, explicitly assign it to 'local'"
                ),
                "packagename": (
                    "`packagename` defaults to the name of the directory this "
                    "file is in if not defined. It should always be defined to "
                    "avoid confusion"
                ),
            },
        ),
    ),
    "rcc-worker": Asset(
        name="rcc-worker",
        paths=Paths(
            makefiles=[
                "components/*.rcc/Makefile",
                "components/*/*.rcc/Makefile",
                "hdl/adapters/*.rcc/Makefile",
                "hdl/cards/*.rcc/Makefile",
                "hdl/devices/*.rcc/Makefile",
            ],
            xml=lambda file: file.parent / f"{file.parent.stem}.xml"
            if (file.parent / f"{file.parent.stem}.xml").exists()
            else file.parent / f"{file.parent.stem}-rcc.xml",
        ),
        tag="rccworker",
        treesitter=Treesitter(
            fragments_to_ignore=[
                "include $(OCPI_CDK_DIR)/include/worker.mk\n",
            ],
        ),
        variables=Variables(
            accepted=[
                "excludeplatforms",
                "excludetargets",
                "includedirs",
                "language",
                "libraries",
                "onlyplatforms",
                "onlytargets",
                "rccplatforms",
                "sourcefiles",
                "staticprereqlibs",
                "version",
            ],
            not_recommended={
                "slave": (
                    "`slave` as a top level attribute is the old syntax from "
                    "before v2.1; this should be changed in favour of using "
                    "`slaves` as a child element"
                ),
                "workers": (
                    "`workers` is used to define multiple workers in one "
                    "worker directory. This is bad practice; they should be "
                    "defined in individual directories"
                ),
            },
            recommended={
                "language": (
                    "`language` defaults to 'C' if not defined, for backwards "
                    "compatibility with very early versions of OpenCPI which "
                    "didn't feature multiple languages. To avoid accidentally "
                    'creating a C Worker, always define `language="c++"`'
                ),
                "version": (
                    "`version` defaults to '1' if not defined, for backwards "
                    "compatibility with versions of OpenCPI before ~v1.4. To "
                    "avoid accidentally using the older data flow paradigm, "
                    'always define `version="2"`'
                ),
            },
            translations={
                "rccincludedirs": "includedirs",
                "rccstaticprereqlibs": "staticprereqlibs",
            },
        ),
    ),
}
