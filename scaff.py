import subprocess

commands = []

for minor in range(24, 40):
    for with_awscrt in (False, True):
        withs = f"--with='botocore<1.{minor}' --with=boto3"
        if with_awscrt:
            withs += " --with=awscrt"
        commands.append(f"uv run {withs} main.py >> log.jsonl")

subprocess.check_call(
    [
        "hyperfine",
        "--warmup=3",  # If the version(s) are not in uv cache...
        *commands,
    ]
)
