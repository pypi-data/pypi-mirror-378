# SymMaps
The package is generally used to set up and navigate systems of equations/variables using symbols defined over pandas indices. The package contains the following useful classes:

## Helper classes (base.py)
---
`symMaps/base.py` defines three small helper classes that simplifies the task of making adjustments to symbols defined over pandas indices. An introduction to the class is added as part of the documentation for the `SimplySys` (`docs_SimpleSys.ipynb`). Here is a short description of the helper classes:

### `Lag`

    ```
	Utility for creating lagged versions of pandas indices and Series.

	The Lag class provides static helpers that shift a pandas Index or Series
	backwards (i.e. create index/value pairs corresponding to v[index - lag]).
	It supports 1D indices and MultiIndex objects via level or dict specifications.

	Key methods
	- series(v, lag, level=None, fkeep=False, bfill='exo', exo=0):
	  Return a pd.Series with values shifted according to `lag`. Handles options:
		fkeep: keep forward-shifted indices outside original domain.
		bfill: how to backfill values not present in original series ('exo','ss', False).
		exo: numeric value used when bfill == 'exo'.
	- idx(idx, lag, level=None):
	  Return a shifted Index (or MultiIndex) corresponding to lag specification.

	Typical usage
	- Create lagged parameters or variables before adding them to linear
	  constraints in LPSys (see symMaps.lpSys.LPSys.initA_lag).
    ```

### `Lead` 

    ```
	Lead is a thin wrapper around Lag that applies a forward shift.

	Lead inverts the sign of the lag input and then calls the Lag helpers.
	This allows callers to express leads (future indices) using the same
	interface as lags. All parameters and options are passed through to Lag.

	Example:
	  Lead.series(v, lead, fkeep=True, bfill=False)
    ```

### `Roll`

    ```
    Utilities to 'roll' (circularly shift) pandas indices and Series.

	Roll performs circular rotations of index levels. Unlike Lag, Roll does not
	create new index elements; it permutes existing ones. Methods mirror those
	of Lag but use numpy.roll semantics. Useful for circular boundary conditions
	or categorical index rotations.

	Key methods
	- series(v, roll, level=None): return a Series whose index is rolled.
	- idx(idx, roll, level=None): return rolled Index or MultiIndex.
    ```


## SimpleSys (simpleSys.py)
---
`symMaps.simplySys.py` defines a simple way of navigating a collection of symbols defined over pandas indices in the class `SimpleSys`. The notebook `docs_SimpleSys.ipynb` goes through the setup and shows examples of how to use this.


## Linear programming (lpSys.py)
---
`symMaps.lpSys.py` defines three classes that are especially useful for navigating linear programming problems. The main class here is `LPSys` that includes a lot of different methods to set up sparse coefficient matrices for LP problems. See `docs_LPSys` for a documentation of this class. Here is a brief description of the class:

    ```
	LPSys — a helper for building and compiling linear programs using pandas indices.

	Purpose
	- Provide a high-level, index-aware API for declaring variables, constraints
	  and their linear relationships using pandas Index / MultiIndex objects.
	- Maintain sparse definitions (series over partial domains) and compile them
	  into the dense structures required by solvers (e.g. scipy.optimize.linprog).

	Key concepts / attributes
	- self.v: dict mapping variable name -> domain (pd.Index, pd.MultiIndex or None for scalar).
	- self.eq, self.ub: dict mapping constraint name -> domain (pd.Index, pd.MultiIndex or None for scalar).
	- self.lp: dict-like store for problem components:
		- 'A_eq' / 'A_ub' : AMDictionaries of AMatrix objects (matrix coefficients).
		- 'c', 'l', 'u' etc: coefficient dictionaries (GpyDict / pandas Series).
	- self.maps: compiled mappings from pandas domains to stacked global variable indices.
	- self.len: dict of lengths for domains (used when building arrays).
	- self.out: compiled arguments (A, b, c, bounds) ready for solver.

	Important methods (high-level)
	- compileMaps(): build internal mappings (self.maps) from declared domains (self.v, self.eq, self.ub).
	- compileParams() / compileParams(...): convert self.lp parameter dicts to solver vectors/matrices.
	- initA_infer(name, series, v, constr, attr='eq'): add AMatrix using inference from series index.
	- initA_lag(...), initA_roll(...): helpers to add matrix coefficients where the variable
	  index is a lag/roll (calls symMaps.base.Lag / Lead / Roll utilities).
	- lazyA(...), lazyA_lag(...): broadcast a (possibly partial) coefficient series across
	  combined domains and add as AMatrix; variants handle lag/roll mappings before broadcasting.
	- sparse_bounds() / dense_bounds(): helpers to convert bound declarations to solver bounds.
	- unloadSol(sol): map solver solution back to pandas Series / dictionaries for variables and duals.

	Notes on lags/leads/rolls
	- This class uses Lag, Lead and Roll utilities (defined in symMaps.base) to transform
	  pandas indices/series before building matrix blocks. These utilities are expected
	  to return aligned pd.Index / pd.Series objects that match the intended constraint domains.
	- When adding lagged coefficients, the constraint domain and variable domain can be
	  different; initA_lag / lazyA_lag handle mapping between them via index transformations.

	Usage (brief example)
		self.v = {'y': pd.MultiIndex.from_product([t, i])}
		self.eq = {'vec_tx0': t[1:]}
		self.compileMaps()
		# add parameter defined on y domain
		par = pd.Series(..., index=self.v['y'])
		# add a lagged coefficient that aligns par[t-1,i] with constraint vec_tx0[t]
		self.initA_lag('vec_tx0_y', series=par, v='y', constr='vec_tx0', attr='eq',
					   lag=1, level='t', fkeep=False, bfill=False)

	Implementation details
	- Internally uses lightweight AMatrix objects and AMDict containers to keep the
	  model sparse until compileParams() is called.
	- Many methods accept scalar, 1d or nd index inputs and dispatch based on
	  pandas Index vs MultiIndex types.

	See also
	- symMaps.base.Lag, Lead, Roll — helpers for index/series transformations.
	- AMatrix, AMDict definitions in this module (below) — low-level matrix block abstractions.
    ```



