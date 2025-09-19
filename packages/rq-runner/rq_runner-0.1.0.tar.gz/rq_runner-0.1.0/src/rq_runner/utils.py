from pathlib import Path


def get_settings_files(sub_dir='rq-runner', filename='settings.toml') -> list[Path]:
    return [
        Path.cwd() / filename,
        Path.home() / sub_dir / filename,
        Path(f'/etc/{sub_dir}/{filename}'),
    ]


def get_ansible_cfg() -> Path | None:
    for f in get_settings_files(filename='ansible.cfg'):
        if f.exists():
            return f
    return None
