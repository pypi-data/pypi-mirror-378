# -*- coding: utf-8 -*-
"""Utilities for working with GFF3 files in the GDT package.

This module provides functions to load, filter, and standardize GFF3 files,
as well as to check them against a GeneDict. It includes functionality for
loading GFF3 files into pandas DataFrames, filtering out ORFs, and checking
the presence of gene IDs in a GeneDict.

"""

import concurrent.futures as cf
import re
import shutil
import types
from functools import partial
from pathlib import Path
from typing import Any, Callable, cast

import pandas as pd

from . import gdict, log_setup

GFF3_COLUMNS: tuple[str, ...] = (
    "seqid",
    "source",
    "type",
    "start",
    "end",
    "score",
    "strand",
    "phase",
    "attributes",
)
QS_GENE = "type == 'gene'"
QS_GENE_TRNA_RRNA = "type in ('gene', 'tRNA', 'rRNA')"

_RE_ID = re.compile(r"ID=([^;]+)")
_RE_contains_GeneID = re.compile(r"Dbxref=.*GeneID:")


def load_gff3(
    filename: str | Path,
    sep: str = "\t",
    comment: str = "#",
    header: int | None = None,
    names: tuple[str, ...] = GFF3_COLUMNS,
    usecols: tuple[str, ...] = ("type", "start", "end", "attributes"),
    query_string: str | None = None,
    **kwargs: Any,
) -> pd.DataFrame:
    """Load a GFF3 file into a pandas DataFrame, optionally filtering by a query string.

    Args:
        filename (str | Path): Path to the GFF3 file.
        sep (str): Separator used in the file.
        comment (str): Comment character in the file.
        header (int | None): Row number to use as the column names, None if no header.
        names (tuple[str, ...]): Tuple of column names to use.
        usecols (list[str]): List of columns to read from the file.
        query_string (str | None): Query string to filter the DataFrame.
                                   Defaults to None, which means no filtering.
        **kwargs: Additional keyword arguments passed to `pd.read_csv`.

    Returns:
        pd.DataFrame: DataFrame containing the filtered GFF3 data.

    """
    if query_string:
        df: pd.DataFrame = (
            pd.read_csv(
                filename,
                sep=sep,
                comment=comment,
                header=header,
                names=names,
                usecols=usecols,
                **kwargs,
            )
            .query(query_string)
            .sort_values(by=["start", "end"], ascending=[True, False], ignore_index=True)
        )
        return df

    df = pd.read_csv(
        filename,
        sep=sep,
        comment=comment,
        header=header,
        names=names,
        usecols=usecols,
        **kwargs,
    ).sort_values(by=["start", "end"], ascending=[True, False], ignore_index=True)
    return df


def filter_orfs(
    gff3_df: pd.DataFrame,
    orfs_strings: list[str] = ["Name=ORF", "Name=orf"],
    *,
    extended: bool = False,
) -> pd.DataFrame:
    """Filter out ORFs from a GFF3 DataFrame.

    Args:
        gff3_df (pd.DataFrame): DataFrame containing GFF3 data.
        orfs_strings (list): List of strings to identify ORFs.
            Defaults to ['Name=ORF', 'Name=orf'].
        extended (bool): If True, adds more strings to filter out ORFs.
            Defaults to False. If True, adds ['gene=ORF', 'gene=orf', 'gene=Orf',
            'Name=Orf'] to the filter list.

    Returns:
        pd.DataFrame: DataFrame with ORFs removed.

    """
    if extended:
        orfs_strings.extend(["gene=ORF", "gene=orf", "gene=Orf", "Name=Orf"])

    return gff3_df[~gff3_df["attributes"].str.contains("|".join(orfs_strings))].reset_index(
        drop=True
    )


# will be pre-compiled by the PathBuilder class
def _std_builder(
    base_path: Path,
    suffix: str,
    ext: str,
    an: str,
) -> Path:
    return base_path / f"{an}{suffix}{ext}"


# will be pre-compiled by the PathBuilder class
def _folder_builder(
    base_path: Path,
    suffix: str,
    ext: str,
    an: str,
) -> Path:
    return base_path / an / f"{an}{suffix}{ext}"


class PathBuilder:
    """Flexible class to build paths (mostly GFF/Fasta) based on accession numbers.

    This class provides a framework for building file paths with
    different strategies that can be swapped at runtime.
    """

    def __init__(self, ext: str = ".gff3") -> None:
        """Initialize the builder with no build method set."""
        self._build_method: Callable[[str], Path] | None = None
        self.ext: str = ext
        self._str: str = f"PathBuilder('{ext}', build=None)"

    def build(self, an: str) -> Path:
        """Build the path for a given accession number.

        This method uses the currently active build strategy.

        Args:
            an (str): Accession number.

        Returns:
            Path: Path to the GFF3 file.

        Raises:
            ValueError: If no build method has been set.

        """
        if self._build_method is None:
            raise ValueError(
                "No build method set. Use one of the 'use_*_builder' methods first."
            )
        return self._build_method(an)

    def use_std_builder(
        self,
        base: str | Path,
        suffix: str = "",
    ) -> "PathBuilder":
        """Set the standard filesystem-based build method.

        This method expects files to be stored in a flat structure
        under the specified base directory, with filenames formatted as
        "<accession_number><suffix><self.ext>".

        Args:
            base (str | Path]): Base directory where files are stored.
            suffix (str): Suffix to append to the filename. Defaults to "".

        Returns:
            PathBuilder: Returns self.

        """
        base_path = Path(base).resolve()

        self._build_method = partial(
            _std_builder,
            base_path,
            suffix,
            self.ext,
        )
        self._str = (
            f"PathBuilder('{self.ext}', build='std', base='{base_path}', "
            f"suffix='{suffix}')"
        )
        return self

    def use_folder_builder(
        self,
        base: str | Path,
        suffix: str = "",
    ) -> "PathBuilder":
        """Set the folder-based build method.

        This method expects files to be stored in subfolders named after
        the accession number, with filenames formatted as
        "<accession_number>/<accession_number><suffix><self.ext>".

        Args:
            base (str | Path): Base directory where files are stored.
            suffix (str): Suffix to append to the filename. Defaults to "".

        Returns:
            PathBuilder: Returns self.

        """
        base_path = Path(base).resolve()

        self._build_method = partial(
            _folder_builder,
            base_path,
            suffix,
            self.ext,
        )

        self._str = (
            f"PathBuilder('{self.ext}', build='folder', base='{base_path}', "
            f"suffix='{suffix}')"
        )
        return self

    def use_custom_builder(
        self,
        builder_func: Callable[["PathBuilder", str], Path],
        help_text: str | None = None,
    ) -> "PathBuilder":
        """Set a custom build function as a drop-in replacement.

        The custom function should have the signature: (self, an: str) -> Path
        where 'self' refers to the PathBuilder instance.

        Args:
            builder_func (Callable[["PathBuilder", str], Path]): A function that takes
                the PathBuilder instance (self) and an accession number (str) and
                returns a Path object.
            help_text (str | None): Optional help text to describe the
                custom builder function. This is used by the __repr__ method
                to provide more context about the builder. If not provided,
                it defaults to the function's name.

        Returns:
            PathBuilder: Returns self.

        Example:
            import tigre
            from pathlib import Path

            def my_custom_builder(self, an: str) -> Path:
                return Path(f"/custom/path/{an}_special{self.ext}")

            gff_path = tigre.PathBuilder(".gff")
            gff_path.use_custom_builder(my_custom_builder)
            path = gff_path.build("NC_123456.1")
            print(path)  # Outputs: /custom/path/NC_123456.1_special.gff

        """
        self._build_method = types.MethodType(builder_func, self)

        if help_text is None:
            help_text = getattr(builder_func, "__name__", "anonymous_function")

        self._str = f"PathBuilder('{self.ext}', build='custom', help_text='{help_text}')"
        return self

    def __repr__(self) -> str:
        """Return a string representation of the PathBuilder."""
        return self._str


def check_single_an(
    an: str,
    an_path: Path,
    gene_set: set[str],
    keep_orfs: bool = False,
    query_string: str = QS_GENE_TRNA_RRNA,
) -> dict[str, str | int | list[str]]:
    """Check a single GFF3 file for gene information and dbxref.

    Args:
        an (str): Accession number to check.
        an_path (Path): Path to the GFF3 file.
        gene_set (set[str]): Set of keys from a GeneDict to check against.
        keep_orfs (bool): Whether to keep ORFs in the DataFrame.
        query_string (str): Query string to filter the DataFrame.

    Returns:
        dict: Dictionary containing the results of the check.

    """
    try:
        df = load_gff3(an_path, query_string=query_string)

        if not keep_orfs:  # removing ORFs
            df = filter_orfs(df)

        df["gene_id"] = df["attributes"].str.extract(_RE_ID, expand=False)  # type: ignore[call-overload]
        gene_ids = df["gene_id"].values

        in_gene_dict_mask = [g in gene_set for g in gene_ids]

        # Get dbxref info
        dbxref_mask = df["attributes"].str.contains(_RE_contains_GeneID, na=False)

        status = "good_to_go"
        if not all(in_gene_dict_mask):
            status = "M_in_gene_dict" if all(dbxref_mask) else "M_dbxref_GeneID"

        return {
            "AN": an,
            "status": status,
            "gene_count": len(df),
            "dbxref_count": sum(dbxref_mask),
            "gene_dict_count": sum(in_gene_dict_mask),
            "genes": gene_ids.tolist(),
            "genes_without_dbxref": df[~dbxref_mask]["gene_id"].tolist(),
            "genes_with_dbxref": df[dbxref_mask]["gene_id"].tolist(),
            "genes_not_in_dict": [
                g for g, in_dict in zip(gene_ids, in_gene_dict_mask) if not in_dict
            ],
            "genes_in_dict": [
                g for g, in_dict in zip(gene_ids, in_gene_dict_mask) if in_dict
            ],
        }
    except Exception as e:
        return {"AN": an, "status": "error", "error": str(e)}


def _check_column(
    log: log_setup.GDTLogger,
    df: pd.DataFrame,
    col: str,
    df_txt: str = "TSV",
) -> None:
    """Check if a specific column exists in the DataFrame."""
    log.trace(f"check_column called | col: {col} | df_txt: {df_txt}")
    if col not in df.columns:
        log.error(f"Column '{col}' not found in DataFrame")
        log.error(f"Available columns: {df.columns}")
        raise ValueError(f"Column '{col}' not found in {df_txt}. Please check the file.")


def check_gff_in_tsv(
    log: log_setup.GDTLogger,
    df: pd.DataFrame,
    gff_builder: PathBuilder,
    an_column: str = "AN",
) -> None:
    """Check if GFF3 files exist for each accession number in the DataFrame.

    Args:
        log (GDTLogger): Logger instance for logging messages.
        df (pd.DataFrame): DataFrame containing accession numbers.
        base_path (Path): Base path where GFF3 files are expected to be found.
        gff_builder (GFFBuilder): Function to build GFF file paths.
        an_column (str): Column name containing accession numbers. Default is "AN".

    """
    log.trace(f"check_gff_in_tsv called | {gff_builder}")
    _check_column(log, df, an_column, "TSV")

    no_files = [
        (an, an_path)
        for an in df[an_column]
        if not (an_path := gff_builder.build(an)).is_file()
    ]

    if no_files:
        for an, path in no_files:
            log.error(f"GFF3 file not found for {an}, expected {path}")
        raise FileNotFoundError(
            f"Missing {len(no_files)} GFF3 files. Please check the log for details."
        )


def filter_whole_tsv(
    log: log_setup.GDTLogger,
    tsv_path: Path,
    gdict_path: Path | None = None,
    keep_orfs: bool = False,
    workers: int = 0,
    an_column: str = "AN",
    gff_ext: str = ".gff3",
    gff_suffix: str = "",
    in_folder: bool = False,
    query_string: str = QS_GENE_TRNA_RRNA,
    check_flag: bool = False,
) -> None:
    """Filter a whole TSV containing GFF3 files and check them against a GeneDict.

    Args:
        log (GDTLogger): Logger instance for logging messages.
        tsv_path (Path): Path to the TSV file containing accession numbers.
        gdict_path (Path | None): Path to the GDICT file.
                                   If None, an empty GeneDict is used.
        keep_orfs (bool): Whether to keep ORFs in the GFF3 files. Default is False.
        workers (int): Number of worker processes to use for parallel processing.
                       Default is 0, meaing max cpu cores.
        an_column (str): Column name containing accession numbers in the TSV file.
                         Default is "AN".
        gff_ext (str): File Extension for GFF3 files. Default is ".gff3".
        gff_suffix (str): Suffix to be added when building GFF Paths from the TSV file.
                         Example: "_clean" will create GFF paths like "<AN>_clean.gff3"
                          if --gff-ext is ".gff3".
        in_folder (bool): If True, GFF3 files are expected to be stored in subfolders
                          named after the accession number. Default is False
                          (expect GFF files to be in the same folder as the TSV file)
        query_string (str): Query string to filter GFF3 files.
                            Default is QS_GENE_TRNA_RRNA.
        check_flag (bool): If True, do not save changes any files.
                           Default is False.

    """
    an_missing_dbxref_geneid: list[str] = []
    an_missing_gene_dict: list[str] = []
    an_good_to_go: list[str] = []

    # check if tsv_path exists
    if not tsv_path.exists():
        log.error(f"tsv file not found: {tsv_path}")
        raise FileNotFoundError(f"tsv file not found: {tsv_path}")

    base_folder = tsv_path.parent

    gff_builder = (
        PathBuilder(gff_ext).use_folder_builder(base_folder, gff_suffix)
        if in_folder
        else PathBuilder(gff_ext).use_std_builder(base_folder, gff_suffix)
    )
    log.debug(f"{gff_builder}")

    tsv = pd.read_csv(tsv_path, sep="\t")
    check_gff_in_tsv(log, tsv, gff_builder, an_column)

    MISC_DIR = base_folder / "misc"  # noqa: N806
    GDT_DIR = MISC_DIR / "gdt"  # noqa: N806
    GDT_DIR.mkdir(511, True, True)  # 511 = 0o777

    # check if tsv_path exists, if not, create empty gene_dict
    if gdict_path:
        if not gdict_path.exists():
            log.error(f"gdict file not found: {gdict_path}")
            raise FileNotFoundError(f"gdict file not found: {gdict_path}")

        # check if gdict file is in GDT_DIR
        if gdict_path.parent != GDT_DIR:
            gdict_path = Path(shutil.move(gdict_path, GDT_DIR / gdict_path.name)).resolve()
            log.info(f"Moving gdict file to {gdict_path}")

        gene_set = gdict.read_gdict_as_set(gdict_path)
        log.debug(f"GeneDict loaded as set from {gdict_path}")
        log.trace(f"Entries in GeneDict set: {len(gene_set)}")

    else:
        gene_set = set()
        log.debug("No gdict file provided. Using empty GeneDict.")

    # start processing
    log.info(f"Processing {len(tsv)} ANs with {workers} workers")
    with cf.ThreadPoolExecutor(max_workers=workers) as executor:
        tasks = [
            executor.submit(
                check_single_an,
                an,
                gff_builder.build(an),
                gene_set,
                keep_orfs,
                query_string,
            )
            for an in tsv[an_column]
        ]

        for future in cf.as_completed(tasks):
            result = future.result()
            if result["status"] == "error":
                log.error(f"Error processing {result['AN']}: {result['error']}")
                continue

            an: str = cast(str, result["AN"])  # TODO, how can i remove this cast?
            log.trace(f"-- [Processing: {an}] --")
            log.trace(
                f"\tgenes: {result['gene_count']} | "
                f"have dbxref: {result['dbxref_count']} | "
                f"genes in gene_dict: {result['gene_dict_count']}"
            )
            log.trace(f"\tgenes: {result['genes']}")
            log.trace(f"\twith dbxref : {result['genes_with_dbxref']}")
            log.trace(f"\tin gene_dict : {result['genes_in_dict']}")
            log.trace(f"\twithout dbxref : {result['genes_without_dbxref']}")
            log.trace(f"\tnot in gene_dict: {result['genes_not_in_dict']}")

            if result["status"] == "M_in_gene_dict":
                log.trace(f"\t{an} is missing genes in gene_dict but have dbxref")
                an_missing_gene_dict.append(an)

            elif result["status"] == "M_dbxref_GeneID":
                log.trace(
                    f"\t{an} is missing genes in gene_dict and is also missing dbxref"
                )
                an_missing_dbxref_geneid.append(an)

            else:
                log.trace(f"\t{an} is good to go!")
                an_good_to_go.append(an)

            log.trace(f"-- [End Processing: {an}] --")

    log.info(f"ANs good to go: {len(an_good_to_go)}")
    log.trace(f"ANs good to go: {an_good_to_go}")
    log.info(f"ANs missing gene_dict: {len(an_missing_gene_dict)}")
    log.trace(f"ANs missing gene_dict: {an_missing_gene_dict}")
    log.info(f"ANs missing dbxref: {len(an_missing_dbxref_geneid)}")
    log.trace(f"ANs missing dbxref: {an_missing_dbxref_geneid}")
    log.info("Processing finished, resolving output files")

    path_gene_dict = MISC_DIR / "AN_missing_gene_dict.txt"
    path_dbxref = MISC_DIR / "AN_missing_dbxref_GeneID.txt"

    if an_missing_dbxref_geneid and not check_flag:
        with open(path_dbxref, "w") as f:
            f.write("\n".join(an_missing_dbxref_geneid))

    elif not check_flag:
        log.debug("No ANs missing dbxref GeneID, skipping file creation")
        # check if file exists and remove it
        if path_dbxref.exists():
            log.debug(f"Removing file: {path_dbxref}")
            path_dbxref.unlink()

    if an_missing_gene_dict and not check_flag:
        with open(path_gene_dict, "w") as f:
            f.write("\n".join(an_missing_gene_dict))

    elif not check_flag:
        log.debug("No ANs missing gene_dict, skipping file creation")
        if path_gene_dict.exists():
            log.debug(f"Removing file: {path_gene_dict}")
            path_gene_dict.unlink()

    if check_flag:
        log.info("Check flag is set, not saving any changes to any files.")


def standardize_tsv(
    log: log_setup.GDTLogger,
    tsv_path: Path,
    gdict_path: Path,
    an_colum: str,
    gff_ext: str,
    gff_suffix: str,
    in_folder: bool,
    query_string: str,
    check_flag: bool,
    second_place: bool,
    gdt_tag: str,
    error_on_missing: bool,
    save_copy: bool,
) -> None:
    """Standardize GFF3 files listed in a TSV based on a GeneDict.

    Args:
        log (GDTLogger): Logger instance for logging messages.
        tsv_path (Path): Path to the TSV file containing accession numbers.
        gdict_path (Path): Path to the GDICT file.
        an_colum (str): Column name containing accession numbers in the TSV file.
        gff_ext (str): File Extension for GFF3 files. Default is ".gff3".
        gff_suffix (str): Suffix to be added when building GFF Paths from the TSV file.
                          Example: "_clean" will create GFF paths like "<AN>_clean.gff3"
                          if --gff-ext is ".gff3".
        in_folder (bool): If True, GFF3 files are expected to be stored in subfolders
                          named after the accession number. Default is False
                          (expect GFF files to be in the same folder as the TSV file)
        query_string (str): Query string to filter GFF3 files.
        check_flag (bool): If True, do not save changes to GFF3 files.
        second_place (bool): If True, add gdt_tag to the second place in attributes gff.
        gdt_tag (str): Tag to use for gdt_tag in GFF3 attributes.
        error_on_missing (bool): If True, raise an ValueError
                                 if a gene ID is not in the GeneDict.
        save_copy (bool): If True, save a copy of the original GFF3 file.

    """
    if not tsv_path.exists():
        log.error(f"tsv file not found: {tsv_path}")
        raise FileNotFoundError(f"tsv file not found: {tsv_path}")

    if not gdict_path.exists():
        log.error(f"gdict file not found: {gdict_path}")
        raise FileNotFoundError(f"gdict file not found: {gdict_path}")

    gene_dict = gdict.read_gdict(gdict_path)
    log.debug(f"Gene dictionary loaded from {gdict_path}")

    tsv = pd.read_csv(tsv_path, sep="\t")
    base_folder = tsv_path.parent

    gff_builder = (
        PathBuilder(gff_ext).use_folder_builder(base_folder, gff_suffix)
        if in_folder
        else PathBuilder(gff_ext).use_std_builder(base_folder, gff_suffix)
    )
    log.debug(f"{gff_builder}")
    check_gff_in_tsv(log, tsv, gff_builder, an_colum)

    for an in tsv[an_colum]:
        standardize_gff3(
            log,
            gff_builder.build(an),
            gene_dict,
            query_string,
            check_flag,
            second_place,
            gdt_tag,
            error_on_missing,
            save_copy,
        )

    if check_flag:
        log.info(f"Not saving new gff, check flag set to {check_flag}")


def standardize_gff3(
    log: log_setup.GDTLogger,
    gff_path: Path,
    gene_dict: gdict.GeneDict,
    query_string: str,
    check_flag: bool,
    second_place: bool,
    gdt_tag: str,
    error_on_missing: bool,
    save_copy: bool,
    single_run: bool = False,
) -> None:
    """Standardize a GFF3 file by adding a gdt_tag to the attributes column.

    Args:
        log (GDTLogger): Logger instance for logging messages.
        gff_path (Path): Path to the GFF3 file.
        gene_dict (GeneDict): GeneDict to check against.
        query_string (str): Query string to filter GFF3 features.
        check_flag (bool): If True, do not save changes to the GFF3 file.
        second_place (bool): If True, add gdt_tag to the second place in attributes gff.
        gdt_tag (str): Tag to use for the gdt_tag in GFF3 attributes.
        error_on_missing (bool): If True, raise an ValueError
                                 if a gene ID is not in the GeneDict.
        save_copy (bool): If True, save a copy of the original GFF3 file.
        single_run (bool): If True, check if the GFF3 file exists before processing.
                           Default is False, because in bulk processing,
                           the check should be done in the calling function.

    """
    if single_run and not gff_path.exists():
        log.error(f"GFF3 file not found: {gff_path}")
        raise FileNotFoundError(f"GFF3 file not found: {gff_path}")

    with open(gff_path, "r") as f:
        lines = f.readlines()

    headers, index = [], 0
    while lines[index].startswith("#"):
        headers.append(lines[index].strip())
        index += 1

    contents = []
    series_holder = pd.Series([""], dtype="string")

    for text in lines[index:]:
        if not (text := text.strip()):
            continue
        line = text.split("\t")
        joined_line = "\t".join(line)

        # line[2] is type line, line[8] is attributes
        series_holder[0] = line[2]
        if pd.eval(query_string, local_dict={"type": series_holder})[0]:  # type: ignore[index]
            gene_id = m.group(1) if (m := _RE_ID.search(line[8])) else None
            if gene_id:
                gdt_label = gene_dict.get(gene_id, None)

                if not gdt_label:
                    log.error(f"Gene ID {gene_id} not found in gene_dict.")

                    if error_on_missing:
                        raise ValueError(f"Gene ID {gene_id} not found in gene_dict.")

                    contents.append("\t".join(line))
                    continue

                gdt_str = f"{gdt_tag}={gdt_label.label}"

                if gdt_str in line[8]:
                    log.trace(f"Skipping {gdt_str} in {gff_path.name}. Already present.")
                    contents.append("\t".join(line))
                    continue

                if f"{gdt_tag}=" in line[8]:
                    log.debug(f"Removing existing {gdt_tag} tag in {gff_path.name}.")
                    line[8] = re.sub(rf"{gdt_tag}=[^;]*;?", "", line[8])
                    line[8] = line[8][:-1] if line[8].endswith(";") else line[8]

                if second_place:
                    left, right = line[8].split(";", 1)
                    line[8] = f"{left};{gdt_str};{right}" if right else f"{left};{gdt_str}"

                else:
                    line[8] = (
                        f"{line[8]}{'' if line[8].endswith(';') else ';'}"
                        f"{gdt_tag}={gdt_label.label}"
                    )
            else:
                _handle_missing_gene_id(
                    log, gff_path, query_string, joined_line, error_on_missing
                )

        contents.append("\t".join(line))

    if not check_flag:
        log.info(f"Standardizing {gff_path.name} by adding: {gdt_tag}")
        if save_copy:
            backup_path = gff_path.with_suffix(".original")
            shutil.copy(gff_path, backup_path)
            log.info(f"Backup created at {backup_path}")

        with open(gff_path, "w") as f:
            f.write("\n".join(headers))
            f.write("\n")
            f.write("\n".join(contents))
            f.write("\n\n")

    elif single_run:
        log.info(f"Not saving new gff, check flag set to {check_flag}")


def _handle_missing_gene_id(
    log: log_setup.GDTLogger,
    gff_path: Path,
    query_string: str,
    joined_line: str,
    error_on_missing: bool = False,
) -> None:
    """Handle case where gene_id is not found."""
    log.error(
        f"ID not found in {gff_path.name}. This is not supposed to happen, "
        f"and could be a problem with query_string ({query_string}). "
        f"Feature att: {joined_line}"
    )
    if error_on_missing:
        raise ValueError(f"ID not found in {gff_path.name}. att: {joined_line}")
