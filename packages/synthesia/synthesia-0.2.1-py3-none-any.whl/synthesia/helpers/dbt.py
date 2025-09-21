"""Modules to pull connection details from dbt profiles."""

from dlt.sources.credentials import GcpServiceAccountCredentials
from pathlib import Path
import yaml

def get_dbt_profile(profile_name: str, profiles_dir: str = "~/.dbt") -> dict:
    profiles_dir = Path(profiles_dir).expanduser() / "profiles.yml"
    if not profiles_dir.is_file():
        raise FileNotFoundError(f"Could not find `profiles.yml` file at {profiles_dir}")

    with open(profiles_dir, "r") as f:
        profiles = yaml.safe_load(f)

    profile = profiles.get(profile_name)
    if profile is None:
        raise ValueError(f"Profile '{profile_name}' not found in {profiles_dir}")

    return profile

def get_dbt_target(profile: dict, target_name: str | None = None) -> dict:
    targets = profile.get("outputs")
    if targets is None:
        raise ValueError("No outputs found in the dbt profile.")

    if target_name is None:
        target_name = profile.get("target")
        if target_name is None:
            raise ValueError("No target specified in the dbt profile.")

    target = targets.get(target_name)
    if target is None:
        raise ValueError(f"Target '{target_name}' not found in the dbt profile outputs.")

    return target

def get_credentials_from_target(target: dict) -> GcpServiceAccountCredentials:
    required_keys = ["keyfile"]
    missing_keys = [key for key in required_keys if key not in target]
    if missing_keys:
        raise ValueError(f"Missing required keys in target: {', '.join(missing_keys)}")
    with open(target["keyfile"], "r") as f:
        keyfile_json = f.read()
    credentials = GcpServiceAccountCredentials()
    credentials.parse_native_representation(keyfile_json)
    return credentials

def find_project_config_file(start_path: Path | str = ".") -> Path | None:
    current_dir = Path(start_path).resolve()
    for parent in [current_dir, *current_dir.parents]:
        candidate = parent / "dbt_project.yml"
        if candidate.is_file():
            return candidate
    return None

def get_credentials_from_current_project(
    target_name: str = None,
    profiles_dir: str = "~/.dbt",
) -> GcpServiceAccountCredentials:
    project_file = find_project_config_file(".")
    if project_file is None:
        raise FileNotFoundError("Could not find `dbt_project.yml` in current or parent directories.")

    with open(project_file, "r") as f:
        project_config = yaml.safe_load(f)
    profile_name = project_config.get("profile")
    if profile_name is None:
        raise ValueError("No profile specified in `dbt_project.yml`.")

    profile = get_dbt_profile(profile_name, profiles_dir)
    target = get_dbt_target(profile, target_name)
    credentials = get_credentials_from_target(target)
    return credentials
