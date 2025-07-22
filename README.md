# botocore-sign-perf

Benchmarking tool for Boto S3 signature performance.

## Usage

* Ensure you have [`hyperfine`][hyperfine] and [`uv`][uv] installed.
* Run `uv run scaff.py`, which will compose a command line that will run `main.py`
  with various versions of boto3/botocore.
* Examine `log.jsonl` or `uv run analyze_results.py` to group results into Markdown form.

[hyperfine]: https://github.com/sharkdp/hyperfine
[uv]: https://github.com/astral-sh/uv
