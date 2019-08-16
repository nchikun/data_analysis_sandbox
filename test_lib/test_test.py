from mock import Mock


def test_mysum():
    m = Mock()
    m.return_value = 3
    m()