"""Cluster breaks that exploit the same weakness into unique findings.

Many mutated payloads are variations on one hole. Embed each break, cluster by
cosine similarity, and report unique vulnerabilities — not a raw, inflated
attack count.

Clustering is greedy nearest-centroid: at a few hundred breaks per campaign
that is exact and cheap; approximate NN (HNSW) is only worth it at far larger
scale. The embedder is injectable — the default is sentence-transformers, but
tests pass a stub so no model download is needed.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

from agent_red_team.contracts import Attempt, Finding

# Embed a batch of texts into vectors. Injected in tests; lazy real default.
Embedder = Callable[[Sequence[str]], list[list[float]]]


def _default_embedder(texts: Sequence[str]) -> list[list[float]]:
    from sentence_transformers import SentenceTransformer  # lazy: heavy import

    model = SentenceTransformer("all-MiniLM-L6-v2")
    return [list(map(float, v)) for v in model.encode(list(texts))]


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    if na == 0 or nb == 0:
        return 0.0
    return float(dot / (na * nb))


def dedupe(
    breaks: list[Attempt],
    *,
    embed: Embedder | None = None,
    threshold: float = 0.82,
) -> list[Finding]:
    """Group successful attempts into unique findings (one per weakness)."""
    if not breaks:
        return []
    embed = embed or _default_embedder
    vectors = embed([b.payload.text for b in breaks])

    # greedy clustering: each break joins the first centroid it is near enough to
    clusters: list[list[int]] = []
    centroids: list[list[float]] = []
    for i, vec in enumerate(vectors):
        placed = False
        for c, centroid in enumerate(centroids):
            if _cosine(vec, centroid) >= threshold:
                clusters[c].append(i)
                placed = True
                break
        if not placed:
            clusters.append([i])
            centroids.append(vec)

    return [_finding_from_cluster([breaks[i] for i in idxs]) for idxs in clusters]


def _finding_from_cluster(members: list[Attempt]) -> Finding:
    # representative = strongest break, ties broken by shortest payload
    rep = min(members, key=lambda a: (-a.verdict.score, len(a.payload.text)))
    proof = rep.verdict.proof.value if rep.verdict.proof else "unknown"
    ids = [m.payload.id for m in members if m.payload.id]
    return Finding(
        title=f"{rep.payload.family.value} injection via {rep.payload.target_surface} ({proof})",
        family=rep.payload.family,
        surface=rep.payload.target_surface,
        severity="high",
        minimal_payload=rep.payload.text,
        fix_hint="Separate tool-result data from instructions; never act on it.",
        example_attempt_ids=ids,
    )
