from as_envhelper import load_env, get_env

def test_basic(tmp_path):
    f=tmp_path/".env"
    f.write_text('PORT=8080\nDEBUG=true\nSECRET="""multi\nline"""')
    load_env([str(f)])
    assert get_env("PORT")==8080
    assert get_env("DEBUG") is True
    assert "multi" in get_env("SECRET")
