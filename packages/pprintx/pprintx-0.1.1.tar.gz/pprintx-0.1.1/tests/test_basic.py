from pprintx import pprint, color

def test_basic_print(capsys):
    pprint << color(2) << "Green text"
    captured = capsys.readouterr()
    assert "Green text" in captured.out
