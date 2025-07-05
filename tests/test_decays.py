import awkward as ak

from atlas_mc_scanner import decays, common


def test_execute_decay(monkeypatch):
    fake_data = ak.Array(
        {
            "decay_pdgId": [[[13, 22], [13]], [[]]],
            "none_count": [0, 2],
        }
    )

    monkeypatch.setattr(common, "deliver", lambda *a, **k: "dummy")
    monkeypatch.setattr(common, "to_awk", lambda result: {"atlas-mc-scanner": fake_data})

    monkeypatch.setattr(decays, "get_pdgid_from_name_or_int", lambda name: 13)
    monkeypatch.setattr(
        decays,
        "get_particle_name",
        lambda pid: {13: "mu-", 22: "gamma"}.get(pid, f"Unknown ({pid})"),
    )

    summaries = decays.execute_decay("rucio://scope:name", "13")

    expected = [
        decays.DecaySummary(pdgids=None, decay_names="", count=2, fraction=0.4),
        decays.DecaySummary(
            pdgids=(13, 22),
            decay_names="mu- + gamma",
            count=1,
            fraction=0.2,
        ),
        decays.DecaySummary(pdgids=(13,), decay_names="mu-", count=1, fraction=0.2),
        decays.DecaySummary(pdgids=tuple(), decay_names="", count=1, fraction=0.2),
    ]

    assert summaries == expected
