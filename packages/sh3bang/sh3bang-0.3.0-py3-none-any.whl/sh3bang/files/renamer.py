import os
from pathlib import Path


def rename_files(folder: str, prefix: str = "", dry_run: bool = False):
    """Rename files in a folder by replacing spaces with underscores.
    Optionally add a prefix to each file.
    """
    folder_path = Path(folder)

    if not folder_path.exists() or not folder_path.is_dir():
        raise ValueError(f"{folder} is not a valid directory")

    for file in folder_path.iterdir():
        if file.is_file():
            new_name = file.name.replace(" ", "_")
            if prefix:
                new_name = f"{prefix}_{new_name}"
            new_path = file.with_name(new_name)

            if dry_run:
                print(f"[DRY RUN] Would rename: {file.name} -> {new_name}")
            else:
                file.rename(new_path)
                print(f"Renamed: {file.name} -> {new_name}")
