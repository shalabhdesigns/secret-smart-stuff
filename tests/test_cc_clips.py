from shorts.cc_clips import classify


def test_classify():
    assert classify("GTA 6 Trailer 2 LEAKS", "2026-08-01") == "never"
    assert classify("5 DETALLES de GTA 6", "2026-08-01") == "trailer-based"
    assert classify("GTA 6 funny police chase", "2026-11-21") == "gameplay"
    assert classify("How to Teleport Anywhere in GTA Online", "2026-11-21") == "never"
    assert classify("$1 to $1,000,000 car in GTA 5", "2026-10-01") == "gameplay"
