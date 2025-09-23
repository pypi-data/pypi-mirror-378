from starbound import cli
import json

def test_vjson_roundtrip(tmp_path):
    obj = {"name":"UnitTestName","version":2,"data":{"k":"v","n":123}}
    jpath = tmp_path/"in.json"
    out_bin = tmp_path/"out.sbvj01"
    out_json = tmp_path/"out.json"
    jpath.write_text(json.dumps(obj))

    rc = cli.main(["vjson-make", str(jpath), "-o", str(out_bin)])
    assert rc == 0 and out_bin.exists()

    rc = cli.main(["vjson-dump", str(out_bin), "-o", str(out_json)])
    assert rc == 0 and out_json.exists()

    roundtrip = json.loads(out_json.read_text())
    assert roundtrip["name"] == obj["name"]
    assert roundtrip["version"] == obj["version"]
    assert roundtrip["data"] == obj["data"]
