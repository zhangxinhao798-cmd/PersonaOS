"""Deterministic expression package loader for PersonaOS."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from backend.models.expression_package import (
    ExpressionPackage,
    ExpressionPackageManifest,
    ExpressionPackageValidationResult,
    ExpressionStyle,
)


class ExpressionPackageError(Exception):
    """Raised when an expression package cannot be loaded."""


class ExpressionPackageLoader:
    """Loads file-backed expression packages without voice cloning or LLM calls."""

    MANIFEST_FILE = "manifest.json"

    def validate(
        self,
        package_path: str | Path,
    ) -> ExpressionPackageValidationResult:
        """Validate required expression package files and manifest fields."""

        root = Path(package_path)
        errors: list[str] = []
        warnings: list[str] = []

        if not root.exists():
            return ExpressionPackageValidationResult(
                is_valid=False,
                errors=[f"Expression package path does not exist: {root}"],
            )

        if not root.is_dir():
            return ExpressionPackageValidationResult(
                is_valid=False,
                errors=[f"Expression package path is not a directory: {root}"],
            )

        manifest_path = root / self.MANIFEST_FILE
        if not manifest_path.exists():
            return ExpressionPackageValidationResult(
                is_valid=False,
                errors=["Missing manifest.json"],
            )

        try:
            manifest = self._build_manifest(self._read_json(manifest_path))
        except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
            return ExpressionPackageValidationResult(
                is_valid=False,
                errors=[f"Invalid manifest.json: {exc}"],
            )

        for field_name in ("package_id", "name", "version"):
            if not getattr(manifest, field_name):
                errors.append(f"Manifest missing required field: {field_name}")

        style_path = root / manifest.style_path
        if not style_path.exists():
            errors.append(f"Missing style file: {manifest.style_path}")

        examples_path = root / manifest.examples_path
        if not examples_path.exists():
            warnings.append(f"Missing examples file: {manifest.examples_path}")

        return ExpressionPackageValidationResult(
            is_valid=not errors,
            errors=errors,
            warnings=warnings,
        )

    def load(self, package_path: str | Path) -> ExpressionPackage:
        """Load a valid expression package directory."""

        root = Path(package_path)
        validation = self.validate(root)
        if not validation.is_valid:
            raise ExpressionPackageError("; ".join(validation.errors))

        manifest = self._build_manifest(
            self._read_json(root / self.MANIFEST_FILE)
        )
        style = self._build_style(self._read_json(root / manifest.style_path))
        examples = self._read_optional_list(root / manifest.examples_path)

        return ExpressionPackage(
            manifest=manifest,
            style=style,
            examples=examples,
            package_path=str(root),
        )

    def _read_json(self, path: Path) -> Any:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def _read_optional_list(self, path: Path) -> list:
        if not path.exists():
            return []
        data = self._read_json(path)
        if not isinstance(data, list):
            raise ExpressionPackageError(f"Expected list in {path.name}")
        return data

    def _build_manifest(self, data: dict) -> ExpressionPackageManifest:
        if not isinstance(data, dict):
            raise TypeError("manifest must be a JSON object")
        return ExpressionPackageManifest(
            package_id=str(data.get("package_id", "")),
            name=str(data.get("name", "")),
            version=str(data.get("version", "")),
            description=str(data.get("description", "")),
            persona_id=str(data.get("persona_id", "")),
            style_path=str(data.get("style_path", "style.json")),
            examples_path=str(data.get("examples_path", "examples.json")),
            metadata=dict(data.get("metadata", {})),
        )

    def _build_style(self, data: dict) -> ExpressionStyle:
        if not isinstance(data, dict):
            raise ExpressionPackageError("style must be a JSON object")
        return ExpressionStyle(
            tone=str(data.get("tone", "")),
            rhythm=str(data.get("rhythm", "")),
            pacing=str(data.get("pacing", "")),
            vocabulary=list(data.get("vocabulary", [])),
            catchphrases=list(data.get("catchphrases", [])),
            sentence_patterns=list(data.get("sentence_patterns", [])),
            pause_patterns=list(data.get("pause_patterns", [])),
            emphasis_patterns=list(data.get("emphasis_patterns", [])),
            avoid=list(data.get("avoid", [])),
        )
