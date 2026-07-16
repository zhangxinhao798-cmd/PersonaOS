"""Deterministic persona package loader for PersonaOS."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from backend.models.persona_library import PersonaLibraryEntry
from backend.models.persona_package import (
    PersonaPackage,
    PersonaPackageManifest,
    PersonaPackageValidationResult,
)
from backend.models.persona_profile import PersonaProfile
from backend.models.persona_source import PersonaSource
from backend.models.persona_version import PersonaVersion


class PersonaPackageError(Exception):
    """Raised when a persona package cannot be loaded."""


class PersonaPackageLoader:
    """Loads file-backed persona packages without activating them.

    The loader owns deterministic package parsing only. It does not review,
    approve, activate, persist, or call model providers.
    """

    MANIFEST_FILE = "manifest.json"

    def validate(self, package_path: str | Path) -> PersonaPackageValidationResult:
        """Validate required package files and basic manifest fields."""

        root = Path(package_path)
        errors: list[str] = []
        warnings: list[str] = []

        if not root.exists():
            return PersonaPackageValidationResult(
                is_valid=False,
                errors=[f"Package path does not exist: {root}"],
            )

        if not root.is_dir():
            return PersonaPackageValidationResult(
                is_valid=False,
                errors=[f"Package path is not a directory: {root}"],
            )

        manifest_path = root / self.MANIFEST_FILE
        if not manifest_path.exists():
            return PersonaPackageValidationResult(
                is_valid=False,
                errors=["Missing manifest.json"],
            )

        try:
            manifest_data = self._read_json(manifest_path)
            manifest = self._build_manifest(manifest_data)
        except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
            return PersonaPackageValidationResult(
                is_valid=False,
                errors=[f"Invalid manifest.json: {exc}"],
            )

        for field_name in ("package_id", "name", "version"):
            if not getattr(manifest, field_name):
                errors.append(f"Manifest missing required field: {field_name}")

        profile_path = root / manifest.profile_path
        if not profile_path.exists():
            errors.append(f"Missing profile file: {manifest.profile_path}")

        examples_path = root / manifest.examples_path
        if not examples_path.exists():
            warnings.append(f"Missing examples file: {manifest.examples_path}")

        sources_path = root / manifest.sources_path
        if not sources_path.exists():
            warnings.append(f"Missing sources file: {manifest.sources_path}")

        knowledge_path = root / manifest.knowledge_path
        if not knowledge_path.exists():
            warnings.append(f"Missing knowledge file: {manifest.knowledge_path}")

        return PersonaPackageValidationResult(
            is_valid=not errors,
            errors=errors,
            warnings=warnings,
        )

    def load(self, package_path: str | Path) -> PersonaPackage:
        """Load a valid package directory into a PersonaPackage."""

        root = Path(package_path)
        validation = self.validate(root)
        if not validation.is_valid:
            raise PersonaPackageError("; ".join(validation.errors))

        manifest = self._build_manifest(
            self._read_json(root / self.MANIFEST_FILE)
        )
        profile = self._build_profile(
            self._read_json(root / manifest.profile_path)
        )
        examples = self._read_optional_list(root / manifest.examples_path)
        sources = [
            self._build_source(source_data)
            for source_data in self._read_optional_list(
                root / manifest.sources_path
            )
        ]
        knowledge = self._read_optional_dict(root / manifest.knowledge_path)

        return PersonaPackage(
            manifest=manifest,
            profile=profile,
            examples=examples,
            sources=sources,
            knowledge=knowledge,
            package_path=str(root),
        )

    def to_library_entry(
        self,
        package: PersonaPackage,
        created_at: str = "",
        change_note: str = "Initial persona package import.",
    ) -> PersonaLibraryEntry:
        """Convert a loaded package into a draft library entry."""

        if package.profile is None:
            raise PersonaPackageError("Persona package has no profile.")

        manifest = package.manifest
        source_ids = [source.id for source in package.sources if source.id]
        version_id = f"{manifest.package_id}:{manifest.version}"
        version = PersonaVersion(
            id=version_id,
            persona_name=package.profile.name,
            version=manifest.version,
            created_at=created_at,
            profile_snapshot=self._profile_snapshot(package.profile),
            source_ids=source_ids,
            change_note=change_note,
        )

        return PersonaLibraryEntry(
            id=manifest.package_id,
            name=manifest.name,
            description=manifest.description,
            current_version_id=version_id,
            profile=package.profile,
            versions=[version],
            source_ids=source_ids,
        )

    def _read_json(self, path: Path) -> Any:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def _read_optional_list(self, path: Path) -> list:
        if not path.exists():
            return []
        data = self._read_json(path)
        if not isinstance(data, list):
            raise PersonaPackageError(f"Expected list in {path.name}")
        return data

    def _read_optional_dict(self, path: Path) -> dict:
        if not path.exists():
            return {}
        data = self._read_json(path)
        if not isinstance(data, dict):
            raise PersonaPackageError(f"Expected object in {path.name}")
        return data

    def _build_manifest(self, data: dict) -> PersonaPackageManifest:
        if not isinstance(data, dict):
            raise TypeError("manifest must be a JSON object")
        return PersonaPackageManifest(
            package_id=str(data.get("package_id", "")),
            name=str(data.get("name", "")),
            version=str(data.get("version", "")),
            description=str(data.get("description", "")),
            profile_path=str(data.get("profile_path", "profile.json")),
            examples_path=str(data.get("examples_path", "examples.json")),
            sources_path=str(data.get("sources_path", "sources.json")),
            knowledge_path=str(data.get("knowledge_path", "knowledge.json")),
            metadata=dict(data.get("metadata", {})),
        )

    def _build_profile(self, data: dict) -> PersonaProfile:
        if not isinstance(data, dict):
            raise PersonaPackageError("profile must be a JSON object")
        return PersonaProfile(
            name=str(data.get("name", "")),
            traits=dict(data.get("traits", {})),
            values=list(data.get("values", [])),
            style=str(data.get("style", "")),
            boundaries=list(data.get("boundaries", [])),
            thinking_patterns=list(data.get("thinking_patterns", [])),
            communication_style=list(data.get("communication_style", [])),
            speech_patterns=list(data.get("speech_patterns", [])),
            examples=list(data.get("examples", [])),
        )

    def _build_source(self, data: dict) -> PersonaSource:
        if not isinstance(data, dict):
            raise PersonaPackageError("source entries must be JSON objects")
        return PersonaSource(
            id=str(data.get("id", "")),
            name=str(data.get("name", "")),
            source_type=str(data.get("source_type", "")),
            content=str(data.get("content", "")),
            metadata=dict(data.get("metadata", {})),
        )

    def _profile_snapshot(self, profile: PersonaProfile) -> dict:
        return {
            "name": profile.name,
            "traits": dict(profile.traits),
            "values": list(profile.values),
            "style": profile.style,
            "boundaries": list(profile.boundaries),
            "thinking_patterns": list(profile.thinking_patterns),
            "communication_style": list(profile.communication_style),
            "speech_patterns": list(profile.speech_patterns),
            "examples": list(profile.examples),
        }

