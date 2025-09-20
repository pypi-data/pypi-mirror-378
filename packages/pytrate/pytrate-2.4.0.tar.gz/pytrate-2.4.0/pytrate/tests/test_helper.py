from unittest import TestCase
import arviz as az
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest
import xarray as xr

from pytrate import helper


class TestExpandSequences:
    def test_returns_df(self):
        series = pd.Series({"a": "NKT", "b": "NST", "c": "NTT"})
        assert isinstance(helper.expand_sequences(series), pd.DataFrame)

    def test_result_as_expected(self):
        series = pd.Series({"a": "NKT", "b": "NST", "c": "NTT"})
        expect = pd.DataFrame(
            {1: ["N", "N", "N"], 2: ["K", "S", "T"], 3: ["T", "T", "T"]},
            index=["a", "b", "c"],
        )
        assert (helper.expand_sequences(series) == expect).all().all()

    def test_index_correct(self):
        series = pd.Series({"a": "NKT", "b": "NST", "c": "NTT"})
        df = helper.expand_sequences(series)
        assert list(df.index) == ["a", "b", "c"]

    def test_columns_correct(self):
        series = pd.Series({"a": "NKT", "b": "NST", "c": "NTT"})
        df = helper.expand_sequences(series)
        assert list(df.columns) == [1, 2, 3]


class TestTiter:
    def test_titer_10(self):
        assert helper.Titer("10").log_value == 0

    def test_titer_10_int(self):
        """Should be able to pass an int."""
        assert helper.Titer(10).log_value == 0

    def test_titer_lt10(self):
        assert helper.Titer("<10").log_value == -1

    def test_titer_lt20(self):
        """The log value of <20 should be the log value of <10 +1."""
        assert helper.Titer("<20").log_value == (helper.Titer("<10").log_value + 1)

    def test_titer_lt10_leading_whitespace(self):
        assert helper.Titer(" <10").log_value == -1

    def test_titer_lt10_trailing_whitespace(self):
        assert helper.Titer("<10 ").log_value == -1

    def test_titer_lt10_central_whitespace(self):
        assert helper.Titer("< 10").log_value == -1

    def test_titer_gt10(self):
        with pytest.raises(NotImplementedError):
            assert helper.Titer(">10")

    def test_titer_40(self):
        assert helper.Titer("40").log_value == 2

    def test_intermediate_20_40(self):
        assert helper.Titer("20/40").log_value == 1.5

    def test_intermediate_40_80(self):
        assert helper.Titer("40/80").log_value == 2.5


class TestNDFactor(TestCase):
    def test_index_a_b(self):
        f = helper.NDFactor([("a", "b"), ("a", "c"), ("b", "c")])
        assert f.index(("a", "b")) == 0

    def test_index_a_c(self):
        f = helper.NDFactor([("a", "b"), ("a", "c"), ("b", "c")])
        assert f.index(("a", "c")) == 1

    def test_index_b_c(self):
        f = helper.NDFactor([("a", "b"), ("a", "c"), ("b", "c")])
        assert f.index(("b", "c")) == 2

    def test_make_index(self):
        f = helper.NDFactor([("a", "b"), ("a", "c"), ("b", "c")])
        df = pd.DataFrame([["a", "b"], ["a", "c"], ["b", "c"]])
        assert f.make_index(df) == [0, 1, 2]

    def test_labels(self):
        f = helper.NDFactor([("a", "b"), ("a", "c"), ("b", "c")])
        assert f.labels == ["a-b", "a-c", "b-c"]

    def test_labels_ints(self):
        f = helper.NDFactor([(1, 2), (1, 3), (2, 3)])
        assert f.labels == ["1-2", "1-3", "2-3"]


class TestFindGylcosylationSites(TestCase):
    def test_returns_list(self):
        """
        Should return a list of ints indicating the index of the first 'N' in the glycosylation
        motif.
        """
        assert helper.find_glycosylation_sites("ACDNNSD") == [3]

    def test_returns_empty_list(self):
        """Should return empty list if the sequence doesn't contain a glycosylation motif."""
        assert helper.find_glycosylation_sites("ACDNSD") == []

    def test_index(self):
        assert helper.find_glycosylation_sites("ACDNKSD")[0] == 3

    def test_X_is_proline(self):
        """Glycosylation motif is NX{ST}, where X is not proline."""
        assert helper.find_glycosylation_sites("ACDNPSD") == []

    def test_multiple(self):
        assert helper.find_glycosylation_sites("ANKTCGNSSP") == [1, 6]

    def test_overlapping(self):
        assert helper.find_glycosylation_sites("NNSS") == [0, 1]


class TestGlycosylationChanges(TestCase):
    def test_no_empty(self):
        assert list(helper.find_glycosylation_changes("", "")) == []

    def test_no_differences(self):
        assert list(helper.find_glycosylation_changes("AQCNKT", "AQCNKT")) == []

    def test_different_motifs(self):
        """Different motifs but at the same site."""
        assert list(helper.find_glycosylation_changes("AQCNKT", "AQCNRS")) == []

    def test_single_difference(self):
        assert len(list(helper.find_glycosylation_changes("AQCNKT", "AQCNKA"))) == 1

    def test_single_difference_site(self):
        gc = next(helper.find_glycosylation_changes("AQCNKT", "AQCNKA"))
        assert gc.site == 4

    def test_single_difference_sub(self):
        gc = next(helper.find_glycosylation_changes("AQCNKT", "AQCNKA"))
        assert gc.subs == ["T6A"]

    def test_single_difference_mut_motif(self):
        gc = next(helper.find_glycosylation_changes("AQCNKT", "AQCNKA"))
        assert gc.mut_motif == "NKA"

    def test_single_difference_root_motif(self):
        gc = next(helper.find_glycosylation_changes("AQCNKT", "AQCNKA"))
        assert gc.root_motif == "NKT"

    def test_multiple_subs_but_only_one_necessary(self):
        """K -> Q present, but only T -> necessary."""
        gc = next(helper.find_glycosylation_changes("NKT", "NQA"))
        assert gc.subs == ["T3A"]

    def test_single_difference_multiple_subs_gain_or_loss(self):
        gc = next(helper.find_glycosylation_changes("AQCNKT", "AQCNQA"))
        assert gc.gain_or_loss == "loss"


class TestSubsNecessaryForGlycChange(TestCase):
    def test_1(self):
        """Here, loss of T necessary to lose the glycosylation."""
        assert helper.subs_necessary_for_glyc_change("NKT", "NQA") == [("T", 2, "A")]

    def test_2(self):
        """
        Here both the T -> A and K -> P alone would be necessary and sufficient to result in a loss
        of glycosylation.
        """
        assert helper.subs_necessary_for_glyc_change("NKT", "NPA") == [
            ("K", 1, "P"),
            ("T", 2, "A"),
        ]

    def test_3(self):
        with pytest.raises(
            ValueError, match=r"No difference in glycosylation between NKT and NKS"
        ):
            helper.subs_necessary_for_glyc_change("NKT", "NKS")

    def test_1_reversed(self):
        assert helper.subs_necessary_for_glyc_change("NQA", "NKT") == [("A", 2, "T")]

    def test_2_reversed(self):
        """Here both subs are necessary for the gain. (Need to lose the P and gain the final T)."""
        with pytest.raises(NotImplementedError):
            helper.subs_necessary_for_glyc_change("NPA", "NKT")

    def test_3_reversed(self):
        with pytest.raises(ValueError):
            helper.subs_necessary_for_glyc_change("NKS", "NKT")

    def test_4(self):
        """Here, loss of N necessary to lose the glycosylation."""
        assert helper.subs_necessary_for_glyc_change("NKT", "AQT") == [("N", 0, "A")]

    def test_5(self):
        """Here all changes necessary."""
        with pytest.raises(NotImplementedError):
            helper.subs_necessary_for_glyc_change("APC", "NKT")

    def test_error_seqs_not_len_3(self):
        with pytest.raises(ValueError, match="sequences not len 3:"):
            helper.subs_necessary_for_glyc_change("ABCD", "NKT")


class TestFindSubstitutions(TestCase):
    def test_no_diffs(self):
        assert list(helper.find_substitutions("AKC", "AKC")) == []

    def test_one_diff(self):
        assert list(helper.find_substitutions("AKC", "ADC")) == ["K2D"]

    def test_multiple_diffs(self):
        assert list(helper.find_substitutions("AKC", "TDC")) == ["A1T", "K2D"]

    def test_diffs_at_start(self):
        assert list(helper.find_substitutions("AKC", "DKC")) == ["A1D"]

    def test_diffs_at_end(self):
        assert list(helper.find_substitutions("AKC", "AKD")) == ["C3D"]

    def test_diffs_at_start_and_end(self):
        assert list(helper.find_substitutions("AKC", "DKR")) == ["A1D", "C3R"]

    def test_glycosylation_gain(self):
        """If append_glyc_changes=True, then glycosylation gains should have '(+g)' appended."""
        subs = helper.find_substitutions("NKN", "NKT", append_glyc_changes=True)
        assert list(subs) == ["N3T+g"]

    def test_another_glycosylation_gain(self):
        """If append_glyc_changes=True, then glycosylation gains should have '(+g)' appended."""
        subs = helper.find_substitutions(
            "ABCDEFGNKNHIJK", "ABCDEFGNKSHIJR", append_glyc_changes=True
        )
        assert list(subs) == ["N10S+g", "K14R"]

    def test_glycosylation_loss(self):
        """If append_glyc_changes=True, then glycosylation losses should have '(g-)' appended."""
        subs = helper.find_substitutions("NKT", "NKN", append_glyc_changes=True)
        assert list(subs) == ["T3N-g"]

    def test_multiple_subs_necessary(self):
        """
        If multiple substitutions are necessary for the glyc change, a NotImplementedError should
        be raised.
        """
        with pytest.raises(NotImplementedError):
            list(helper.find_substitutions("AKR", "NKT", append_glyc_changes=True))

    def test_cant_pass_append_and_unify_glyc_changes(self):
        with pytest.raises(
            ValueError, match="append and unify glyc_changes can't both be True"
        ):
            list(
                helper.find_substitutions(
                    "NKT", "NKN", append_glyc_changes=True, unify_glyc_changes=True
                )
            )

    def test_unify_glyc_changes_loss(self):
        """
        Tests the behaviour of unify glyc changes.
        """
        subs = helper.find_substitutions("NKT", "NKN", unify_glyc_changes=True)
        assert list(subs) == ["1-g"]

    def test_unify_glyc_changes_loss_and_gain(self):
        """
        Test losing one glycosylation but gaining another.
        """
        subs = helper.find_substitutions(
            "GPNKTRRKS", "GPSKTRNKS", unify_glyc_changes=True
        )
        assert list(subs) == ["3-g", "7+g"]

    def test_sort_aas_with_append_glyc_changes_raises_error(self):
        """
        Should raise NotImplementedError if sort_aas and append_glyc_changes are
        both True.
        """
        msg = "sort_aas not implemented with append_glyc_changes or unify_glyc_changes"
        with pytest.raises(NotImplementedError, match=msg):
            list(
                helper.find_substitutions(
                    "NKT", "NKN", append_glyc_changes=True, sort_aas=True
                )
            )

    def test_sort_aas_with_unify_glyc_changes_raises_error(self):
        """
        Should raise NotImplementedError if sort_aas and unify_glyc_changes are
        both True.
        """
        msg = "sort_aas not implemented with append_glyc_changes or unify_glyc_changes"
        with pytest.raises(NotImplementedError, match=msg):
            list(
                helper.find_substitutions(
                    "NKT", "NKN", unify_glyc_changes=True, sort_aas=True
                )
            )

    def test_sort_aas(self):
        """
        Test that substitutions are returned with sorted amino acids when sort_aas=True.
        """
        assert list(helper.find_substitutions("AKC", "ADC", sort_aas=True)) == ["D2K"]

    def test_sort_aas_multiple_diffs(self):
        """
        Test multiple substitutions with sort_aas=True.
        """
        subs = set(helper.find_substitutions("AKC", "TDC", sort_aas=True))
        assert "A1T" in subs
        assert "D2K" in subs

    def test_sort_aas_preserves_position(self):
        """
        Test that sort_aas preserves the position of the substitution.
        """
        subs = list(helper.find_substitutions("ARC", "ADC", sort_aas=True))

        # D comes before R, so R2D becomes D2R
        assert subs == ["D2R"]

        # Position should still be the second character
        assert all(sub[1].isdigit() for sub in subs)

    def test_sort_aas_multiple_positions(self):
        """
        Test that sort_aas works with multiple positions.
        """
        subs = list(helper.find_substitutions("AKN", "TDS", sort_aas=True))
        assert "A1T" in subs
        assert "D2K" in subs
        assert "N3S" in subs  # N comes before S, so this stays the same

    def test_sort_aas_with_ignore_chars(self):
        """
        Test sort_aas with ignore_chars option.
        """
        # Only K2D becomes D2K, X3C is ignored
        subs = list(
            helper.find_substitutions("AKX", "ADC", sort_aas=True, ignore_chars={"X"})
        )
        assert subs == ["D2K"]


class TestSubstitutionComponents(TestCase):
    def test_sub_components_1(self):
        assert helper.sub_components("N145K") == (145, "N", "K")

    def test_sub_components_2(self):
        assert helper.sub_components("E1N") == (1, "E", "N")

    def test_glycosylation_loss_ignored(self):
        assert helper.sub_components("N145K(g-)") == (145, "N", "K")

    def test_glycosylation_gain_ignored(self):
        assert helper.sub_components("N145T(g+)") == (145, "N", "T")


class TestHdiScatter(TestCase):
    def test_returns_tuple(self):
        """
        Test that hdi_scatter_data returns a tuple.
        """
        # make idata with 4 chains of 100 samples each
        idata = az.from_dict(posterior={"var1": np.random.randn(4, 100)})
        result = helper.hdi_scatter_data(idata, "var1")
        assert isinstance(result, tuple)

    def test_mean_is_dataarray(self):
        """
        Test that the mean returned by hdi_scatter_data is a DataArray.
        """
        idata = az.from_dict(posterior={"var1": np.random.randn(4, 100)})
        mean, _ = helper.hdi_scatter_data(idata, "var1")
        assert isinstance(mean, xr.DataArray)

    def test_hdi_err_is_ndarray(self):
        """
        Test that the hdi_err returned by hdi_scatter_data is an ndarray.
        """
        idata = az.from_dict(posterior={"var1": np.random.randn(4, 100)})
        _, hdi_err = helper.hdi_scatter_data(idata, "var1")
        assert isinstance(hdi_err, np.ndarray)

    def test_hdi_err_shape(self):
        """
        Test that the hdi_err returned by hdi_scatter_data has the correct shape.
        """
        idata = az.from_dict(posterior={"var1": np.random.randn(4, 100)})
        _, hdi_err = helper.hdi_scatter_data(idata, "var1")
        assert hdi_err.shape == (2,)

    @pytest.mark.slow
    def test_plot_hdi_scatter(self):
        """
        Test that plot_hdi_scatter creates a plot without errors.
        """
        x_idata = az.from_dict(posterior={"var1": np.random.randn(4, 100, 50)})
        y_idata = az.from_dict(posterior={"var1": np.random.randn(4, 100, 50)})
        ax = plt.gca()
        result_ax = helper.plot_hdi_scatter(x_idata, "var1", y_idata, ax=ax)
        assert result_ax is ax

    def test_hdi_scatter_data_with_xarray_dataset(self):
        """
        Test that hdi_scatter_data can handle being passed an xarray.Dataset.
        """
        data = xr.DataArray(
            np.random.randn(4, 50, 200), dims=("chain", "draw", "var1"), name="x"
        )
        mean, hdi_err = helper.hdi_scatter_data(data)
        assert isinstance(mean, xr.DataArray)
        assert isinstance(hdi_err, np.ndarray)
        assert hdi_err.shape == (2, 200)


class TestIsSubstitution:
    def test_different_chars(self):
        """Should return True for different characters."""
        assert helper.is_substitution("A", "C")

    def test_same_chars(self):
        """Should return False for the same characters."""
        assert not helper.is_substitution("A", "A")

    def test_ignore_set(self):
        """Should return False if either character is in the ignore set."""
        assert not helper.is_substitution("A", "C", ignore={"A"})
        assert not helper.is_substitution("A", "C", ignore={"C"})
        assert not helper.is_substitution("A", "C", ignore={"A", "C"})

    def test_ignore_none(self):
        """Should handle ignore=None."""
        assert helper.is_substitution("A", "C", ignore=None)

    def test_empty_ignore_set(self):
        """Should return True for different characters with empty ignore set."""
        assert helper.is_substitution("A", "C", ignore=set())

    def test_special_characters(self):
        """Should work with special characters like gap or unknown."""
        assert helper.is_substitution("A", "-")
        assert helper.is_substitution("A", "X")
        assert not helper.is_substitution("A", "-", ignore={"-"})


class TestSeqsDifferByN:
    def test_identical_sequences(self):
        """Should return False for identical sequences when n=1."""
        assert not helper.sequences_differ_by_n("ABCD", "ABCD", n=1)

    def test_identical_sequences_n_zero(self):
        """Should return empty list when sequences are identical and n=0."""
        assert [] == helper.sequences_differ_by_n("ABCD", "ABCD", n=0)

    def test_single_substitution_with_custom_numbering(self):
        """Should return the substitution with custom numbering."""
        result = helper.sequences_differ_by_n(
            "ABCD", "AKCD", n=1, numbering_start=1, yield_tuples=True
        )
        assert result == [("B", 2, "K")]

    def test_unknown_aa_not_ignored(self):
        """'X' should not be ignored by default."""
        assert helper.sequences_differ_by_n("ABCD", "AXCD", n=1, numbering_start=1)

    def test_gap_not_ignored(self):
        """'-' should not be ignored by default."""
        assert helper.sequences_differ_by_n("ABCD", "A-CD", n=1, numbering_start=1)

    def test_n_too_small(self):
        """Should return False if sequences differ by more substitutions than n."""
        assert not helper.sequences_differ_by_n("AABB", "AAAA", n=1)

    def test_n_exact_match(self):
        """
        Should return a list of substitutions if sequences differ by exactly n
        substitutions.
        """
        assert isinstance(helper.sequences_differ_by_n("AABC", "AABD", n=1), list)

    def test_ignore_chars(self):
        """Should ignore specified characters when comparing."""
        assert not helper.sequences_differ_by_n("ABXD", "ABYD", n=0, ignore_chars={"X"})
