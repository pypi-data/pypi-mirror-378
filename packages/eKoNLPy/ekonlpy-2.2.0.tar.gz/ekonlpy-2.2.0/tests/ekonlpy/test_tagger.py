def test_tagger():
    from ekonlpy.tag import Mecab

    mecab = Mecab()
    text = "금통위는 따라서 물가안정과 병행, 경기상황에 유의하는 금리정책을 펼쳐나가기로 했다고 밝혔다."
    tokens = mecab.pos(text)
    print(tokens)
    ans = [
        ("금통위", "NNG"),
        ("는", "JX"),
        ("따라서", "MAJ"),
        ("물가", "NNG"),
        ("안정", "NNG"),
        ("과", "JC"),
        ("병행", "NNG"),
        (",", "SC"),
        ("경기", "NNG"),
        ("상황", "NNG"),
        ("에", "JKB"),
        ("유의", "NNG"),
        ("하", "XSV"),
        ("는", "ETM"),
        ("금리", "NNG"),
        ("정책", "NNG"),
        ("을", "JKO"),
        ("펼쳐", "VV"),
        ("나가", "VX"),
        ("기", "ETN"),
        ("로", "JKB"),
        ("했", "VV"),
        ("다고", "EC"),
        ("밝혔", "VV"),
        ("다", "EF"),
        (".", "SF"),
    ]
    assert tokens == ans

    mecab.add_dictionary("금통위", "NNG")


if __name__ == "__main__":
    test_tagger()
