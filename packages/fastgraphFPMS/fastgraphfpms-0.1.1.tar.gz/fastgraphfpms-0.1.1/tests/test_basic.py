def test_graph_display():
    from fastgraphFPMS import Graph
    m = [[0,1],[1,0]]
    g = Graph(m)
    s = g.display()
    assert "[[0, 1], [1, 0]]" in s
