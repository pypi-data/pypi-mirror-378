import json
from starbound import cli

def test_vjson_edit_and_player_info(tmp_path, capsys):
    # Arrange an input SBVJ01 by using vjson-make
    input_json = tmp_path/"in.json"
    sbv = tmp_path/"in.sbvj01"
    out_sbv = tmp_path/"out.sbvj01"
    out_dump = tmp_path/"out.json"
    input_json.write_text(json.dumps({
        "name": "UnitTestPlayer",
        "version": 1,
        "data": {
            "uuid": "abc-123",
            "identity": {"name": "Alpha", "species": "human"}
        }
    }))

    rc = cli.main(["vjson-make", str(input_json), "-o", str(sbv)])
    assert rc == 0 and sbv.exists()

    # Edit identity.name -> Beta
    rc = cli.main(["vjson-edit", str(sbv), "--set", "identity.name=\"Beta\"", "-o", str(out_sbv)])
    assert rc == 0 and out_sbv.exists()

    # Apply JSON patch deep-merge
    patch = tmp_path/"patch.json"
    patch.write_text(json.dumps({
        "stats": {"skills": {"b": 2}, "mp": 50}
    }))
    rc = cli.main(["vjson-edit", str(out_sbv), "--patch", str(patch), "-o", str(out_sbv)])
    assert rc == 0

    # Dump and verify change
    rc = cli.main(["vjson-dump", str(out_sbv), "-o", str(out_dump)])
    assert rc == 0 and out_dump.exists()
    data = json.loads(out_dump.read_text())
    assert data["data"]["identity"]["name"] == "Beta"
    # Deep-merge preserved unknown key and added nested fields
    data_stats = data["data"].setdefault("stats", {})
    # Our test data did not include stats initially; patch should add it
    assert data_stats.get("mp") == 50
    assert data_stats.get("skills", {}).get("b") == 2

    # Append tags using --append
    rc = cli.main(["vjson-edit", str(out_sbv), "--append", "tags=\"t1\"", "--append", "tags=\"t2\"", "-o", str(out_sbv)])
    assert rc == 0

    # player-info should see updated name
    rc = cli.main(["player-info", str(out_sbv), "--json"])
    assert rc == 0
    out = capsys.readouterr().out
    info = json.loads(out)
    assert info["name"] == "Beta" and info["uuid"] == "abc-123"

    # Dump again and verify tags appended
    rc = cli.main(["vjson-dump", str(out_sbv), "-o", str(out_dump)])
    assert rc == 0
    data = json.loads(out_dump.read_text())
    assert data["data"].get("tags") == ["t1","t2"]
