import json
from starbound import cli
import starbound.workshop as ws

def test_prepare_titles_file_with_mock(tmp_path, monkeypatch, capsys):
    # Mock workshop tree
    steam = tmp_path/"steam"
    work = steam/"steamapps"/"workshop"/"content"/"211820"
    (work/"100").mkdir(parents=True)
    (work/"200").mkdir(parents=True)
    (work/"100"/"contents.pak").write_bytes(b"pak-100")
    (work/"200"/"contents.pak").write_bytes(b"pak-200")

    # Mock metadata so that 100 has title 'Cool Mod', 200 has 'Old Stuff'
    def fake_meta(ids):
        mapping = {
            '100': {'publishedfileid': '100', 'title': 'Cool Mod'},
            '200': {'publishedfileid': '200', 'title': 'Old Stuff'},
        }
        return [mapping[i] for i in ids if i in mapping]
    monkeypatch.setattr(ws, 'get_metadata', fake_meta)

    titles_file = tmp_path/"titles.txt"
    titles_file.write_text("# wanted titles\nCool\n")

    outdir = tmp_path/"modset"
    rc = cli.main(["workshop","prepare","--steam-dir", str(steam), "--out-dir", str(outdir), "--titles-file", str(titles_file)])
    assert rc == 0
    # Should include only 100 based on title match
    assert (outdir/"100.pak").exists()
    assert not (outdir/"200.pak").exists()