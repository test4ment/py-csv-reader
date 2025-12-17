from .csvreader import CSVObject


def test_concat():
    a = CSVObject([{"a": 1, "b": 1}])
    b = CSVObject([{"a": 2, "b": 2}])
    
    c = a.concat(b)

    assert c._data == CSVObject([{"a": 1, "b": 1}, {"a": 2, "b": 2}])._data

def test_mean():
    a = CSVObject([
        {"a": 1},
        {"a": 2},
        {"a": 3},
        {"a": 4},
        {"a": 5},
    ])

    mean = a.query().mean("a")
    
    assert mean == 3.0

def test_groupby_agg():
    a = CSVObject([
        {"name": "Vasiliy", "mark": 5},
        {"name": "Jorji", "mark": 4},
        {"name": "Vasiliy", "mark": 4},
        {"name": "Evgeniy", "mark": 4},
        {"name": "Jorji", "mark": 3},
        {"name": "Vasiliy", "mark": 4},
        {"name": "Vasiliy", "mark": 4},
    ])

    means = a.query().groupbycolumn("name").mean("mark")

    assert means["Vasiliy"] == 17 / 4
    assert means["Jorji"] == 7 / 2
    assert means["Evgeniy"] == 4 / 1
    