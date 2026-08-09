"""NumPy 2 compatibility shim for c-lasso.

c-lasso 1.0.11 -- the pinned release, and the latest one upstream has -- still
calls ``np.infty`` in five places: ``solve_R1.py:212``, ``solve_R2.py:239`` and
``:293``, ``solve_R3.py:205``, ``solve_R4.py:211``. NumPy 2.0 removed that
alias, so against the QIIME 2 2026.7 distribution (numpy 2.x) every
``qiime classo regress`` call dies with

    AttributeError: `np.infty` was removed in the NumPy 2.0 release.

before the solver returns anything -- for PATH, LAMfixed, CV and StabSel alike.
``classify`` is unaffected; it does not reach those lines.

Restoring the alias is exact rather than an approximation: ``np.infty`` was only
ever a second name for ``np.inf``, so no number changes. This is a stopgap --
the durable fix is a patched c-lasso (upstream has no release with the fix).
Delete this module once the pin can move to one that does.

Import it before calling into c-lasso's solvers.
"""

import numpy as np

if not hasattr(np, "infty"):
    np.infty = np.inf
