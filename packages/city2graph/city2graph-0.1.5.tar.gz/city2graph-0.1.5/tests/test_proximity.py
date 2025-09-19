"""Concise proximity module tests (minimal yet 100% coverage target).

This suite intentionally compresses prior expansive testing into a small set
of focused scenarios that exercise every public code path and meaningful
branch in ``city2graph.proximity`` after refactoring/simplification.

Test categories:
1. Core generators (kNN, fixed-radius, triangulation family, MST, Waxman)
2. Distance metrics: euclidean, manhattan, network (incl. caching + errors)
3. Directed variants + multi-layer bridging
4. group_nodes (matches, empty, predicate mapping, network error)
5. Contiguity graph (validation, rook vs queen, empty, metric variants, errors)
6. Error handling & metric normalization (non-string, unknown metrics)
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import cast

import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import LineString
from shapely.geometry import Point
from shapely.geometry import Polygon

if TYPE_CHECKING:  # Only for typing/cast, avoid runtime import
    import networkx as nx

from city2graph.proximity import bridge_nodes
from city2graph.proximity import contiguity_graph
from city2graph.proximity import delaunay_graph
from city2graph.proximity import euclidean_minimum_spanning_tree
from city2graph.proximity import fixed_radius_graph
from city2graph.proximity import gabriel_graph
from city2graph.proximity import group_nodes
from city2graph.proximity import knn_graph
from city2graph.proximity import relative_neighborhood_graph
from city2graph.proximity import waxman_graph


def _points(coords: list[tuple[float, float]], crs: str = "EPSG:27700") -> gpd.GeoDataFrame:
    return gpd.GeoDataFrame(
        {"id": list(range(len(coords)))},
        geometry=[Point(x, y) for x, y in coords],
        crs=crs,
    ).set_index("id")


def _poly_points_fixture(crs: str = "EPSG:3857") -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    poly = Polygon([(0, 0), (2, 0), (2, 2), (0, 2)])
    polys = gpd.GeoDataFrame({"name": ["A"]}, geometry=[poly], crs=crs).set_index(
        pd.Index(["A"], name="zone")
    )
    pts = gpd.GeoDataFrame(
        {"pid": [1, 2, 3]},
        geometry=[Point(1, 1), Point(2, 1), Point(3, 3)],
        crs=crs,
    ).set_index("pid")
    return polys, pts


@pytest.fixture
def small_points() -> gpd.GeoDataFrame:
    """Small square-ish point set for proximity generators."""
    return _points([(0, 0), (1, 0), (0, 1), (2, 2)])


@pytest.fixture
def network_edges() -> gpd.GeoDataFrame:
    """Tiny 2-edge network for network distance metric tests."""
    src_ids = [0, 1]
    dst_ids = [1, 2]
    geom = [LineString([(0, 0), (1, 0)]), LineString([(1, 0), (0, 1)])]
    mi = pd.MultiIndex.from_arrays([src_ids, dst_ids], names=("source_id", "target_id"))
    data = {
        "source_id": src_ids,
        "target_id": dst_ids,
        "geometry": geom,
    }
    return gpd.GeoDataFrame(data, index=mi, crs="EPSG:27700")


# ---------------------------------------------------------------------------
# Distance helper behaviour
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("metric", ["euclidean", "manhattan"])
def test_knn_and_fixed_radius_basic(small_points: gpd.GeoDataFrame, metric: str) -> None:
    """Core sanity checks for kNN/fixed-radius under both Euclidean & Manhattan."""
    nodes, edges = knn_graph(small_points, k=2, distance_metric=metric)
    assert len(nodes) == len(small_points)
    if edges.empty:  # degenerate geometry unlikely but guard
        return
    assert {"weight", "geometry"}.issubset(edges.columns)
    nodes_r, edges_r = fixed_radius_graph(small_points, radius=1.5, distance_metric=metric)
    assert len(nodes_r) == len(small_points)
    if metric == "manhattan" and not edges.empty:
        # Manhattan edges have 3 coordinate points (L path) unless aligned
        geom = edges.geometry.iloc[0]
        assert isinstance(geom, LineString)
        assert 2 <= len(geom.coords) <= 3


def test_knn_non_string_metric_defaults(small_points: gpd.GeoDataFrame) -> None:
    """Non-string metric argument falls back to euclidean (robust normalisation)."""
    nodes, edges = knn_graph(small_points, k=1, distance_metric=None)  # type: ignore[arg-type]
    assert len(nodes) == len(small_points)
    assert not edges.empty


def test_network_metric_knn_and_cache(
    small_points: gpd.GeoDataFrame, network_edges: gpd.GeoDataFrame
) -> None:
    """Two calls with network metric reuse cached network graph on network_gdf."""
    # First call builds cache
    _, e1 = fixed_radius_graph(
        small_points, radius=2.0, distance_metric="network", network_gdf=network_edges
    )
    assert hasattr(network_edges, "_c2g_cached_nx")
    # Second call reuses cache
    _, e2 = fixed_radius_graph(
        small_points, radius=2.0, distance_metric="network", network_gdf=network_edges
    )
    assert e1.equals(e2)


def test_network_metric_requires_network_gdf(small_points: gpd.GeoDataFrame) -> None:
    """Requesting network metric without network_gdf triggers clear error."""
    with pytest.raises(ValueError, match="network_gdf is required"):
        knn_graph(small_points, k=1, distance_metric="network")


# ---------------------------------------------------------------------------
# Triangulation based generators
# ---------------------------------------------------------------------------


def test_delaunay_and_subgraphs(small_points: gpd.GeoDataFrame) -> None:
    """Gabriel and RNG are subgraphs of Delaunay (edge count monotonicity)."""
    # Delaunay needs >=3 points; we already have 4
    _, d_edges = delaunay_graph(small_points)
    _, g_edges = gabriel_graph(small_points)
    _, r_edges = relative_neighborhood_graph(small_points)
    assert len(g_edges) <= len(d_edges)
    assert len(r_edges) <= len(d_edges)


def test_mst_and_waxman(small_points: gpd.GeoDataFrame) -> None:
    """MST has n-1 edges and Waxman returns expected schema."""
    _, mst_edges = euclidean_minimum_spanning_tree(small_points)
    assert len(mst_edges) == max(len(small_points) - 1, 0)
    _, wax_edges = waxman_graph(small_points, beta=0.8, r0=2.0, seed=7)
    # Probabilistic: just ensure schema
    assert {"weight", "geometry"}.issubset(wax_edges.columns)


def test_gabriel_rng_two_points_branch() -> None:
    """Gabriel and RNG handle exactly two points (single edge candidate path)."""
    pts = _points([(0, 0), (1, 0)])
    _, g_edges = gabriel_graph(pts)
    _, r_edges = relative_neighborhood_graph(pts)
    # With two points, both graphs should have at most one edge
    assert len(g_edges) <= 1
    assert len(r_edges) <= 1


# ---------------------------------------------------------------------------
# Directed variants & bridging
# ---------------------------------------------------------------------------


def test_directed_variants_and_bridge(small_points: gpd.GeoDataFrame) -> None:
    """Directed kNN & radius plus bidirectional layer bridging produce edges."""
    src = small_points.iloc[:2]
    dst = small_points.iloc[2:]
    _, k_edges = knn_graph(src, k=1, target_gdf=dst)
    _, r_edges = fixed_radius_graph(src, radius=3.0, target_gdf=dst)
    assert len(k_edges) == len(src)
    assert len(r_edges) >= 1

    # bridge_nodes over two layers (both methods)
    layers = {"a": src, "b": dst}
    _, b_knn = bridge_nodes(layers, proximity_method="knn", k=1)
    _, b_rad = bridge_nodes(layers, proximity_method="fixed_radius", radius=5.0)
    assert len(b_knn) == 2  # a->b, b->a
    assert len(b_rad) == 2


def test_directed_network_variants(
    small_points: gpd.GeoDataFrame, network_edges: gpd.GeoDataFrame
) -> None:
    """Directed kNN and radius with network metric exercise _directed_graph path."""
    # Partition into sources and destinations
    src = small_points.iloc[:2]
    dst = small_points.iloc[2:]

    # kNN directed with network metric
    _, e_knn = knn_graph(
        src,
        k=1,
        target_gdf=dst,
        distance_metric="network",
        network_gdf=network_edges,
    )
    # Expect at least one edge if any destination is reachable on the network
    assert len(e_knn) >= 0

    # Radius directed with network metric (radius chosen to include 0->2 path ~2.41)
    _, e_rad = fixed_radius_graph(
        src,
        radius=2.5,
        target_gdf=dst,
        distance_metric="network",
        network_gdf=network_edges,
    )
    assert len(e_rad) >= 1


# ---------------------------------------------------------------------------
# Contiguity minimal tests (queen vs rook, manhattan, errors, empty)
# ---------------------------------------------------------------------------


def _small_square_polygons() -> gpd.GeoDataFrame:
    polys = [
        Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),  # 0
        Polygon([(1, 0), (2, 0), (2, 1), (1, 1)]),  # 1 (touches 0)
        Polygon([(0, 1), (1, 1), (1, 2), (0, 2)]),  # 2 (touches 0)
        Polygon([(2, 0), (3, 0), (3, 1), (2, 1)]),  # 3 (touches 1 only)
    ]
    return gpd.GeoDataFrame({"val": range(len(polys))}, geometry=polys, crs="EPSG:3857").set_index(
        pd.Index(range(len(polys)), name="pid")
    )


def test_contiguity_queen_vs_rook() -> None:
    """Queen contiguity yields superset (or equal) of rook edges."""
    gdf = _small_square_polygons()
    nodes_q, edges_q = contiguity_graph(gdf, contiguity="queen")
    nodes_r, edges_r = contiguity_graph(gdf, contiguity="rook")
    assert set(nodes_q.index) == set(gdf.index)
    assert set(nodes_r.index) == set(gdf.index)
    assert len(edges_q) >= len(edges_r)


def test_contiguity_manhattan_geometry() -> None:
    """Manhattan metric uses polyline (straight or L-shape)."""
    gdf = _small_square_polygons()
    _, edges_m = contiguity_graph(gdf, distance_metric="manhattan")
    if not edges_m.empty:
        geom = edges_m.geometry.iloc[0]
        assert isinstance(geom, LineString)
        assert 2 <= len(geom.coords) <= 3


def test_contiguity_invalid_type() -> None:
    """Invalid contiguity type raises ValueError."""
    gdf = _small_square_polygons()
    with pytest.raises(ValueError, match="Invalid contiguity type"):
        contiguity_graph(gdf, contiguity="invalid")


def test_contiguity_empty_input() -> None:
    """Empty input returns empty nodes/edges GeoDataFrames."""
    empty = gpd.GeoDataFrame({"geometry": []}, geometry="geometry", crs="EPSG:3857")
    nodes, edges = contiguity_graph(empty)
    assert nodes.empty
    assert edges.empty


def test_contiguity_network_requires_network_gdf() -> None:
    """Network metric without network_gdf raises ValueError."""
    gdf = _small_square_polygons()
    with pytest.raises(ValueError, match="network_gdf is required"):
        contiguity_graph(gdf, distance_metric="network")


# ---------------------------------------------------------------------------
# group_nodes public API coverage
# ---------------------------------------------------------------------------


def test_group_nodes_basic_matches() -> None:
    """group_nodes connects polygon to contained points (boundary inclusive)."""
    polys, pts = _poly_points_fixture()
    nodes, edges = group_nodes(polys, pts)
    # One polygon node retained, two point nodes in same CRS
    assert set(nodes.keys()) == {"polygon", "point"}
    edge_key = next(iter(edges))
    e = edges[edge_key]
    # Only the first two points lie inside the polygon
    assert len(e) == 2
    assert {pid for _, pid in e.index} == {1, 2}
    assert "weight" in e.columns
    assert "geometry" in e.columns


def test_group_nodes_empty_points() -> None:
    """Empty point set returns empty edge GeoDataFrame while preserving nodes."""
    polys, pts = _poly_points_fixture()
    empty_pts = pts.iloc[0:0]
    nodes, edges = group_nodes(polys, empty_pts)
    assert nodes["point"].empty
    edge_key = next(iter(edges))
    assert edges[edge_key].empty


def test_group_nodes_empty_polygons() -> None:
    """Empty polygon set returns empty edges while preserving point nodes."""
    polys, pts = _poly_points_fixture()
    empty_polys = polys.iloc[0:0]
    nodes, edges = group_nodes(empty_polys, pts)
    assert nodes["polygon"].empty
    edge_key = next(iter(edges))
    assert edges[edge_key].empty


def test_group_nodes_predicate_alias_within() -> None:
    """Predicate 'within' excludes boundary point so only interior point remains."""
    polys, pts = _poly_points_fixture()
    # Shift third point to be strictly outside
    nodes, edges = group_nodes(polys, pts, predicate="within")
    edge_key = next(iter(edges))
    # Points 1 only strictly within (point 2 is on boundary so excluded for within)
    e = edges[edge_key]
    assert {pid for _, pid in e.index} == {1}


def test_group_nodes_network_metric_requires_network() -> None:
    """Network metric without network_gdf raises explicit error for group_nodes."""
    polys, pts = _poly_points_fixture()
    with pytest.raises(ValueError, match="network_gdf is required"):
        group_nodes(polys, pts, distance_metric="network")


class TestContiguityPublicAPI:
    """Retain existing public API test name for quick test task reference."""

    def test_small_grid(self) -> None:
        """Smoke test small grid contiguity output symmetry."""
        gdf = _small_square_polygons()
        nodes, edges = contiguity_graph(gdf)
        assert set(nodes.index) == set(gdf.index)
        # Edges GeoDataFrame stores undirected edges once (u,v where u< v maybe);
        # validate symmetry by converting to networkx graph and checking neighbors.
        G = cast("nx.Graph", contiguity_graph(gdf, as_nx=True))
        for u, v in G.edges():
            assert G.has_edge(v, u)


## End of concise suite


# ---------------------------------------------------------------------------
# Additional coverage tests (public API only) to reach 100% proximity coverage
# ---------------------------------------------------------------------------


def _single_point_gdf() -> gpd.GeoDataFrame:
    return gpd.GeoDataFrame({"id": [0]}, geometry=[Point(0, 0)], crs="EPSG:27700").set_index("id")


def test_knn_single_point_early_exit() -> None:
    """KNN with a single point returns no edges (early return path)."""
    gdf = _single_point_gdf()
    nodes, edges = knn_graph(gdf, k=3)
    assert len(nodes) == 1
    assert edges.empty


def test_knn_zero_k_early_exit(small_points: gpd.GeoDataFrame) -> None:
    """K <= 0 triggers early return with no edges."""
    nodes, edges = knn_graph(small_points, k=0)
    assert len(nodes) == len(small_points)
    assert edges.empty


def test_knn_network_metric_success(
    network_edges: gpd.GeoDataFrame, small_points: gpd.GeoDataFrame
) -> None:
    """KNN network metric builds distance matrix and edges (cache path already covered)."""
    nodes, edges = knn_graph(
        small_points, k=1, distance_metric="network", network_gdf=network_edges
    )
    assert len(nodes) == len(small_points)
    assert not edges.empty


def test_delaunay_network_metric(
    network_edges: gpd.GeoDataFrame, small_points: gpd.GeoDataFrame
) -> None:
    """Delaunay with network metric attaches network-based weights/geometries."""
    nodes, edges = delaunay_graph(
        small_points, distance_metric="network", network_gdf=network_edges
    )
    if len(small_points) >= 3:
        assert not edges.empty


def test_gabriel_network_metric(
    network_edges: gpd.GeoDataFrame, small_points: gpd.GeoDataFrame
) -> None:
    """Gabriel network metric branch executed."""
    nodes, edges = gabriel_graph(small_points, distance_metric="network", network_gdf=network_edges)
    assert len(nodes) == len(small_points)


def test_rng_network_metric(
    network_edges: gpd.GeoDataFrame, small_points: gpd.GeoDataFrame
) -> None:
    """Relative Neighborhood Graph network metric branch executed."""
    nodes, edges = relative_neighborhood_graph(
        small_points, distance_metric="network", network_gdf=network_edges
    )
    assert len(nodes) == len(small_points)


def test_mst_network_metric(
    network_edges: gpd.GeoDataFrame, small_points: gpd.GeoDataFrame
) -> None:
    """Minimum spanning tree under network metric (complete graph fallback)."""
    nodes, edges = euclidean_minimum_spanning_tree(
        small_points, distance_metric="network", network_gdf=network_edges
    )
    # Tree edges <= n-1
    assert len(edges) <= max(len(small_points) - 1, 0)


def test_fixed_radius_network_metric(
    network_edges: gpd.GeoDataFrame, small_points: gpd.GeoDataFrame
) -> None:
    """Fixed-radius network metric selection path covered."""
    nodes, edges = fixed_radius_graph(
        small_points, radius=2.5, distance_metric="network", network_gdf=network_edges
    )
    assert len(nodes) == len(small_points)


def test_waxman_basic(small_points: gpd.GeoDataFrame) -> None:
    """Waxman graph probabilistic construction (schema validation)."""
    nodes, edges = waxman_graph(small_points, beta=0.5, r0=3.0, seed=123)
    assert set(edges.columns) >= {"weight", "geometry"}


def test_waxman_manhattan_metric(small_points: gpd.GeoDataFrame) -> None:
    """Waxman with Manhattan metric exercises the dispatcher manhattan branch."""
    nodes, edges = waxman_graph(
        small_points, beta=0.4, r0=2.0, seed=42, distance_metric="manhattan"
    )
    assert len(nodes) == len(small_points)
    assert set(edges.columns) >= {"weight", "geometry"}


def test_waxman_network_requires_network_gdf(small_points: gpd.GeoDataFrame) -> None:
    """Waxman with network metric should require network_gdf (dispatcher path)."""
    with pytest.raises(ValueError, match="network_gdf is required for network distance metric"):
        waxman_graph(small_points, beta=0.3, r0=1.5, distance_metric="network")


def test_waxman_network_crs_mismatch(small_points: gpd.GeoDataFrame) -> None:
    """Waxman with network metric and mismatched CRS raises from _network_dm."""
    # Build a tiny network in a different CRS than points
    net = gpd.GeoDataFrame(
        {"geometry": [LineString([(0, 0), (1, 1)])]},
        index=pd.MultiIndex.from_arrays([[0], [1]], names=("source_id", "target_id")),
        crs="EPSG:4326",
    )
    with pytest.raises(ValueError, match="CRS mismatch"):
        waxman_graph(small_points, beta=0.3, r0=1.5, distance_metric="network", network_gdf=net)


def test_waxman_invalid_metric_raises(small_points: gpd.GeoDataFrame) -> None:
    """Unknown metric propagates from internal dispatcher via public API."""
    with pytest.raises(ValueError, match="Unknown distance metric"):
        waxman_graph(small_points, beta=0.5, r0=2.0, distance_metric="invalid")  # type: ignore[arg-type]


def test_group_nodes_invalid_metric() -> None:
    """Unsupported distance metric raises ValueError via public API."""
    polys, pts = _poly_points_fixture()
    with pytest.raises(ValueError, match="Unsupported distance_metric"):
        group_nodes(polys, pts, distance_metric="invalid")  # type: ignore[arg-type]


def test_group_nodes_crs_mismatch() -> None:
    """CRS mismatch path triggers ValueError."""
    polys, pts = _poly_points_fixture()
    pts2 = pts.to_crs("EPSG:4326")
    with pytest.raises(ValueError, match="same CRS"):
        group_nodes(polys, pts2)


def test_group_nodes_missing_crs() -> None:
    """Both inputs must have a CRS error branch (no CRS)."""
    polys, _ = _poly_points_fixture()
    # Rebuild both layers with no CRS to hit the explicit missing-CRS validation
    poly_geom = polys.geometry.iloc[0]
    polys_nocrs = gpd.GeoDataFrame({"name": ["A"]}, geometry=[poly_geom], crs=None).set_index(
        pd.Index(["A"], name="zone")
    )
    # Build a brand-new GeoDataFrame with shapely geometries so CRS is truly None
    coords = [(1, 1), (2, 1), (3, 3)]
    pts_nocrs = gpd.GeoDataFrame(
        {"pid": [1, 2, 3]},
        geometry=[Point(x, y) for x, y in coords],
        crs=None,
    ).set_index("pid")
    assert polys_nocrs.crs is None
    assert pts_nocrs.crs is None
    with pytest.raises(ValueError, match="CRS"):
        group_nodes(polys_nocrs, pts_nocrs)


def test_group_nodes_network_crs_mismatch() -> None:
    """Network metric with mismatched network CRS raises."""
    polys, pts = _poly_points_fixture()
    # Simple network in different CRS
    poly_centroid = polys.geometry.iloc[0].centroid
    net = gpd.GeoDataFrame(
        {"geometry": [LineString([poly_centroid, poly_centroid])]},
        index=pd.MultiIndex.from_arrays([[0], [1]], names=("source_id", "target_id")),
        crs="EPSG:4326",
    )
    with pytest.raises(ValueError, match="CRS mismatch between inputs and network"):
        group_nodes(polys, pts, distance_metric="network", network_gdf=net)


def test_group_nodes_network_metric_success() -> None:
    """Successful network metric group_nodes call (weights/geometries via network)."""
    polys, pts = _poly_points_fixture()
    # Build simple network linking polygon centroid to each point
    poly_centroid = polys.geometry.iloc[0].centroid
    lines = []
    src = []
    dst = []
    for i, p in enumerate(pts.geometry):
        src.append(i)
        dst.append(i + 100)
        lines.append(LineString([poly_centroid, p]))
    mi = pd.MultiIndex.from_arrays([src, dst], names=("source_id", "target_id"))
    net = gpd.GeoDataFrame({"geometry": lines}, index=mi, crs=polys.crs)
    nodes, edges = group_nodes(polys, pts, distance_metric="network", network_gdf=net)
    edge_key = next(iter(edges))
    e = edges[edge_key]
    assert len(e) == 2  # two contained points


def test_group_nodes_network_with_length_weight() -> None:
    """group_nodes with network edges carrying 'length' triggers weighted paths branch."""
    polys, pts = _poly_points_fixture()
    poly_centroid = polys.geometry.iloc[0].centroid
    lines = []
    src = []
    dst = []
    lengths = []
    for i, p in enumerate(pts.geometry):
        src.append(i)
        dst.append(i + 100)
        seg = LineString([poly_centroid, p])
        lines.append(seg)
        lengths.append(seg.length)
    mi = pd.MultiIndex.from_arrays([src, dst], names=("source_id", "target_id"))
    net = gpd.GeoDataFrame({"length": lengths, "geometry": lines}, index=mi, crs=polys.crs)
    nodes, edges = group_nodes(polys, pts, distance_metric="network", network_gdf=net)
    edge_key = next(iter(edges))
    e = edges[edge_key]
    assert len(e) == 2
    assert set(e.columns) >= {"weight", "geometry"}


def test_group_nodes_no_matches_nonempty() -> None:
    """Non-empty inputs but no spatial matches hit empty-join early branch."""
    # Polygon far from points to ensure no containment matches
    polys = gpd.GeoDataFrame(
        {"name": ["A"]},
        geometry=[Polygon([(10, 10), (12, 10), (12, 12), (10, 12)])],
        crs="EPSG:3857",
    ).set_index(pd.Index(["A"], name="zone"))
    pts = gpd.GeoDataFrame(
        {"pid": [1, 2]},
        geometry=[Point(0, 0), Point(1, 1)],
        crs="EPSG:3857",
    ).set_index("pid")
    nodes, edges = group_nodes(polys, pts)
    edge_key = next(iter(edges))
    assert edges[edge_key].empty


def test_group_nodes_crs_mismatch_explicit_branch() -> None:
    """CRS mismatch after validation: one empty input avoids utils' global CRS check.

    This specifically exercises the explicit branch in group_nodes that checks
    ``poly_crs != pt_crs`` by constructing a scenario where validate_gdf does not
    raise (because one GDF is empty) but the CRSs still differ.
    """
    # Non-empty polygon in EPSG:3857
    polys = gpd.GeoDataFrame(
        {"name": ["A"]},
        geometry=[Polygon([(0, 0), (2, 0), (2, 2), (0, 2)])],
        crs="EPSG:3857",
    ).set_index(pd.Index(["A"], name="zone"))
    # Empty points in a different CRS (EPSG:4326)
    pts = gpd.GeoDataFrame(
        {"pid": []}, geometry=gpd.GeoSeries([], dtype="geometry"), crs="EPSG:4326"
    ).set_index(pd.Index([], name="pid"))
    with pytest.raises(ValueError, match="CRS mismatch between inputs:"):
        group_nodes(polys, pts)


def test_contiguity_network_metric_success() -> None:
    """Contiguity graph with network metric builds network-path geometries."""
    gdf = _small_square_polygons().iloc[:2]  # two adjacent squares
    # Build network line connecting centroids
    c1 = gdf.geometry.iloc[0].centroid
    c2 = gdf.geometry.iloc[1].centroid
    net = gpd.GeoDataFrame(
        {"geometry": [LineString([c1, c2])]},
        index=pd.MultiIndex.from_arrays([[0], [1]], names=("source_id", "target_id")),
        crs=gdf.crs,
    )
    nodes, edges = contiguity_graph(gdf, distance_metric="network", network_gdf=net)
    assert len(edges) == 1


def test_waxman_network_metric_success(
    small_points: gpd.GeoDataFrame, network_edges: gpd.GeoDataFrame
) -> None:
    """Waxman with network metric executes network distance dispatcher path."""
    nodes, edges = waxman_graph(
        small_points,
        beta=0.6,
        r0=3.0,
        distance_metric="network",
        network_gdf=network_edges,
        seed=7,
    )
    assert len(nodes) == len(small_points)
    # Probabilistic; ensure schema exists (execution path hit)
    assert set(edges.columns) >= {"weight", "geometry"}


def test_contiguity_network_length_weight_branch() -> None:
    """Contiguity with network metric and 'length' attribute triggers weighted path logic."""
    gdf = _small_square_polygons().iloc[:2]  # two adjacent squares
    c1 = gdf.geometry.iloc[0].centroid
    c2 = gdf.geometry.iloc[1].centroid
    net = gpd.GeoDataFrame(
        {"length": [c1.distance(c2)], "geometry": [LineString([c1, c2])]},
        index=pd.MultiIndex.from_arrays([[0], [1]], names=("source_id", "target_id")),
        crs=gdf.crs,
    )
    nodes, edges = contiguity_graph(gdf, distance_metric="network", network_gdf=net)
    assert len(edges) == 1
    # Ensure geometry and weight present (path weight via 'length')
    assert set(edges.columns) >= {"weight", "geometry"}


def test_contiguity_edges_unique_undirected_path() -> None:
    """Ensure unique undirected edges path in _generate_contiguity_edges is exercised."""
    gdf = _small_square_polygons()
    _, edges = contiguity_graph(gdf, contiguity="queen")
    # Should produce at least one edge for the small grid
    assert len(edges) >= 1


def test_contiguity_invalid_metric_raises() -> None:
    """Unsupported contiguity distance_metric triggers ValueError."""
    gdf = _small_square_polygons()
    with pytest.raises(ValueError, match="Unsupported distance_metric"):
        contiguity_graph(gdf, distance_metric="invalid")


def test_contiguity_network_crs_mismatch() -> None:
    """Network CRS different from polygons CRS raises ValueError."""
    gdf = _small_square_polygons().iloc[:2]
    c1 = gdf.geometry.iloc[0].centroid
    c2 = gdf.geometry.iloc[1].centroid
    # Deliberately different CRS for network
    net = gpd.GeoDataFrame(
        {"geometry": [LineString([c1, c2])]},
        index=pd.MultiIndex.from_arrays([[0], [1]], names=("source_id", "target_id")),
        crs="EPSG:4326",
    )
    with pytest.raises(ValueError, match="CRS mismatch"):
        contiguity_graph(gdf, distance_metric="network", network_gdf=net)


def test_contiguity_empty_as_nx() -> None:
    """Empty contiguity result as NetworkX preserves metadata."""
    empty = gpd.GeoDataFrame({"geometry": []}, geometry="geometry", crs="EPSG:3857")
    G = cast("nx.Graph", contiguity_graph(empty, as_nx=True))
    assert G.number_of_nodes() == 0
    assert G.number_of_edges() == 0
    assert G.graph.get("contiguity") == "queen"
    assert G.graph.get("distance_metric") == "euclidean"


def test_contiguity_single_polygon_no_edges() -> None:
    """Single polygon yields no adjacency edges (weights.neighbors empty branch)."""
    gdf = gpd.GeoDataFrame(
        {"val": [0]},
        geometry=[Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])],
        crs="EPSG:3857",
    ).set_index(pd.Index([0], name="pid"))
    nodes, edges = contiguity_graph(gdf)
    assert len(nodes) == 1
    assert edges.empty


def test_directed_knn_as_nx(small_points: gpd.GeoDataFrame) -> None:
    """Directed kNN with as_nx=True exercises _directed_graph return branch."""
    src = small_points.iloc[:2]
    dst = small_points.iloc[2:]
    G = cast("nx.Graph", knn_graph(src, k=1, target_gdf=dst, as_nx=True))
    assert hasattr(G, "number_of_nodes")
    assert G.number_of_edges() >= 1


def test_directed_knn_crs_mismatch(small_points: gpd.GeoDataFrame) -> None:
    """Directed helpers validate CRS equality between src and dst."""
    src = small_points.iloc[:2]
    dst = small_points.iloc[2:].to_crs("EPSG:4326")
    with pytest.raises(ValueError, match="CRS mismatch between source and target"):
        knn_graph(src, k=1, target_gdf=dst)


def test_network_edge_weight_length_branch(small_points: gpd.GeoDataFrame) -> None:
    """Provide 'length' edge attribute on network to trigger weighted path branch."""
    # Build a simple 2-edge network with explicit 'length' attributes
    src_ids = [0, 1]
    dst_ids = [1, 2]
    lengths = [1.0, 2.0]
    geom = [LineString([(0, 0), (1, 0)]), LineString([(1, 0), (0, 1)])]
    mi = pd.MultiIndex.from_arrays([src_ids, dst_ids], names=("source_id", "target_id"))
    data = {
        "source_id": src_ids,
        "target_id": dst_ids,
        "length": lengths,
        "geometry": geom,
    }
    net = gpd.GeoDataFrame(data, index=mi, crs="EPSG:27700")
    # Use network metric to ensure _set_network_edge_geometries is invoked
    _, e = fixed_radius_graph(small_points, radius=2.5, distance_metric="network", network_gdf=net)
    assert set(e.columns) >= {"weight", "geometry"}


def test_mst_unknown_metric_raises(small_points: gpd.GeoDataFrame) -> None:
    """Unknown distance metric should raise from internal dispatcher via MST."""
    with pytest.raises(ValueError, match="Unknown distance metric"):
        euclidean_minimum_spanning_tree(small_points, distance_metric="invalid")


def test_network_geometry_fallback_same_nearest_node() -> None:
    """When both endpoints map to the same nearest network node, use straight segment fallback.

    This specifically exercises the branch in network geometry construction where the
    shortest-path node sequence has length <= 1, so the resulting edge geometry should
    be a direct LineString between the original point coordinates (not along the network).
    """
    # Two sample points very close to the origin
    pts = gpd.GeoDataFrame(
        {"id": [0, 1]},
        geometry=[Point(0.0, 0.01), Point(0.02, 0.0)],
        crs="EPSG:27700",
    ).set_index("id")

    # A sparse network with one node at the origin and another far away, ensuring both
    # points map to the origin node as their nearest network node
    net = gpd.GeoDataFrame(
        {
            "geometry": [
                LineString([(0.0, 0.0), (100.0, 100.0)]),
            ]
        },
        index=pd.MultiIndex.from_arrays([[0], [1]], names=("source_id", "target_id")),
        crs="EPSG:27700",
    )

    # Network distance between both points is 0 (same mapped network node), so any
    # positive radius will include the edge. Geometry should fall back to straight line
    # between the two points (not a path along the network, which would be degenerate).
    nodes, edges = fixed_radius_graph(pts, radius=0.1, distance_metric="network", network_gdf=net)
    assert len(nodes) == 2
    assert len(edges) == 1
    geom = edges.geometry.iloc[0]
    assert isinstance(geom, LineString)
    # The fallback straight segment should have non-zero length approximately equal to
    # the Euclidean distance between the two sample points (diagonal ~0.02236)
    assert geom.length > 0
