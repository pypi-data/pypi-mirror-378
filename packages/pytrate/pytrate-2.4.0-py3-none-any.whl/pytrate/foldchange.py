"""
Fold change models work by decomposing differences in titers between mutants and their parent (or
_root_) viruses as a linear additive combination of the mutant's amino acid substitutions.

$$T_{m,s} = X \\beta + T_{r_m,s}$$

where:

- $T_{m,s}$ is the titer between a mutant ($m$) and serum ($s$).
- $T_{r_m,s}$ is the titer between the root used to make mutant $m$ ($r_m$) and serum ($s$).
- $X \\beta$ captures the linear additive combination of the substitutions ($X$) and the effect
  sizes of each substitution ($\\beta$).
"""

import re

import numpy as np
import pandas as pd
import pymc as pm

from pytensor import sparse, tensor

from . import helper


class FoldChangeModel:

    def __init__(
        self,
        df_root: pd.DataFrame,
        df_mut: pd.DataFrame,
        mutant_subs: dict[str, list[str]],
    ) -> None:
        """
        Args:
            df_root: DataFrame containing root titers. Index must be `'antigen'`. Columns must
                contain `"serum"` and `"log_titer"`. `"root"` must be present in the
                `df_root` index.
            df_mut: DataFrame containing root titers. Index must be `'antigen'`. Columns must
                contain `"serum"`, `"log_titer"` and `"root"`. Value of `"root"` must be present in
                the `df_root` index.
            mutant_subs: Dict that maps a mutant to its substitutions.
        """
        if df_mut.index.name != "antigen":
            raise ValueError("df_mut index must be named 'antigen'")

        if df_root.index.name != "antigen":
            raise ValueError("df_root index must be named 'antigen'")

        if missing := set(mutant_subs) - set(df_mut.index):
            raise ValueError(f"mutant(s) {missing} in mutant_subs missing from df_mut")

        if missing := set(df_mut.index) - set(mutant_subs):
            raise ValueError(f"mutant(s) {missing} in df_mut missing from mutant_subs")

        #: DataFrame containing root titers.
        self.df_root = df_root

        #: DataFrame containing mutant titers.
        self.df_mut = df_mut

        #: All root viruses
        self.roots = sorted(set(df_root.index))

        #: All individual mutants.
        self.mutants = sorted(set(df_mut.index))

        #: All (serum, root) combinations.
        self.root_sr_pairs = helper.NDFactor(df_root["serum"].items())

        #: All individual sera.
        self.sera = tuple(sorted(set(serum for _, serum in self.root_sr_pairs.values)))

        self.mutant_subs = mutant_subs

        #: Substitutions for each mutant merged such that any set of substitutions that always
        #: appear together are grouped. See `helper.merge_maximal_subgroup_subs` for details.
        self.mutant_subs_merged = helper.merge_maximal_subgroup_subs(mutant_subs)

        #: All individual substitutions.
        self.subs = tuple(sorted(set(helper.unpack(self.mutant_subs_merged.values()))))

        def gen_sub_serums():
            for ag, sr in (
                self.df_mut.reset_index()[["antigen", "serum"]].drop_duplicates().values
            ):
                yield from ((sub, sr) for sub in self.mutant_subs_merged[ag])

        self.sub_serum = helper.NDFactor(list(gen_sub_serums()))

        #: `np.ndarray` (n. mutant titrations, n. (sub, serum) combinations) encoding the
        #: substitutions this mutant has, and the sera that they are titrated against in each row of
        #: `df_mut`.
        self.X = np.zeros((len(df_mut), len(self.sub_serum)))
        for i, row in enumerate(df_mut.itertuples()):
            mutant = row.Index
            for sub in self.mutant_subs_merged[mutant]:
                j = self.sub_serum.index((sub, row.serum))
                self.X[i, j] = 1.0
        self.X = self.X.astype(int)

        #: Sparse representation of `X`.
        self.X_sparse = sparse.csr_from_dense(tensor.as_tensor(self.X))

        #: DataFrame version of `X`, with appropriate column and index.
        self.df_X = pd.DataFrame(
            self.X,
            index=self.df_mut.set_index("serum", append=True).index,
            columns=self.sub_serum.values,
        )

        #: Index mapping (root, serum) pairs to `df_root`.
        self.root_sr_idx = self.root_sr_pairs.make_index(
            df_root.reset_index()[["antigen", "serum"]]
        )

        #: Index mapping (serum) to `df_root`.
        self.root_perserum_idx = df_root["serum"].apply(self.sera.index).values

        #: Index mapping (root, serum) pairs to `df_mut`.
        self.root_idx = self.root_sr_pairs.make_index(df_mut[["root", "serum"]])

        #: Index mapping (sub, serum) pairs to substitutions in `subs`.
        self.sub_idx = [self.subs.index(sub) for sub, _ in self.sub_serum.values]

        independent_subs = set([sub for sub in self.subs if "+" not in sub])

        def site_from_sub(sub: str) -> int:
            return int(re.search(r"\w(\d+)\w", sub).groups()[0])

        #: All sites that occur in substitutions.
        self.sites = sorted(set(site_from_sub(sub) for sub in independent_subs)) + ["+"]

        #: Index mapping substitution sites to substitutions. If `sites_in_hierarchy` is used.
        #: All groups of substitutions that always occur together share a hyperprior.
        #: E.g. 'A127S', 'A127T', 'A127V', all share one prior distribution because they all occur
        #: at site 127. 'D124H+R145G', 'D124N+A263E', 'D237N+N273S' (and all other "subs" that are
        #: actually multiple substitutions that always occur together) also share one single
        #: (hyper) prior.
        self.site_idx = [
            (
                self.sites.index("+")
                if "+" in sub
                else self.sites.index(site_from_sub(sub))
            )
            for sub in self.subs
        ]

    def __repr__(self) -> str:
        return (
            f"FoldChangeModel(df_root={self.df_root}, df_mut={self.df_mut}, "
            f"mutant_subs={self.mutant_subs})"
        )

    def model(
        self,
        use_noncentered: bool = True,
        site_in_hierarchy: bool = False,
        student_t_b_sub_serum: bool = False,
        student_t_b_sub: bool = False,
        student_t_lik: bool = False,
    ) -> pm.Model:
        """
        PyMC model representation of the fold change model.

        Args:
            use_noncentered: Use non-centered parametrisations for normal distributions with
                hierarchical priors.
            site_in_hierarchy: Include sites in the model hierarchy.
            student_t_b_sub_serum: Use a Student-T distribution as the prior for b_sub_serum.
                If False, use a Normal.
            student_t_b_sub: Use a Student-T distribution as the prior for b_sub.
            student_t_lik: Use a Student-T distribution for the likelihood.
        """

        hierarchical_normal = (
            helper.hierarchical_noncentered_normal
            if use_noncentered
            else helper.hierarchical_normal
        )

        coords = dict(
            root_sr=self.root_sr_pairs.labels,
            sub=self.subs,
            serum=self.sera,
            sub_serum=self.sub_serum.labels,
            site=self.sites,
        )

        with pm.Model(coords=coords) as model:

            # Per-serum effect
            serum = hierarchical_normal("b_serum", dims="serum")

            # Root titers
            T_root = hierarchical_normal("T_root", dims="root_sr")
            T_root_mu = T_root[self.root_sr_idx] + serum[self.root_perserum_idx]
            T_root_sd = pm.Exponential("T_root_obs_sd", 2.0)
            if student_t_lik:
                T_root_nu = pm.Exponential("T_root_obs_nu", 2.0)

            T_latent_root = (
                pm.StudentT.dist(mu=T_root_mu, sigma=T_root_sd, nu=T_root_nu)
                if student_t_lik
                else pm.Normal.dist(mu=T_root_mu, sigma=T_root_sd)
            )

            # Root titer likelihood
            pm.Censored(
                "T_root_obs",
                T_latent_root,
                observed=self.df_root["log_titer"].values,
                lower=-1.0,
                upper=None,
            )

            # Delta titers

            # Substitution effects
            if student_t_b_sub and site_in_hierarchy:
                raise NotImplementedError

            elif student_t_b_sub:
                b_sub = pm.StudentT(
                    "b_sub",
                    mu=pm.Normal("b_sub_mu", 0.0, 0.5),
                    sigma=pm.Exponential("b_sub_sigma", 2.0),
                    nu=pm.Exponential("b_sub_nu", 1.0),
                    dims="sub",
                )

            elif site_in_hierarchy:
                site = hierarchical_normal("b_site", dims="site")
                b_sub = hierarchical_normal(
                    "b_sub", dims="sub", hyper_mu=site[self.site_idx]
                )

            else:
                b_sub = hierarchical_normal("b_sub", dims="sub")

            # Individual effects of each substitution in each serum
            b_sub_serum_kwds = dict(
                name="b_sub_serum",
                mu=b_sub[self.sub_idx],
                sigma=pm.Exponential("b_sub_serum_sd", 2.0),
                dims="sub_serum",
            )
            if student_t_b_sub_serum:
                b_sub_serum = pm.StudentT(
                    nu=pm.Exponential("b_sub_serum_nu", 1.0), **b_sub_serum_kwds
                )
            else:
                b_sub_serum = pm.Normal(**b_sub_serum_kwds)

            # Titer drop (delta titer) is additive combination of each mutants substitutions
            T_delta = sparse.dot(self.X_sparse, b_sub_serum[:, None]).flatten()

            # Mutant titers
            T_mut_mu = pm.Deterministic("T_mut_mu", T_root[self.root_idx] + T_delta)
            T_mut_sd = pm.Exponential("T_mut_obs_sd", 2.0)
            if student_t_lik:
                T_mut_nu = pm.Exponential("T_mut_obs_nu", 2.0)

            T_latent_mut = (
                pm.StudentT.dist(mu=T_mut_mu, sigma=T_mut_sd, nu=T_mut_nu)
                if student_t_lik
                else pm.Normal.dist(mu=T_mut_mu, sigma=T_mut_sd)
            )

            # Likelihood
            pm.Censored(
                "T_mut_obs",
                T_latent_mut,
                observed=self.df_mut["log_titer"].values,
                lower=-1.0,
                upper=None,
            )

        return model
