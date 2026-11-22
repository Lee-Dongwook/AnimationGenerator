import os
import stat
import subprocess
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
SCRIPT = ROOT_DIR / "scripts" / "download_coverr_video.sh"


def test_coverr_download_script_prefers_short_vertical_video(tmp_path):
    fake_curl = tmp_path / "curl"
    arguments_file = tmp_path / "curl-arguments"
    fake_curl.write_text(
        """#!/bin/sh
printf '%s\\n' "$@" >> "$FAKE_CURL_ARGUMENTS"
for argument in \"$@\"; do
  case \"$argument\" in
    *api.coverr.co/videos*)
      printf '%s' '{\"hits\":[{\"id\":\"long\",\"title\":\"Rain forest long\",\"duration\":30,\"is_vertical\":false,\"urls\":{\"mp4_download\":\"https://download/long\"}},{\"id\":\"short\",\"title\":\"Rain forest short\",\"duration\":\"16\",\"is_vertical\":false,\"urls\":{\"mp4_download\":\"https://download/short\"}}]}'
      exit 0
      ;;
  esac
done
while [ \"$#\" -gt 0 ]; do
  if [ \"$1\" = \"-o\" ]; then
    printf 'mp4-data' > \"$2\"
    exit 0
  fi
  shift
done
exit 1
"""
    )
    fake_curl.chmod(fake_curl.stat().st_mode | stat.S_IXUSR)
    environment = {
        **os.environ,
        "COVERR_API_KEY": "test-key",
        "FAKE_CURL_ARGUMENTS": str(arguments_file),
        "PATH": f"{tmp_path}:{os.environ['PATH']}",
    }

    result = subprocess.run(
        [str(SCRIPT), "rain", "forest"],
        cwd=ROOT_DIR,
        env=environment,
        check=True,
        capture_output=True,
        text=True,
    )
    output_path = Path(result.stdout.strip())

    try:
        assert output_path.name.startswith("coverr-short.")
        assert output_path.suffix == ".mp4"
        assert output_path.read_bytes() == b"mp4-data"
        assert not output_path.with_suffix("").exists()
        assert "query=rain forest" in arguments_file.read_text()
    finally:
        output_path.unlink(missing_ok=True)
