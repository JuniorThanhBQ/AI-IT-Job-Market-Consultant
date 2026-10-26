import subprocess


def run(root, image, config, _target=None):
    options = [arg for path in config["skip-dirs"] for arg in ("--skip-dirs", path)]
    return subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "-v",
            f"{root}:/src:ro",
            image,
            "fs",
            "--scanners",
            ",".join(config["scanners"]),
            "--timeout",
            config["timeout"],
            "--severity",
            ",".join(config["severity"]),
            "--exit-code",
            "1",
            *options,
            "/src",
        ],
        check=False,
    ).returncode
