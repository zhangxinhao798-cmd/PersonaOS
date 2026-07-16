"""Tests for Expression Package v1 boundaries."""

import json
from pathlib import Path

import pytest

from backend.core import ExpressionPackageError, ExpressionPackageLoader
from backend.models import (
    ExpressionPackage,
    ExpressionPackageManifest,
    ExpressionPackageValidationResult,
    ExpressionStyle,
)


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def create_expression_package(root: Path) -> None:
    write_json(
        root / "manifest.json",
        {
            "package_id": "test-expression",
            "name": "Test Expression",
            "version": "1.0.0",
            "description": "Test expression style.",
            "persona_id": "test-persona",
            "metadata": {"modality": "text-expression"},
        },
    )
    write_json(
        root / "style.json",
        {
            "tone": "calm",
            "rhythm": "short then clear",
            "pacing": "measured",
            "vocabulary": ["boundary"],
            "catchphrases": ["Let's preserve the boundary first."],
            "sentence_patterns": ["First name the boundary."],
            "pause_patterns": ["pause before the next step"],
            "emphasis_patterns": ["emphasize ownership"],
            "avoid": ["voice cloning claims"],
        },
    )
    write_json(
        root / "examples.json",
        [
            {
                "input": "How should this sound?",
                "output": "Calm, clear, and boundary-first.",
            }
        ],
    )


def test_expression_package_models_initialize_with_independent_defaults() -> None:
    package_a = ExpressionPackage()
    package_b = ExpressionPackage()
    package_a.examples.append({"input": "hello"})

    assert isinstance(package_a.manifest, ExpressionPackageManifest)
    assert isinstance(package_a.style, ExpressionStyle)
    assert isinstance(
        ExpressionPackageValidationResult(), ExpressionPackageValidationResult
    )
    assert package_a.examples == [{"input": "hello"}]
    assert package_b.examples == []


def test_expression_loader_validates_missing_manifest(tmp_path: Path) -> None:
    result = ExpressionPackageLoader().validate(tmp_path)

    assert result.is_valid is False
    assert result.errors == ["Missing manifest.json"]


def test_expression_loader_validates_required_manifest_fields(
    tmp_path: Path,
) -> None:
    write_json(tmp_path / "manifest.json", {"name": "Test Expression"})

    result = ExpressionPackageLoader().validate(tmp_path)

    assert result.is_valid is False
    assert "Manifest missing required field: package_id" in result.errors
    assert "Manifest missing required field: version" in result.errors
    assert "Missing style file: style.json" in result.errors


def test_expression_loader_loads_complete_package(tmp_path: Path) -> None:
    create_expression_package(tmp_path)

    package = ExpressionPackageLoader().load(tmp_path)

    assert package.manifest.package_id == "test-expression"
    assert package.manifest.persona_id == "test-persona"
    assert package.manifest.metadata == {"modality": "text-expression"}
    assert package.style.tone == "calm"
    assert package.style.catchphrases == [
        "Let's preserve the boundary first."
    ]
    assert package.style.pause_patterns == ["pause before the next step"]
    assert package.examples == [
        {
            "input": "How should this sound?",
            "output": "Calm, clear, and boundary-first.",
        }
    ]
    assert package.package_path == str(tmp_path)


def test_expression_loader_optional_examples_default_to_empty(
    tmp_path: Path,
) -> None:
    create_expression_package(tmp_path)
    (tmp_path / "examples.json").unlink()

    validation = ExpressionPackageLoader().validate(tmp_path)
    package = ExpressionPackageLoader().load(tmp_path)

    assert validation.is_valid is True
    assert validation.warnings == ["Missing examples file: examples.json"]
    assert package.examples == []


def test_expression_loader_rejects_invalid_examples_shape(
    tmp_path: Path,
) -> None:
    create_expression_package(tmp_path)
    write_json(tmp_path / "examples.json", {"not": "a list"})

    with pytest.raises(ExpressionPackageError):
        ExpressionPackageLoader().load(tmp_path)


def test_expression_loader_rejects_missing_style_file(tmp_path: Path) -> None:
    create_expression_package(tmp_path)
    (tmp_path / "style.json").unlink()

    with pytest.raises(ExpressionPackageError):
        ExpressionPackageLoader().load(tmp_path)
