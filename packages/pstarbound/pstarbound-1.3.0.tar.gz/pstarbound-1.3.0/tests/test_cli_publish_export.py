from starbound import cli

def test_publish_export_roundtrip(tmp_path):
    # Arrange
    srcdir = tmp_path / "src"
    (srcdir / "assets").mkdir(parents=True)
    content = "hello test"
    (srcdir / "assets" / "file.txt").write_text(content)
    outpak = tmp_path / "out.pak"
    dest = tmp_path / "dest"

    # Act
    rc = cli.main(["publish", str(srcdir), "-o", str(outpak)])
    assert rc == 0
    assert outpak.exists()

    rc = cli.main(["export", str(outpak), "-d", str(dest)])
    assert rc == 0

    # Assert
    assert (dest / "assets" / "file.txt").read_text() == content


def test_export_list(tmp_path, capsys):
    # Build a small pak
    srcdir = tmp_path / "src2"
    (srcdir / "assets").mkdir(parents=True)
    (srcdir / "assets" / "file2.txt").write_text("content")
    outpak = tmp_path / "out2.pak"
    cli.main(["publish", str(srcdir), "-o", str(outpak)])

    # List contents
    rc = cli.main(["export", "--list", str(outpak)])
    assert rc == 0
    out = capsys.readouterr().out
    # Paths are normalized to lowercase with leading slash
    assert "/assets/file2.txt" in out
