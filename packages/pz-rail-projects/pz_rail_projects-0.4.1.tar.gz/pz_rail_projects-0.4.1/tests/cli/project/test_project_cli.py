import os

import pytest
from click.testing import CliRunner, Result

from rail.cli.rail_project.project_commands import project_cli


def check_result(
    result: Result,
) -> None:
    if not result.exit_code == 0:
        raise ValueError(f"{result} failed with {result.exit_code} {result.output}")


def test_cli_help() -> None:
    runner = CliRunner()

    result = runner.invoke(project_cli, "--help")
    check_result(result)


def test_cli_inspect() -> None:
    runner = CliRunner()

    result = runner.invoke(project_cli, "inspect tests/ci_project.yaml")
    check_result(result)


def test_cli_build() -> None:
    runner = CliRunner()

    os.system("\\rm -rf tests/temp_data/projects/ci_test/pipelines")
    os.system("\\rm -rf tests/temp_data/projects/ci_test/logs")

    result = runner.invoke(project_cli, "build --flavor all tests/ci_project.yaml")
    check_result(result)


def test_cli_reduce() -> None:
    runner = CliRunner()

    result = runner.invoke(
        project_cli,
        "reduce "
        "--catalog-template truth "
        "--output-catalog-template reduced "
        "--reducer-class-name roman_rubin "
        "--selection gold "
        "tests/ci_project.yaml",
    )
    check_result(result)


def test_cli_subsample() -> None:
    runner = CliRunner()

    result = runner.invoke(
        project_cli,
        "subsample "
        "--catalog-template degraded "
        "--flavor baseline "
        "--file-template test_file_100k "
        "--subsampler-class-name random_subsampler "
        "--subsample-name test_100k "
        "--run-mode dry_run "
        "--selection gold "
        "--basename output.hdf5 "
        "tests/ci_project.yaml",
    )
    check_result(result)


@pytest.mark.parametrize(
    "pipeline",
    [
        "blending",
        "estimate",
        "evaluate",
        "inform",
        "phot-errors",
        "prepare",
        "pz",
        "inform-sompz",
        "estimate-sompz",
        "inform-recalib",
        "estimate-recalib",
        "inform-somlike",
        "somlike-recalib",
        "spec-selection",
        "tomography",
        "truth-to-observed",
    ],
)
def test_cli_run(pipeline: str) -> None:
    runner = CliRunner()

    if pipeline == "estimate":
        label_str = "--input-tag test "
    else:
        label_str = ""

    result = runner.invoke(
        project_cli,
        f"run {pipeline} --selection gold --flavor baseline {label_str}--run-mode dry_run tests/ci_project.yaml",
    )
    check_result(result)


def test_cli_wrap_model(setup_project_area: int) -> None:
    assert setup_project_area == 0
    runner = CliRunner()

    result = runner.invoke(
        project_cli,
        "wrap-pz-models "
        "--outdir tests/temp_data "
        "--flavor baseline "
        "--selection blend "
        "tests/ci_project.yaml",
    )
    check_result(result)
