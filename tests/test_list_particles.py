import awkward as ak

from atlas_mc_scanner import list_particles, common


def test_summarize_particles(monkeypatch):
    fake_data = ak.Array({"pdgid": [[13, 13], [22], []]})

    monkeypatch.setattr(common, "deliver", lambda *a, **k: "dummy")
    monkeypatch.setattr(common, "to_awk", lambda result: {"atlas-mc-scanner": fake_data})

    monkeypatch.setattr(
        list_particles,
        "get_particle_name",
        lambda pid: {13: "mu-", 22: "gamma"}.get(pid, f"Unknown ({pid})"),
    )

    summaries = list_particles.summarize_particles("rucio://scope:name")

    expected = [
        list_particles.ParticleSummary(
            pdgid=13,
            name="mu-",
            count=2,
            avg_per_event=2 / 3,
            max_per_event=2,
            min_per_event=0,
        ),
        list_particles.ParticleSummary(
            pdgid=22,
            name="gamma",
            count=1,
            avg_per_event=1 / 3,
            max_per_event=1,
            min_per_event=0,
        ),
    ]

    assert summaries == expected
