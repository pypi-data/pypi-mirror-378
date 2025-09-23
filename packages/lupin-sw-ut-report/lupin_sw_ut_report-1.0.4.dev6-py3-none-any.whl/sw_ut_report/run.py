import os
import sys
from os import PathLike
from typing import Dict, List, Optional

import typer

from sw_ut_report.__init__ import __version__
from sw_ut_report.parse_txt_file import format_txt_file
from sw_ut_report.parse_xml_file import format_xml_to_dict
from sw_ut_report.template_manager import get_local_template
# Jama imports will be loaded conditionally when needed

cli = typer.Typer()


def input_folder_option() -> typer.Option:
    return typer.Option(
        ...,
        "--input-folder",
        help="Path to the folder containing the txt and xml files",
    )


def version_callback(value: bool):
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@cli.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        None, "--version", callback=version_callback, is_eager=True
    ),
    input_folder: str = input_folder_option(),
    generate_markdown: bool = typer.Option(True, "--markdown", help="Generate markdown report"),
    no_markdown: bool = typer.Option(False, "--no-markdown", help="Do not generate markdown report"),
    create_jama_ut: bool = typer.Option(False, "--create-ut", help="Create/update unit tests in Jama"),
    module_name: Optional[str] = typer.Option(None, "--module-name", help="Module name for Jama UT creation (required with --create-ut)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be done without making changes to Jama"),
    push_ut_test_results: Optional[str] = typer.Option(None, "--push-ut-test-results", help="Push UT test results to Jama for the specified version"),
):
    # Vérification explicite de --version AVANT tout autre traitement
    # Ceci garantit que la version s'affiche même si le callback is_eager ne fonctionne pas dans certains environnements

    # Logs de débogage pour tracer les paramètres reçus
    typer.echo(f"DEBUG: version = {version}", err=True)
    typer.echo(f"DEBUG: input_folder = {input_folder}", err=True)
    typer.echo(f"DEBUG: generate_markdown = {generate_markdown}", err=True)
    typer.echo(f"DEBUG: no_markdown = {no_markdown}", err=True)
    typer.echo(f"DEBUG: create_jama_ut = {create_jama_ut}", err=True)
    typer.echo(f"DEBUG: module_name = {module_name}", err=True)
    typer.echo(f"DEBUG: dry_run = {dry_run}", err=True)
    typer.echo(f"DEBUG: push_ut_test_results = {push_ut_test_results}", err=True)
    typer.echo(f"DEBUG: ctx.invoked_subcommand = {ctx.invoked_subcommand}", err=True)

    if version is True:
        typer.echo(__version__)
        sys.exit(0)

    if ctx.invoked_subcommand is None:
        # Si input_folder est None, ne pas traiter la génération de rapports
        if input_folder is None:
            typer.echo("Error: --input-folder is required for report generation", err=True)
            raise typer.Exit(code=1)

        # Handle markdown generation logic
        if no_markdown:
            generate_markdown = False

        generate_report(input_folder, generate_markdown, create_jama_ut, module_name, dry_run, push_ut_test_results)


@cli.command()
def generate_report(
    input_folder: str = input_folder_option(),
    generate_markdown: bool = typer.Option(True, "--markdown", help="Generate markdown report"),
    no_markdown: bool = typer.Option(False, "--no-markdown", help="Do not generate markdown report"),
    create_jama_ut: bool = typer.Option(False, "--create-ut", help="Create/update unit tests in Jama"),
    module_name: Optional[str] = typer.Option(None, "--module-name", help="Module name for Jama UT creation (required with --create-ut)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be done without making changes to Jama"),
    push_ut_test_results: Optional[str] = typer.Option(None, "--push-ut-test-results", help="Push UT test results to Jama for the specified version"),
):
    # Validate parameters
    if input_folder is None:
        typer.echo("Error: --input-folder is required for report generation", err=True)
        raise typer.Exit(code=1)

    # Handle markdown generation logic
    if no_markdown:
        generate_markdown = False

    if create_jama_ut and not module_name:
        typer.echo("Error: --module-name is required when --create-ut is used", err=True)
        raise typer.Exit(code=1)

    if push_ut_test_results and not input_folder:
        typer.echo("Error: --input-folder is required when --push-ut-test-results is used", err=True)
        raise typer.Exit(code=1)

    if not generate_markdown and not create_jama_ut and not push_ut_test_results:
        typer.echo("Error: At least one output option must be specified (--markdown, --create-ut, or --push-ut-test-results)", err=True)
        raise typer.Exit(code=1)

    # Dry-run validation
    if dry_run and not create_jama_ut:
        typer.echo("Note: --dry-run only applies to Jama operations. Use with --create-ut to see Jama actions.")

    # Handle push UT test results first
    if push_ut_test_results:
        typer.echo(f"Pushing UT test results to Jama for version: {push_ut_test_results}")

        try:
            # Load Jama modules only when needed
            from sw_ut_report.jama_common import setup_logging, JamaConnectionError, JamaValidationError
            from sw_ut_report.push_ut_test_results import push_ut_test_results_to_jama
            setup_logging()

            ut_result = push_ut_test_results_to_jama(push_ut_test_results, input_folder)

            if ut_result == 0:
                typer.echo("✅ Successfully pushed UT test results to Jama")
                typer.echo(f"Exit code: {ut_result}")
                raise typer.Exit(code=0)
            elif ut_result == 1:
                typer.echo("❌ Failed to push UT test results to Jama", err=True)
                typer.echo(f"Exit code: {ut_result}")
                raise typer.Exit(code=1)
            elif ut_result == 2:
                typer.echo("⚠️ Pushed UT test results to Jama with warnings")
                typer.echo(f"Exit code: {ut_result}")
                raise typer.Exit(code=2)
            else:
                typer.echo("❌ Failed to push UT test results to Jama", err=True)
                typer.echo(f"Exit code: 1 (unknown result: {ut_result})")
                raise typer.Exit(code=1)

        except (JamaConnectionError, JamaValidationError) as e:
            typer.echo(f"❌ Jama operation failed: {e}", err=True)
            typer.echo("Exit code: 1")
            raise typer.Exit(code=1)
        except typer.Exit:
            # Re-raise typer.Exit to preserve the original exit code
            raise
        except Exception as e:
            typer.echo(f"❌ Error pushing UT test results: {e}", err=True)
            typer.echo("Exit code: 1")
            raise typer.Exit(code=1)
        return

    typer.echo("test reports generation started")

    all_reports = []

    try:
        file_list = os.listdir(input_folder)
    except FileNotFoundError:
        typer.echo(f"Path '{input_folder}' does not exist.")
        raise typer.Exit(code=1)
    except PermissionError:
        typer.echo(f"Permission denied for the folder '{input_folder}'.")
        raise typer.Exit(code=1)

    for filename in file_list:
        input_file = os.path.join(input_folder, filename)
        _, file_extension = os.path.splitext(filename)

        match file_extension.lower():
            case ".txt":
                scenarios = format_txt_file(read_file_content(input_file))
                for scenario in scenarios:
                    scenario["filename"] = filename
                all_reports.append(
                    {"type": "txt", "filename": filename, "content": scenarios}
                )

            case ".xml":
                suites_data = format_xml_to_dict(input_file)
                suites_data["filename"] = filename
                all_reports.append(
                    {"type": "xml", "filename": filename, "content": suites_data}
                )

            case _:
                if os.path.isdir(input_file):
                    typer.echo(f"Skipping folder: {filename}")
                    continue
                else:
                    print(f"Skipping unsupported file format: {filename}")
                    continue

    if not all_reports:
        typer.echo("No test files found to process.")
        return

    # Execute requested operations
    exit_code = 0  # Default success code

    # Create UTs in Jama if requested
    if create_jama_ut:
        try:
            # Load Jama modules only when needed
            from sw_ut_report.jama_common import JamaConnectionError, JamaValidationError, setup_logging
            setup_logging()

            if dry_run:
                from sw_ut_report.jama_ut_manager import dry_run_unit_tests_creation

                typer.echo(f"DRY-RUN: Analyzing what would be done for module: {module_name}")
                typer.echo("=" * 60)

                ut_result = dry_run_unit_tests_creation(module_name, all_reports)

                if ut_result == 0:
                    typer.echo("✅ Dry-run analysis completed successfully")
                    exit_code = 0
                elif ut_result == 1:
                    typer.echo("❌ Dry-run analysis found errors", err=True)
                    exit_code = 1
                elif ut_result == 2:
                    typer.echo("⚠️ Dry-run analysis completed with warnings")
                    exit_code = 2
                else:
                    typer.echo("❌ Dry-run analysis failed", err=True)
                    exit_code = 1

            else:
                from sw_ut_report.jama_ut_manager import create_unit_tests_in_jama

                typer.echo(f"Creating/updating unit tests in Jama for module: {module_name}")
                typer.echo("=" * 60)

                ut_result = create_unit_tests_in_jama(module_name, all_reports)

                if ut_result == 0:
                    typer.echo("✅ Successfully created/updated unit tests in Jama")
                    exit_code = 0
                elif ut_result == 1:
                    typer.echo("❌ Failed to create/update unit tests in Jama", err=True)
                    exit_code = 1
                elif ut_result == 2:
                    typer.echo("⚠️ Created/updated unit tests in Jama with warnings")
                    exit_code = 2
                else:
                    typer.echo("❌ Failed to create/update unit tests in Jama", err=True)
                    exit_code = 1

        except (JamaConnectionError, JamaValidationError) as e:
            typer.echo(f"❌ Jama operation failed: {e}", err=True)
            exit_code = 1
        except typer.Exit:
            # Re-raise typer.Exit to preserve the original exit code
            raise
        except Exception as e:
            typer.echo(f"❌ Unexpected error during Jama operations: {e}", err=True)
            exit_code = 1

        # Exit with the appropriate code for Jama operations
        typer.echo(f"Exit code: {exit_code}")
        raise typer.Exit(code=exit_code)

    # Generate markdown report if requested
    if generate_markdown:
        try:
            generate_single_markdown(all_reports)
            typer.echo("✅ Successfully generated markdown report")
            # Keep exit_code as 0 for success
        except Exception as e:
            typer.echo(f"❌ Failed to generate markdown report: {e}", err=True)
            exit_code = 1

    # Final exit with the determined code
    typer.echo(f"Final exit code: {exit_code}")
    raise typer.Exit(code=exit_code)


def read_file_content(input_file: PathLike) -> str:
    with open(input_file, "r", encoding="utf-8") as f:
        return f.read()


def generate_single_markdown(all_reports: List[Dict]) -> None:
    template = get_local_template("combined_test_report.j2")
    markdown_content = template.render(reports=all_reports)

    with open("sw_ut_report.md", "w", encoding="utf-8") as md_file:
        md_file.write(markdown_content)
