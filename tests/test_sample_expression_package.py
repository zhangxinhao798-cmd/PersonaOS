"""Tests for sample PersonaOS expression packages."""

from pathlib import Path

from backend.core import ExpressionPackageLoader


ARCHITECT_EXPRESSION_PATH = Path("expressions") / "architect"
STRATEGIST_EXPRESSION_PATH = Path("expressions") / "strategist"


def test_sample_expression_package_files_exist() -> None:
    for package_path in (ARCHITECT_EXPRESSION_PATH, STRATEGIST_EXPRESSION_PATH):
        assert package_path.is_dir()
        assert (package_path / "manifest.json").is_file()
        assert (package_path / "style.json").is_file()
        assert (package_path / "examples.json").is_file()


def test_sample_expression_packages_validate() -> None:
    loader = ExpressionPackageLoader()

    for package_path in (ARCHITECT_EXPRESSION_PATH, STRATEGIST_EXPRESSION_PATH):
        result = loader.validate(package_path)
        assert result.is_valid is True
        assert result.errors == []


def test_architect_expression_package_loads() -> None:
    package = ExpressionPackageLoader().load(ARCHITECT_EXPRESSION_PATH)

    assert package.manifest.package_id == "architect-expression"
    assert package.manifest.persona_id == "architect"
    assert package.style.tone == "calm, precise, and structured"
    assert "Let's preserve the boundary first." in package.style.catchphrases
    assert "voice or avatar claims" in package.style.avoid
    assert package.examples


def test_strategist_expression_package_loads() -> None:
    package = ExpressionPackageLoader().load(STRATEGIST_EXPRESSION_PATH)

    assert package.manifest.package_id == "strategist-expression"
    assert package.manifest.persona_id == "strategist"
    assert package.style.tone == "practical, comparative, and direct"
    assert "Let's frame the decision first." in package.style.catchphrases
    assert "automatic decisions for the user" in package.style.avoid
    assert package.examples


def test_expression_packages_do_not_claim_voice_cloning() -> None:
    loader = ExpressionPackageLoader()

    for package_path in (ARCHITECT_EXPRESSION_PATH, STRATEGIST_EXPRESSION_PATH):
        package = loader.load(package_path)
        serialized = " ".join(
            [
                package.manifest.description,
                package.style.tone,
                package.style.rhythm,
                package.style.pacing,
                " ".join(package.style.catchphrases),
                " ".join(package.style.avoid),
            ]
        ).lower()

        assert "voice clone" not in serialized
        assert "voice cloning" not in serialized
        assert "voice or avatar claims" in package.style.avoid or (
            "automatic decisions for the user" in package.style.avoid
        )
