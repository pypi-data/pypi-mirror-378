import json
from starbound import cli

def test_workshop_list_json_empty(capsys):
    rc = cli.main(["workshop", "list", "--json"])
    assert rc == 0
    out = capsys.readouterr().out.strip()
    # Should at least be valid JSON list
    data = json.loads(out or "[]")
    assert isinstance(data, list)


def test_workshop_sync_dry_run_and_copy(tmp_path, capsys):
    # Arrange workshop path structure: <steam>/steamapps/workshop/content/211820/12345/contents.pak
    steam = tmp_path / "steam"
    workshop_content = steam / "steamapps" / "workshop" / "content" / "211820" / "12345"
    workshop_content.mkdir(parents=True)
    src_pak = workshop_content / "contents.pak"
    src_pak.write_bytes(b"pakdata")

    mods_dir = tmp_path / "mods"
    mods_dir.mkdir(parents=True)

    # Dry run should print planned action
    rc = cli.main(["workshop", "sync", "--steam-dir", str(steam), "--mods-dir", str(mods_dir), "--dry-run"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "copy" in out and "contents.pak" in out

    # Real copy
    rc = cli.main(["workshop", "sync", "--steam-dir", str(steam), "--mods-dir", str(mods_dir)])
    assert rc == 0
    # Assert file exists
    dst = mods_dir / "12345.pak"
    assert dst.exists() and dst.read_bytes() == b"pakdata"