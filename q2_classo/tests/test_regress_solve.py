"""One real c-lasso solve, small enough to run in CI.

Every other test in this suite is a registration, naming or asset check, and
the CI smoke test only runs ``qiime classo regress --help``. Nothing actually
called the solver -- which is how ``regress`` came to be completely dead
against numpy 2 (c-lasso 1.0.11 uses the removed ``np.infty`` alias; see
q2_classo/_numpy_compat.py) without a single test going red.

Deliberately tiny -- n=40, d=12, PATH + LAMfixed only, no cross-validation and
no stability selection -- so it stays cheap. It asserts shapes and finiteness,
not coefficient values: the point is to catch "the solver cannot run at all",
not to pin numerical output.
"""

import unittest

import numpy as np
import pandas as pd
import qiime2

from q2_classo import regress

N_SAMPLES = 40
N_FEATURES = 12


def toy_problem(seed=0):
    """A well-conditioned sparse regression: 3 of 12 features carry signal."""
    rng = np.random.default_rng(seed)
    ids = pd.Index(
        ["S{:02d}".format(i) for i in range(N_SAMPLES)], name="sample-id"
    )
    labels = ["F{:02d}".format(j) for j in range(N_FEATURES)]
    features = pd.DataFrame(
        rng.normal(size=(N_SAMPLES, N_FEATURES)), index=ids, columns=labels
    )
    beta = np.zeros(N_FEATURES)
    beta[:3] = [3.0, -2.0, 1.0]
    y = features.values @ beta + rng.normal(size=N_SAMPLES) * 0.5
    metadata = qiime2.Metadata(pd.DataFrame({"y": y}, index=ids))
    return features, metadata.get_column("y")


class TestRegressSolve(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        features, y = toy_problem()
        cls.problem = regress(
            features, y, path=True, cv=False, stabsel=False, lamfixed=True
        )

    # intercept=True is the registered default, so c-lasso prepends an
    # 'intercept' column to the coefficients.
    def test_path_betas(self):
        betas = np.asarray(self.problem.solution.PATH.BETAS)
        lambdas = np.asarray(self.problem.solution.PATH.LAMBDAS)
        self.assertEqual(betas.shape, (len(lambdas), N_FEATURES + 1))
        self.assertTrue(np.all(np.isfinite(betas)))
        self.assertTrue(np.any(betas != 0.0))

    def test_lamfixed_beta(self):
        beta = np.asarray(self.problem.solution.LAMfixed.beta)
        self.assertEqual(beta.shape, (N_FEATURES + 1,))
        self.assertTrue(np.all(np.isfinite(beta)))

    def test_labels_line_up_with_coefficients(self):
        self.assertEqual(
            len(self.problem.data.label),
            np.asarray(self.problem.solution.LAMfixed.beta).shape[0],
        )


if __name__ == "__main__":
    unittest.main()
