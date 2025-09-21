import io

import numpy as np

import homcloud.coupled_alpha_ext
from homcloud.coupled_alpha import CoupledAlphaShape
from homcloud.pdgm_format import PDGMReader


def test_for_2d_data():
    result = homcloud.coupled_alpha_ext.compute_2d(
        np.array([[0, 0], [1, 0], [0.5, 0.7]]),
        np.array([[0.02, 0.4], [1, 0.41], [0.5, -0.7]]),
    )
    assert set(s for s in result if len(s) == 4) == set([(0, 1, 2, 3), (0, 1, 3, 5), (1, 2, 3, 4), (1, 3, 4, 5)])
    assert len([s for s in result if len(s) == 4]) == 4
    assert len([s for s in result if len(s) == 3]) == 12
    assert len([s for s in result if len(s) == 2]) == 13
    assert len([s for s in result if len(s) == 1]) == 6


def test_for_3d_data():
    result = homcloud.coupled_alpha_ext.compute_3d(
        np.array([[0, 0, 0.001], [1, 0, 0.0001], [0.5, 0.7, 0.000001]]),
        np.array([[0.02, 0.4, -0.001], [1, 0.41, -0.0001], [0.5, -0.7, -0.000001]]),
    )
    # print(result)
    assert set(len(s) for s in result) == set([1, 2, 3, 4, 5])
    assert len([s for s in result if len(s) == 1]) == 6


class TestCoupledAlphaShape:
    def test_2d_case(self):
        coupled_alpha_shape = CoupledAlphaShape.build(
            np.array([[0, 0], [10, 0]]),
            np.array([[3, 1], [7, 2]]),
        )
        filt = coupled_alpha_shape.relative_ph_filtration(save_boundary_map=True)
        f = io.BytesIO()
        filt.compute_pdgm(f)
        f.seek(0)
        reader = PDGMReader(f)
        assert reader.metadata["dim"] == 2
        assert reader.metadata["filtration_type"] == "coupled-alpha-relative"

        births, deaths, ess_births = reader.load_pd_chunk("pd", 0)
        assert births == [0, 0]
        assert deaths == [10 / 4, 13 / 4]
        assert ess_births == []

        births, deaths, ess_births = reader.load_pd_chunk("pd", 1)
        assert births == [17 / 4]
        assert deaths == [100 / 4]
        assert ess_births == []

        assert ([], [], []) == reader.load_pd_chunk("pd", 2)

        assert (None, None, None) == reader.load_pd_chunk("pd", 3)

        births, deaths, ess_births = reader.load_pd_chunk("indexed_pd", 0)
        assert sorted(births) == [0, 1]

    def test_3d_case(self):
        coupled_alpha_shape = CoupledAlphaShape.build(
            np.array([[0, 0, 0.001], [1, 0, 0.0001], [0.5, 0.7, 0.000001]]),
            np.array([[0.02, 0.4, -0.001], [1, 0.41, -0.0001], [0.5, -0.7, -0.000001]]),
        )
        filt = coupled_alpha_shape.relative_ph_filtration(save_boundary_map=True)
        f = io.BytesIO()
        filt.compute_pdgm(f)
        f.seek(0)
        reader = PDGMReader(f)
        assert reader.metadata["dim"] == 3
        assert reader.metadata["filtration_type"] == "coupled-alpha-relative"
