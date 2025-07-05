from atlas_mc_scanner import find_containers


def test_execute_find_containers(monkeypatch):
    fake_output = "\n".join([
        "fooAuxDyn.pdgId",
        "something else",
        "barAuxDyn.pdgId",
    ])

    monkeypatch.setattr(find_containers, "get_structure", lambda *a, **k: fake_output)

    result = find_containers.execute_find_containers("dataset")

    expected = [
        find_containers.ContainerInfo(name="bar"),
        find_containers.ContainerInfo(name="foo"),
    ]

    assert result == expected
