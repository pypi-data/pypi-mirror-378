import pkg_resources


def check_requirements(requirements_file: str):
    with open(requirements_file, "r") as f:
        required = [line.strip() for line in f if line.strip()]
    installed = {pkg.key for pkg in pkg_resources.working_set}

    missing = [r for r in required if r.split("==")[0].lower() not in installed]
    return missing
