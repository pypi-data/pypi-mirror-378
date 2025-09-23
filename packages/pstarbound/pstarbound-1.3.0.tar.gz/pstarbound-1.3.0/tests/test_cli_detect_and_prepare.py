import json, os
from pathlib import Path
from starbound import cli

def test_workshop_prepare_only_exclude_patterns(tmp_path, capsys):
    steam = tmp_path/"steam"
    work = steam/"steamapps"/"workshop"/"content"/"211820"
    (work/"X-cool").mkdir(parents=True)
    (work/"X-old").mkdir(parents=True)
    (work/"X-cool"/"contents.pak").write_bytes(b"pak-cool")
    (work/"X-old"/"contents.pak").write_bytes(b"pak-old")

    outdir = tmp_path/"modset2"
    # Include X-* but exclude *old
    rc = cli.main(["workshop","prepare","--steam-dir", str(steam), "--out-dir", str(outdir), "--only", "X-*", "--exclude", "*old"])
    assert rc == 0
    assert (outdir/"X-cool.pak").exists()
    assert not (outdir/"X-old.pak").exists()


def test_detect_install_with_mock_paths(tmp_path, capsys):
    steam = tmp_path/"steam"
    install = steam/"steamapps"/"common"/"Starbound"
    mods = install/"mods"
    workshop = steam/"steamapps"/"workshop"/"content"/"211820"
    mods.mkdir(parents=True)
    workshop.mkdir(parents=True)

    rc = cli.main(["detect-install", "--steam-dir", str(steam), "--json"])
    assert rc == 0
    out = capsys.readouterr().out
    obj = json.loads(out)
    assert Path(obj["install"]) == install
    assert Path(obj["mods"]) == mods
    assert Path(obj["workshop"]) == workshop


def test_workshop_prepare_ids_and_pack(tmp_path, capsys):
    steam = tmp_path/"steam"
    work = steam/"steamapps"/"workshop"/"content"/"211820"
    (work/"A1").mkdir(parents=True)
    (work/"A2").mkdir(parents=True)
    (work/"A1"/"contents.pak").write_bytes(b"pak-A1")
    (work/"A2"/"contents.pak").write_bytes(b"pak-A2")

    outdir = tmp_path/"modset"
    # Prepare only A2
    rc = cli.main(["workshop","prepare","--steam-dir", str(steam), "--out-dir", str(outdir), "--ids", "A2"])
    assert rc == 0
    assert (outdir/"A2.pak").exists()
    assert not (outdir/"A1.pak").exists()

    # Pack prepared dir
    outpak = tmp_path/"modset.pak"
    rc = cli.main(["workshop","pack","--dir", str(outdir), "-o", str(outpak)])
    assert rc == 0 and outpak.exists() and outpak.stat().st_size > 0

    # Verify directory: add one bad pak and expect non-zero exit code
    bad = outdir/"bad.pak"
    bad.write_bytes(b"garbage")
    rc = cli.main(["workshop","verify","--dir", str(outdir), "--json"])
    assert rc == 1
