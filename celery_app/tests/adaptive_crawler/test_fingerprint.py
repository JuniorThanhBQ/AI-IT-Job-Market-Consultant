from tools.adaptive_crawler.helpers import generate_session_fingerprint


def test_generate_session_fingerprint():
    fp1 = generate_session_fingerprint()
    fp2 = generate_session_fingerprint()

    for fp in (fp1, fp2):
        assert "user_agent" in fp
        assert isinstance(fp["user_agent"], str)
        assert len(fp["user_agent"]) > 0
        assert "viewport" in fp
        assert "width" in fp["viewport"] and "height" in fp["viewport"]
        assert fp["locale"] == "vi-VN"
        assert fp["timezone_id"] == "Asia/Ho_Chi_Minh"
        assert "extra_http_headers" in fp
        assert isinstance(fp["extra_http_headers"], dict)
