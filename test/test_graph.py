from test.test_story import get_test_story

import numpy as np
import pytest
from PIL import Image

from storytime_ai import story


def test_plot(tmp_path):
    if not (story._graph and story._plot):
        pytest.skip("graph or plot not available")
    """Test that the graph can be plotted.
    The test checks that the image is not all white.
    """
    st = get_test_story()
    fname = tmp_path / "test.png"
    st.plot_graph(fname)
    img = np.asarray(Image.open(fname))
    assert (img - 255).any()


def test_subgraphs():
    if not (story._graph and story._plot):
        pytest.skip("graph or plot not available")
    st = get_test_story()
    assert not st.has_subgraphs()
    st.prune_dangling_choices()
    assert st.check_integrity()
    st.dialogs["nonsense"] = story.Dialog("nonsense", "nonsense", {})
    assert st.has_subgraphs()
    assert not st.check_integrity()


def test_restriction_to_largest_substory():
    st = get_test_story()
    assert not st.has_subgraphs()
    assert len(st.dialogs) == 3
    st.dialogs["nonsense"] = story.Dialog("nonsense", "nonsense", {})
    st.restrict_to_largest_substory()
    assert not st.has_subgraphs()
