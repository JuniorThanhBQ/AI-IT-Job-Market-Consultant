import subprocess


def run(root, image, config, _target=None):
    options = [arg for rule in config["rules"] for arg in ("--config", rule)]
    options += [arg for level in config["severity"] for arg in ("--severity", level)]
    options += [
        arg for path in config.get("exclude", []) for arg in ("--exclude", path)
    ]
    return subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "-v",
            f"{root}:/src:ro",
            "-w",
            "/src",
            image,
            "semgrep",
            "scan",
            *options,
            "--error",
            "--metrics=off",
            ".",
        ],
        check=False,
    ).returncode
