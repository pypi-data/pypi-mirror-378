# -*- coding: utf-8 -*-
"""Command line interface for the Gene Dictionary Tool (gdt).

This module provides a command line interface with 3 commands:
- `filter`: Filter GFF3 files based on a TSV file.
- `stripped`: Create a stripped version of a GDICT file.
- `standardize`: Standardize gene names in GFF3 files using a GDICT file.

All commands support global flags for debugging, logging, and quiet mode.
The CLI is designed to be user-friendly and provides detailed logging for
each operation.

"""

import argparse
import os
from pathlib import Path

from . import __version__, gdict, gff3_utils, log_setup

C_RESET: str = "\033[0m"

GDT_BANNER: str = f"""           ╔═════════════════════════════╗
           ║   ██████╗ ██████╗ ████████╗ ║
           ║  ██╔════╝ ██╔══██╗╚══██╔══╝ ║
           ║  ██║  ███╗██║  ██║   ██║    ║
           ║  ██║   ██║██║  ██║   ██║    ║
           ║  ╚██████╔╝██████╔╝   ██║    ║
           ║   ╚═════╝ ╚═════╝    ╚═╝    ║
           ║    \033[34mGene Dictionary Tool{C_RESET}     ║
           ╚═════════════════════════════╝
🧬 \033[33mStandardizing gene names across organelle genomes{C_RESET} 🧬
                   Version: \033[32m{__version__}{C_RESET}"""

MAX_CPU: int = os.cpu_count() or 1


def _workers_count(workers: int, threading: bool = False) -> int:
    """Return the number of workers to use."""
    cpus = MAX_CPU * 3 if threading else MAX_CPU
    return min(workers, cpus) if workers > 0 else cpus


def filter_command(
    args: argparse.Namespace,
    log: log_setup.GDTLogger,
) -> None:
    """Command to filter GFF3 files based on a TSV file."""
    args.tsv = Path(args.tsv).resolve()

    if args.gdict:
        args.gdict = Path(args.gdict).resolve()

    log.debug(
        f"filter command: tsv: {args.tsv} | gdict: {args.gdict} | "
        f"keep_orfs: {args.keep_orfs} | workers: {args.workers} | "
        f"AN_column: {args.AN_column} | gff_ext: {args.gff_ext} | "
        f"gff_suffix: {args.gff_suffix} | query_string: {args.query_string}"
    )
    gff3_utils.filter_whole_tsv(
        log,
        args.tsv,
        args.gdict,
        args.keep_orfs,
        _workers_count(args.workers),
        args.AN_column,
        args.gff_ext,
        args.gff_suffix,
        args.in_folder,
        args.query_string,
        args.check,
    )


def _parse_data(
    log: log_setup.GDTLogger,
    label: str,
    label_data: list[str],
    ncbi_descs: set[str],
) -> tuple[str, list[str]]:
    """Parse label data and return a tuple of label and its data."""
    log.trace(
        f"Parsing label: {label} with data: {label_data} and ncbi_descs: {ncbi_descs}"
    )
    if label:
        if "#gd gff_gene" in label_data[0]:
            return (
                label,
                label_data + [f"{desc} #gd NCBI" for desc in sorted(ncbi_descs)],
            )

    return (label, label_data)


def _stripped_large_temp(
    log: log_setup.GDTLogger,
    gdict_in: Path,
    gdict_out: Path,
) -> None:
    """Create a stripped version of a large TEMP GDICT file."""
    log.debug(f"Stripping large TEMP GDICT: {gdict_in.name} to {gdict_out.name}")
    headers = []
    with open(gdict_in, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#"):
                headers.append(line.strip())
            else:
                break

        label: str
        data: list[tuple[str, list[str]]] = []
        label_data: list[str] = []
        ncbi_descs: set[str] = set()

        # parse possible first label
        if line.strip() and line.startswith("[") and line.endswith("]\n"):
            label = line[1:-1].strip()

        # parse rest of the file
        for line in f:
            if not (line := line.strip()):
                continue

            if line.startswith("[") and line.endswith("]"):
                data.append(_parse_data(log, label, label_data, ncbi_descs))

                label = line[1:-1].strip()
                label_data = []
                ncbi_descs = set()
                continue

            if "#gd" in line and label:
                label_data.append(line)
                continue

            if "#dx" in line and label:
                ncbi_desc = line.split("ncbi_desc:")[1].strip()
                ncbi_descs.add(ncbi_desc)
                continue

        # append last entry
        data.append(_parse_data(log, label, label_data, ncbi_descs))

        with open(gdict_out, "w", encoding="utf-8") as out:
            for header in headers:
                out.write(f"{header}\n")

            for entry in data:
                if entry:
                    out.write(f"\n[{entry[0]}]\n")
                    for ld in entry[1]:
                        out.write(f"{ld}\n")


def stripped_command(
    args: argparse.Namespace,
    log: log_setup.GDTLogger,
) -> None:
    """Command to create a stripped version of a GDT file."""
    log.info(
        f"stripped command: gdict_in: {args.gdict_in} | "
        f"gdict_out: {args.gdict_out} | "
        f"overwrite: {args.overwrite}"
    )
    args.gdict_in = Path(args.gdict_in).resolve()
    args.gdict_out = Path(args.gdict_out).resolve()

    if not args.gdict_in.exists():
        log.error(f"gdict not found: {args.gdict_in}")
        raise FileNotFoundError(f"GDICT file not found: {args.gdict_in}")

    if args.gdict_out.exists() and not args.overwrite:
        log.error(
            f"gdict already exists, overwrite: {args.overwrite} | "
            f"gdict: {args.gdict_out}"
        )
        raise FileExistsError(
            f"GDICT file already exists: {args.gdict_out}. "
            f"Use overwrite=True to overwrite."
        )

    if args.large_temp:
        _stripped_large_temp(log, args.gdict_in, args.gdict_out)
        log.info(f"Stripped large TEMP GDICT created: {args.gdict_out}")
        return

    gene_dict = gdict.read_gdict(args.gdict_in)
    log.info("Info before stripping:")
    log_setup.log_info(log, gene_dict)

    stripped = gene_dict.create_stripped(keep_gn=args.keep_gn)
    stripped.update_info()

    log.info("\nNew Header:")
    for txt in stripped.header:
        log.info(txt)

    log.info("New Info:")
    log_setup.log_info(log, stripped)
    stripped.to_gdict(args.gdict_out, overwrite=args.overwrite)


def standardize_command(
    args: argparse.Namespace,
    log: log_setup.GDTLogger,
) -> None:
    """Command to standardize gene names in GFF3 files using a GDT file."""
    log.info(
        f"standardize command: gff: {args.gff} | tsv: {args.tsv} | "
        f"gdict: {args.gdict} | AN_column: {args.AN_column} | "
        f"gff_ext: {args.gff_ext} | gff_suffix: {args.suffix} | "
        f"query_string: {args.query_string} | check: {args.check} | "
        f"second_place: {args.second_place} | gdt_tag: {args.gdt_tag} | "
        f"error_on_missing: {args.error_on_missing} | save_copy: {args.save_copy}"
    )
    args.gdict = Path(args.gdict).resolve()
    if args.gff:
        args.gff = Path(args.gff).resolve()

        if not args.gff.is_file():
            log.error(f"gff file not found: {args.gff}")

        if not args.gdict.exists():
            log.error(f"gdt file not found: {args.gdict}")
            raise FileNotFoundError(f"gdt file not found: {args.gdict}")

        gene_dict = gdict.read_gdict(args.gdict)
        log.debug(f"Gene dictionary loaded from {args.gdict}")

        gff3_utils.standardize_gff3(
            log,
            args.gff,
            gene_dict,
            args.query_string,
            args.check,
            args.second_place,
            args.gdt_tag,
            args.error_on_missing,
            args.save_copy,
            True,
        )

    elif args.tsv:
        args.tsv = Path(args.tsv).resolve()
        gff3_utils.standardize_tsv(
            log,
            args.tsv,
            args.gdict,
            args.AN_column,
            args.gff_ext,
            args.gff_suffix,
            args.in_folder,
            args.query_string,
            args.check,
            args.second_place,
            args.gdt_tag,
            args.error_on_missing,
            args.save_copy,
        )


def cli_run() -> None:
    """Command line interface for the Gene Dictionary Tool (gdt)."""
    # Global parser to add debug, log, and quiet flags to all subcommands
    global_flags = argparse.ArgumentParser(add_help=False)
    global_flags.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity level. Use multiple times for more verbose output: "
        "-v (INFO console, TRACE file), -vv (DEBUG console, TRACE file), "
        "-vvv (TRACE console, TRACE file). Default: INFO console + DEBUG file.",
    )
    global_flags.add_argument(
        "--log",
        required=False,
        type=str,
        metavar="PATH",
        default=None,
        help="Path to the log file. If not provided, a default log file will be "
        "created.",
    )
    global_flags.add_argument(
        "--no-log-file",
        required=False,
        action="store_true",
        default=False,
        help="Disable file logging.",
    )

    global_flags.add_argument(
        "--quiet",
        required=False,
        action="store_true",
        default=False,
        help="Suppress console output.",
    )

    main_parser = argparse.ArgumentParser(
        description=GDT_BANNER,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[global_flags],
        epilog=f"Source ~ \033[32mhttps://github.com/brenodupin/gdt{C_RESET}",
    )
    main_parser.add_argument(
        "--version",
        action="version",
        version=f"gdt {__version__}",
        help="Show the version of the gdt package.",
    )

    subparsers = main_parser.add_subparsers(
        dest="command",
        required=True,
    )

    filter_parser = subparsers.add_parser(
        "filter",
        help="Filter GFF3 files indexed through TSV file.",
        description="Filter GFF3 files that are indexed via TSV file, "
        "creating AN_missing_dbxref.txt and/or AN_missing_gene_dict.txt "
        "based on the provided GDT file.",
        parents=[global_flags],
    )
    filter_parser.add_argument(
        "--tsv",
        required=True,
        type=str,
        metavar="PATH",
        help="TSV file with indexed GFF3 files to filter.",
    )
    filter_parser.add_argument(
        "--AN-column",
        required=False,
        default="AN",
        type=str,
        metavar="STR",
        help="Column name for NCBI Accession Number inside the TSV. Default: AN",
    )
    filter_parser.add_argument(
        "--gdict",
        required=False,
        default=False,
        type=str,
        metavar="PATH",
        help="GDICT file to use for filtering. "
        "If not provided, an empty GeneDict (i.e GDICT file) will be used.",
    )
    filter_parser.add_argument(
        "--keep-orfs",
        required=False,
        default=False,
        action="store_true",
        help="Keep ORFs. Default: exclude ORFs",
    )
    filter_parser.add_argument(
        "--workers",
        required=False,
        default=0,
        type=int,
        metavar="INT",
        help="Number of workers to use. "
        f"Default: 0 (use all available cores: {os.cpu_count()})",
    )
    filter_parser.add_argument(
        "--gff-ext",
        required=False,
        default=".gff3",
        type=str,
        metavar="STR",
        help="File Extension for GFF files. Default: '.gff3'",
    )
    filter_parser.add_argument(
        "--gff-suffix",
        required=False,
        default="",
        type=str,
        metavar="STR",
        help="Suffix to be added when building GFF Paths from the TSV file. "
        "Example: '_clean' will create GFF paths like '<AN>_clean.gff3' if "
        "--gff-ext is '.gff3'. ",
    )
    filter_parser.add_argument(
        "--in-folder",
        required=False,
        default=False,
        action="store_true",
        help="Expect GFF3 files to be stored in subfolders named after the accession"
        "number, e.g., 'AN1234567/AN1234567.gff3'. Default: False"
        "(expect GFF files to be in the same folder as the TSV file).",
    )
    filter_parser.add_argument(
        "--query-string",
        required=False,
        default=gff3_utils.QS_GENE_TRNA_RRNA,
        type=str,
        metavar="STR",
        help="Query string that pandas filter features in GFF. "
        f"Default: '{gff3_utils.QS_GENE_TRNA_RRNA}'",
    )
    filter_parser.add_argument(
        "--check",
        required=False,
        default=False,
        action="store_true",
        help="Just check for filtering issues, "
        "do not write or delete any files. Default: False",
    )

    stripped_parser = subparsers.add_parser(
        "stripped",
        help="Create a stripped version of a GDICT file",
        description="Filter GeneGeneric's (#gn) and Dbxref's (#dx) out of a GDICT file,"
        " keeping only GeneDescription (#gd) entries and their metadata.",
        parents=[global_flags],
    )
    stripped_parser.add_argument(
        "--gdict_in",
        "-gin",
        required=True,
        type=str,
        metavar="PATH",
        help="Input GDICT file to strip.",
    )
    stripped_parser.add_argument(
        "--gdict_out",
        "-gout",
        required=True,
        type=str,
        metavar="PATH",
        help="New GDICT file to create.",
    )
    stripped_parser.add_argument(
        "--keep-gn",
        required=False,
        default=False,
        action="store_true",
        help="Keep GeneGeneric entries (#gn) in the stripped GDICT file. "
        "Default: False (keep only GeneDescription in the stripped).",
    )
    stripped_parser.add_argument(
        "--overwrite",
        required=False,
        default=False,
        action="store_true",
        help="Overwrite output file, if it already exists. Default: False",
    )
    stripped_parser.add_argument(
        "--large-temp",
        required=False,
        default=False,
        action="store_true",
        help="This flag is a different way to parse large TEMP Description gdicts. "
        "Useful if you started a new .gdict project without (or with a small) "
        "stripped gdict. This will strip all #dx entries, but in labels that start with"
        " #gd gff_gene, it will keep all #dx's unique ncbi_desc to better help the "
        "manual curation. After parsing this stripped version, the user should re-start"
        " the process using this parsed stripped as the first `newest_gdict_file`.",
    )

    standardize_parser = subparsers.add_parser(
        "standardize",
        help="Standardize gene names in GFF3 files.",
        description="Standardize gene names across features in "
        "GFF3 files using a GDICT file.",
        parents=[global_flags],
    )
    # mutually exclusive group for GFF or TSV input
    flag_group = standardize_parser.add_mutually_exclusive_group(required=True)
    flag_group.add_argument(
        "--gff",
        type=str,
        metavar="PATH",
        help="GFF3 file to standardize.",
    )
    flag_group.add_argument(
        "--tsv",
        type=str,
        metavar="PATH",
        help="TSV file with indexed GFF3 files to standardize.",
    )

    standardize_parser.add_argument(
        "--gdict",
        required=True,
        type=str,
        metavar="PATH",
        help="GDICT file to use for standardization. ",
    )
    standardize_parser.add_argument(
        "--AN-column",
        required=False,
        default="AN",
        type=str,
        metavar="STR",
        help="Column name for NCBI Accession Number inside the TSV. Default: AN",
    )
    standardize_parser.add_argument(
        "--gff-ext",
        required=False,
        default=".gff3",
        type=str,
        metavar="STR",
        help="File Extension for GFF files. Default: '.gff3'",
    )
    standardize_parser.add_argument(
        "--gff-suffix",
        required=False,
        default="",
        type=str,
        metavar="STR",
        help="Suffix to be added when building GFF Paths from the TSV file. "
        "Example: '_clean' will create GFF paths like '<AN>_clean.gff3' if "
        "--gff-ext is '.gff3'. ",
    )
    standardize_parser.add_argument(
        "--in-folder",
        required=False,
        default=False,
        action="store_true",
        help="Expect GFF3 files to be stored in subfolders named after the accession"
        "number, e.g., 'AN1234567/AN1234567.gff3'. Default: False"
        "(expect GFF files to be in the same folder as the TSV file).",
    )
    standardize_parser.add_argument(
        "--query-string",
        required=False,
        default=gff3_utils.QS_GENE_TRNA_RRNA,
        type=str,
        metavar="STR",
        help="Query string that pandas filter features in GFF. "
        f"Default: '{gff3_utils.QS_GENE_TRNA_RRNA}'",
    )
    standardize_parser.add_argument(
        "--check",
        required=False,
        default=False,
        action="store_true",
        help="Just check for standardization issues, "
        "do not modify the GFF3 file. Default: False",
    )
    standardize_parser.add_argument(
        "--second-place",
        required=False,
        default=False,
        action="store_true",
        help="Add gdt-tag pair to the second place in the GFF3 file, after the ID. "
        "Default: False (add to the end of the attributes field).",
    )
    standardize_parser.add_argument(
        "--gdt-tag",
        required=False,
        default="gdt_label",
        type=str,
        metavar="STR",
        help="Tag to use for the GDT key/value pair in the GFF3 file. "
        "Default: 'gdt_label='.",
    )
    standardize_parser.add_argument(
        "--error-on-missing",
        required=False,
        default=False,
        action="store_true",
        help="Raise an error if a feature is missing in the GDICT file. "
        "Default: False (just log a warning and skip the feature).",
    )
    standardize_parser.add_argument(
        "--save-copy",
        required=False,
        default=False,
        action="store_true",
        help="Save a copy of the original GFF3 file with a .original suffix. "
        "Default: False (change inplace).",
    )

    args = main_parser.parse_args()

    if not args.quiet:
        print(GDT_BANNER)

    log = log_setup.setup_logger(
        args.verbose,
        args.log,
        args.quiet,
        args.no_log_file,
        args.command,
    )
    log.info(f"GDT v{__version__} - Gene Dictionary Tool")
    log.trace(f"Full args: {args}")
    log.debug(f"Working directory: {Path().resolve()}")
    log.trace(f"CLI script location: {Path(__file__).resolve()}")

    log.trace("CLI execution started")
    log.trace(f"call path: {Path().resolve()}")
    log.trace(f"cli  path: {Path(__file__)}")
    log.trace(f"args: {args}")

    match args.command:
        case "filter":
            filter_command(args, log)

        case "stripped":
            stripped_command(args, log)

        case "standardize":
            standardize_command(args, log)
        case _:
            log.error(f"Unknown command: {args.command}")
            exit(1)

    log.trace("CLI execution finished")
    exit(0)
