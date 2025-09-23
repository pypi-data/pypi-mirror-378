import json
from pathlib import Path
from starbound import cli

def test_dungeon_index_basic(tmp_path, capsys):
    assets = tmp_path/"assets"
    sdir = assets/"ships"/"export"
    sdir.mkdir(parents=True)
    (sdir/"exported.structure").write_text(json.dumps({
        "blockImage": "export_blocks.png",
        "objects": [{"name": "chair", "position": [1,2]}]
    }))
    ddir = assets/"dungeons"/"test"
    ddir.mkdir(parents=True)
    (ddir/"dummy.dungeon").write_text("{}")

    outdir = tmp_path/"out"
    rc = cli.main(["dungeon-index", "--assets", str(assets), "--out", str(outdir)])
    assert rc == 0
    idx = json.loads((outdir/"index.json").read_text())
    paths = [e["path"] for e in idx["entries"]]
    assert "/ships/export/exported.structure" in paths
    assert "/dungeons/test/dummy.dungeon" in paths