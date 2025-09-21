"""Provide linear algebra utilities for dynamical systems analysis.

This module provides specialized linear algebra routines for analyzing
dynamical systems, particularly in the context of the Circular Restricted
Three-Body Problem (CR3BP). The functions focus on eigenvalue analysis,
stability classification, and matrix decompositions relevant to periodic
orbits and manifold computations.

All routines use pure NumPy for portability and are designed to be
vectorized and JIT-friendly where applicable.

References
----------
.. [Koon2011] Koon, W. S., Lo, M. W., Marsden, J. E., Ross, S. D. (2011).
   *Dynamical Systems, the Three-Body Problem and Space Mission Design*.
   Springer.
"""
from typing import Set, Tuple

import numpy as np

from hiten.utils.log_config import logger


def eigenvalue_decomposition(A: np.ndarray, discrete: int = 0, delta: float = 1e-4) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    r"""Classify eigenvalue-eigenvector pairs into stable, unstable, and center subspaces.

    Performs eigenvalue decomposition and classifies the spectrum based on
    stability criteria for either continuous-time or discrete-time dynamical
    systems. Each eigenvector is pivot-normalized for consistent representation.

    Parameters
    ----------
    A : ndarray, shape (n, n)
        Real or complex square matrix to analyze.
    discrete : int, optional
        Classification mode. Default is 0.
        
        * 0 : Continuous-time system (Jacobian matrix)
              Uses sign of real part of lambda for classification
        * 1 : Discrete-time system (map matrix)
              Uses absolute value of lambda with neutral band for classification
    delta : float, optional
        Half-width of neutral band around stability threshold. Default is 1e-4.
        For continuous systems: absolute value of real part of lambda < delta -> center
        For discrete systems: absolute value of (absolute value of lambda - 1) < delta -> center

    Returns
    -------
    sn : ndarray
        Stable eigenvalues. For continuous: real part of lambda < -delta.
        For discrete: absolute value of lambda < 1-delta.
    un : ndarray
        Unstable eigenvalues. For continuous: real part of lambda > +delta.
        For discrete: absolute value of lambda > 1+delta.
    cn : ndarray
        Center eigenvalues (neutral spectrum within delta band).
    Ws : ndarray, shape (n, n_s)
        Stable eigenvectors stacked column-wise.
    Wu : ndarray, shape (n, n_u)
        Unstable eigenvectors stacked column-wise.
    Wc : ndarray, shape (n, n_c)
        Center eigenvectors stacked column-wise.

    Raises
    ------
    numpy.linalg.LinAlgError
        If eigenvalue decomposition fails. Returns empty arrays in this case.

    Notes
    -----
    - Eigenvectors are pivot-normalized: first non-zero entry equals 1
    - Small imaginary parts (< 1e-14) are set to zero for numerical stability
    - Empty subspaces return zero-column matrices with correct dimensions
    
    Examples
    --------
    >>> import numpy as np
    >>> from hiten.algorithms.dynamics.utils.linalg import eigenvalue_decomposition
    >>> # Continuous-time system with stable, center, unstable eigenvalues
    >>> A = np.diag([-2.0, 0.0, 0.5])
    >>> sn, un, cn, Ws, Wu, Wc = eigenvalue_decomposition(A)
    >>> sn
    array([-2.])
    >>> un
    array([0.5])
    >>> cn
    array([0.])
    
    See Also
    --------
    :func:`~hiten.algorithms.dynamics.utils.linalg.eigenvalue_decomposition` :
        General eigenvalue classification
    """
    logger.debug(f"Starting eigenvalue decomposition for matrix A with shape {A.shape}, discrete={discrete}, delta={delta}")
    # Compute eigen-decomposition
    try:
        eigvals, eigvecs = np.linalg.eig(A)
        logger.debug(f"Computed raw eigenvalues: {eigvals}")
    except np.linalg.LinAlgError as e:
        logger.error(f"Eigenvalue computation failed for matrix A: {e}")
        # Return empty/appropriately shaped arrays or raise error?
        # For now, returning empty arrays based on previous structure
        n = A.shape[0]
        empty_complex = np.array([], dtype=np.complex128)
        empty_matrix = np.zeros((n, 0), dtype=np.complex128)
        return empty_complex, empty_complex, empty_complex, empty_matrix, empty_matrix, empty_matrix

    # Remove infinitesimal imaginary parts if an eigenvalue is "basically real"
    eigvals = np.array([_zero_small_imag_part(ev, tol=1e-14) for ev in eigvals])
    logger.debug(f"Eigenvalues after zeroing small imaginary parts: {eigvals}")

    # Prepare lists
    sn, un, cn = [], [], []      # stable, unstable, center eigenvalues
    Ws_list, Wu_list, Wc_list = [], [], []  # stable, unstable, center eigenvectors

    # Classify each eigenvalue/vector, then pivot-normalize vector
    for k in range(len(eigvals)):
        val = eigvals[k]
        vec = eigvecs[:, k].copy() # Work on a copy to avoid modifying original eigvecs
        logger.debug(f"Processing eigenvalue {k+1}/{len(eigvals)}: {val}")

        # Find pivot (the first non-tiny entry), then normalize by that pivot
        pivot_index = 0
        while pivot_index < len(vec) and abs(vec[pivot_index]) < 1e-14:
            pivot_index += 1
        
        if pivot_index < len(vec):
            pivot = vec[pivot_index]
            if abs(pivot) > 1e-14:
                logger.debug(f"  Normalizing eigenvector {k+1} by pivot {pivot} at index {pivot_index}")
                vec = vec / pivot
            else:
                # This case (pivot element is zero/tiny) might indicate linear dependence
                # or numerical issues. Keep the original vector for now.
                logger.warning(f"  Pivot element for eigenvector {k+1} is near zero ({pivot}). Skipping normalization.")
        else:
            # This case (all elements are tiny) implies a zero vector, which shouldn't happen for eigenvectors
            logger.warning(f"  Eigenvector {k+1} seems to be a zero vector. Check matrix properties.")

        # Optionally remove tiny real/imag parts in the vector
        vec = _remove_infinitesimals_array(vec, tol=1e-14)

        # Classification: stable/unstable/center
        classification = "center" # Default
        if discrete == 1:
            # Discrete-time system => compare magnitude to 1 +- delta
            mag = abs(val)
            if mag < 1 - delta:
                classification = "stable"
                sn.append(val)
                Ws_list.append(vec)
            elif mag > 1 + delta:
                classification = "unstable"
                un.append(val)
                Wu_list.append(vec)
            else:
                classification = "center"
                cn.append(val)
                Wc_list.append(vec)
        else:
            # Continuous-time system => check sign of real part
            if val.real < -delta:
                classification = "stable"
                sn.append(val)
                Ws_list.append(vec)
            elif val.real > +delta:
                classification = "unstable"
                un.append(val)
                Wu_list.append(vec)
            else:
                classification = "center"
                cn.append(val)
                Wc_list.append(vec)
        logger.debug(f"  Classified as {classification}")

    # Convert lists into arrays
    sn = np.array(sn, dtype=np.complex128)
    un = np.array(un, dtype=np.complex128)
    cn = np.array(cn, dtype=np.complex128)

    Ws = np.column_stack(Ws_list) if Ws_list else np.zeros((A.shape[0], 0), dtype=np.complex128)
    Wu = np.column_stack(Wu_list) if Wu_list else np.zeros((A.shape[0], 0), dtype=np.complex128)
    Wc = np.column_stack(Wc_list) if Wc_list else np.zeros((A.shape[0], 0), dtype=np.complex128)

    logger.debug(f"Eigenvalue decomposition finished. Subspace dimensions: stable={len(sn)}, unstable={len(un)}, center={len(cn)}")
    logger.debug(f"Stable eigenvalues: {sn}")
    logger.debug(f"Unstable eigenvalues: {un}")
    logger.debug(f"Center eigenvalues: {cn}")

    return sn, un, cn, Ws, Wu, Wc


def _stability_indices(M: np.ndarray, tol: float = 1e-8) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    r"""Compute Floquet stability indices for periodic orbit analysis.

    Calculates the three stability indices nu_i = (lambda_i + 1/lambda_i)/2
    from the monodromy matrix of a periodic orbit. For symplectic systems,
    eigenvalues occur in reciprocal pairs (lambda, 1/lambda), and this
    function explicitly searches for such pairs.

    Parameters
    ----------
    M : ndarray, shape (6, 6)
        Monodromy matrix from one-period state transition matrix integration.
        Expected to be symplectic for CR3BP applications.
    tol : float, optional
        Tolerance for reciprocal eigenvalue pairing and unit-magnitude
        detection. Default is 1e-8.

    Returns
    -------
    nu : ndarray, shape (3,)
        Stability indices nu_i = (lambda_i + 1/lambda_i)/2.
        Contains np.nan for unpaired eigenvalues.
    eigvals : ndarray, shape (6,)
        Eigenvalues sorted by decreasing magnitude.
    eigvecs : ndarray, shape (6, 6)
        Corresponding eigenvectors.

    Raises
    ------
    ValueError
        If M is not shape (6, 6).
    numpy.linalg.LinAlgError
        If eigenvalue computation fails. Returns NaN arrays in this case.

    Notes
    -----
    - Assumes symplectic structure with reciprocal eigenvalue pairs
    - Robust to small numerical symmetry-breaking errors
    - Identifies trivial pairs (magnitude near 1) first
    - Warns if expected number of pairs (3) cannot be found
    
    For stable periodic orbits, all |nu_i| should be <= 1.
    
    Examples
    --------
    >>> import numpy as np
    >>> from hiten.algorithms.dynamics.utils.linalg import _stability_indices
    >>> # Identity matrix (trivial case)
    >>> M = np.eye(6)
    >>> nu, eigvals, eigvecs = _stability_indices(M)
    >>> np.allclose(nu, 1.0)
    True
    
    See Also
    --------
    :func:`~hiten.algorithms.dynamics.utils.linalg.eigenvalue_decomposition` :
        General eigenvalue classification
    """
    logger.info(f"Calculating stability indices for matrix M with shape {M.shape}, tolerance={tol}")

    if M.shape != (6, 6):
        logger.error(f"Input matrix M has incorrect shape {M.shape}, expected (6, 6).")
        raise ValueError("Input matrix M must be 6x6.")

    # --- Compute Eigenvalues and Eigenvectors ---
    try:
        logger.debug("Computing eigenvalues/vectors for M.")
        eigvals_raw, eigvecs_raw = np.linalg.eig(M)
        logger.debug(f"Raw eigenvalues: {eigvals_raw}")
    except np.linalg.LinAlgError as e:
        logger.error(f"Eigenvalue computation failed: {e}")
        # warnings.warn(f"Eigenvalue computation failed: {e}", RuntimeWarning)
        nan_result = np.full(3, np.nan, dtype=np.complex128)
        nan_eigs = np.full(6, np.nan, dtype=np.complex128)
        nan_vecs = np.full((6, 6), np.nan, dtype=np.complex128)
        return nan_result, nan_eigs, nan_vecs

    # Sort eigenvalues by magnitude (descending) for consistent output
    idx_sort = np.argsort(np.abs(eigvals_raw))[::-1]
    eigvals_sorted = eigvals_raw[idx_sort]
    eigvecs_sorted = eigvecs_raw[:, idx_sort]
    logger.debug(f"Sorted eigenvalues (by magnitude): {eigvals_sorted}")

    # --- Initialize and Prepare for Pairing ---
    nu = np.full(3, np.nan, dtype=np.complex128)
    remaining_evs = list(eigvals_raw) # Use original list for pairing logic
    found_pair_mask = [False, False, False] # To track which nu indices are filled
    pair_idx_nu = 0 # Index for the nu array
    logger.debug(f"Initial list of eigenvalues for pairing: {remaining_evs}")

    # --- 1. Identify Trivial Pair(s) (Magnitude close to 1.0) ---
    trivial_indices_in_list = [
        i for i, ev in enumerate(remaining_evs) 
        if np.isclose(np.abs(ev), 1.0, rtol=tol, atol=tol)
    ]
    logger.debug(f"Found {len(trivial_indices_in_list)} eigenvalues with magnitude close to 1.0: indices {trivial_indices_in_list}")

    if len(trivial_indices_in_list) >= 2:
        # Successfully found at least two trivial eigenvalues
        idx1 = trivial_indices_in_list[0]
        idx2 = trivial_indices_in_list[1]
        ev1 = remaining_evs[idx1]
        
        nu[pair_idx_nu] = (ev1 + 1.0 / ev1) / 2.0
        found_pair_mask[pair_idx_nu] = True
        logger.debug(f"Calculated nu[{pair_idx_nu}] = {nu[pair_idx_nu]} using trivial eigenvalue {ev1}")
        pair_idx_nu += 1
        
        # Remove the *pair* from the list, careful with indices
        indices_to_remove = sorted([idx1, idx2], reverse=True)
        ev_removed1 = remaining_evs.pop(indices_to_remove[0])
        ev_removed2 = remaining_evs.pop(indices_to_remove[1])
        logger.debug(f"Removed trivial pair ({ev_removed1}, {ev_removed2}) from list. Remaining: {remaining_evs}")

        if len(trivial_indices_in_list) > 2:
            extra_count = len(trivial_indices_in_list) - 2
            logger.warning(f"Found {len(trivial_indices_in_list)} eigenvalues with magnitude close to 1.0 "
                           f"(expected 2). Using first two found for nu[0]. "
                           f"The remaining {extra_count} near 1.0 will be processed "
                           f"with other non-trivial pairs.")
                          
    elif len(trivial_indices_in_list) == 1:
        # Found only one eigenvalue near 1.0 - use it but warn.
        logger.warning("Found only one eigenvalue with magnitude close to 1.0 (expected 2). "
                       "Calculating nu[0] based on this value, but pairing might be incomplete.")
        idx1 = trivial_indices_in_list[0]
        ev1 = remaining_evs[idx1]
        
        nu[pair_idx_nu] = (ev1 + 1.0 / ev1) / 2.0
        found_pair_mask[pair_idx_nu] = True
        logger.debug(f"Calculated nu[{pair_idx_nu}] = {nu[pair_idx_nu]} using single trivial eigenvalue {ev1}")
        pair_idx_nu += 1
        
        ev_removed = remaining_evs.pop(idx1) # Remove the single one found
        logger.debug(f"Removed single trivial eigenvalue {ev_removed}. Remaining: {remaining_evs}")

    else: # len(trivial_indices_in_list) == 0
        logger.warning("Did not find any eigenvalues with magnitude close to 1.0 (expected 2). "
                       "Cannot reliably determine the first stability index nu[0].")
        # Proceed to find other pairs, nu[0] will remain NaN unless found later

    # --- 2. Find Remaining Reciprocal Pairs ---
    processed_indices: Set[int] = set() # Indices in the *current* state of remaining_evs
    logger.debug(f"Starting search for remaining reciprocal pairs in {remaining_evs}")
    
    i = 0
    while i < len(remaining_evs):
        if i in processed_indices:
            i += 1
            continue

        current_ev = remaining_evs[i]
        logger.debug(f"  Processing index {i}, eigenvalue {current_ev}")
        # Avoid division by zero if an eigenvalue happens to be exactly zero
        if abs(current_ev) < tol * tol : # Use a very small tolerance here
             logger.warning(f"Encountered eigenvalue very close to zero ({current_ev:.2e}), skipping pairing for it.")
             processed_indices.add(i) # Mark as processed to avoid reciprocal search
             i += 1
             continue
             
        target_reciprocal = 1.0 / current_ev
        logger.debug(f"    Target reciprocal: {target_reciprocal}")
        found_match = False
        
        # Search for reciprocal in the rest of the list
        for j in range(i + 1, len(remaining_evs)):
            if j in processed_indices:
                continue
            
            potential_match = remaining_evs[j]
            logger.debug(f"      Comparing with index {j}, eigenvalue {potential_match}")
            if np.isclose(potential_match, target_reciprocal, rtol=tol, atol=tol):
                # Found a pair (current_ev, potential_match)
                logger.debug(f"    Found reciprocal pair: ({current_ev}, {potential_match}) at indices ({i}, {j})")
                if pair_idx_nu < 3:
                    nu[pair_idx_nu] = (current_ev + 1.0 / current_ev) / 2.0
                    found_pair_mask[pair_idx_nu] = True
                    logger.debug(f"      Calculated nu[{pair_idx_nu}] = {nu[pair_idx_nu]}")
                    pair_idx_nu += 1
                else:
                    logger.error(f"Logic error: Attempted to find more than 3 pairs. "
                                 f"Pair ({current_ev:.4f}, {potential_match:.4f}) ignored.")

                processed_indices.add(i)
                processed_indices.add(j)
                found_match = True
                break # Found match for current_ev, move to next i

        if not found_match:
            logger.debug(f"    No reciprocal found for {current_ev}")
            # No reciprocal found for current_ev among remaining unprocessed eigenvalues
            # Mark as processed so we don't check it again
            processed_indices.add(i)

        i += 1

    # --- 3. Final Checks and Warnings ---
    num_pairs_found = sum(found_pair_mask)
    logger.debug(f"Finished pairing search. Found {num_pairs_found} pairs total.")
    if num_pairs_found != 3:
        logger.warning(f"Failed to find all 3 reciprocal eigenvalue pairs. Found {num_pairs_found}. "
                       f"Check input matrix properties and tolerance ({tol=}). "
                       f"Resulting 'nu' array contains NaN.")
        
    # This unpaired_count calculation was complex and potentially buggy, replacing with simpler logic:
    final_unpaired_evs = [ev for k, ev in enumerate(remaining_evs) if k not in processed_indices]
    if final_unpaired_evs:
         logger.warning(f"Could not find reciprocal partners for {len(final_unpaired_evs)} eigenvalues: {final_unpaired_evs}")

    logger.info(f"Stability indices calculation complete. Resulting nu: {nu}")
    # Return nu array, sorted eigenvalues, and corresponding sorted eigenvectors
    return nu, eigvals_sorted, eigvecs_sorted


def _remove_infinitesimals_in_place(vec: np.ndarray, tol: float = 1e-14) -> None:
    r"""Remove numerical noise from complex vector components in-place.

    Sets real and imaginary parts smaller than tolerance to exactly zero,
    helping prevent numerical artifacts from affecting downstream calculations.

    Parameters
    ----------
    vec : ndarray
        Complex vector to clean in-place.
    tol : float, optional
        Tolerance below which components are zeroed. Default is 1e-14.

    Notes
    -----
    Modifies the input vector directly. Particularly useful for cleaning
    eigenvectors that may contain tiny numerical artifacts.
    
    See Also
    --------
    :func:`~hiten.algorithms.dynamics.utils.linalg._remove_infinitesimals_array` : Non-destructive version
    :func:`~hiten.algorithms.dynamics.utils.linalg._zero_small_imag_part` : Cleanup for scalar complex values
    """
    for i in range(len(vec)):
        re = vec[i].real
        im = vec[i].imag
        if abs(re) < tol:
            re = 0.0
        if abs(im) < tol:
            im = 0.0
        vec[i] = re + 1j*im

def _remove_infinitesimals_array(vec: np.ndarray, tol: float = 1e-12) -> np.ndarray:
    r"""Create cleaned copy of vector with numerical noise removed.

    Returns a copy of the input vector with real and imaginary components
    smaller than tolerance set to exactly zero. Preserves the original vector.

    Parameters
    ----------
    vec : ndarray
        Complex vector to clean.
    tol : float, optional
        Tolerance below which components are zeroed. Default is 1e-12.

    Returns
    -------
    ndarray
        Copy of input vector with small values replaced by exact zeros.
    
    See Also
    --------
    :func:`~hiten.algorithms.dynamics.utils.linalg._remove_infinitesimals_in_place` : In-place version
    :func:`~hiten.algorithms.dynamics.utils.linalg._zero_small_imag_part` : Cleanup for scalar complex values
    """
    vcopy = vec.copy()
    _remove_infinitesimals_in_place(vcopy, tol)
    return vcopy

def _zero_small_imag_part(eig_val: complex, tol: float = 1e-12) -> complex:
    r"""Remove small imaginary part from complex number.

    Sets imaginary part to zero if smaller than tolerance. Useful for
    cleaning eigenvalues that should be real but have numerical artifacts.

    Parameters
    ----------
    eig_val : complex
        Complex value to clean.
    tol : float, optional
        Tolerance below which imaginary part is zeroed. Default is 1e-12.

    Returns
    -------
    complex
        Cleaned complex value with small imaginary part removed.
        
    See Also
    --------
    :func:`~hiten.algorithms.dynamics.utils.linalg._remove_infinitesimals_array` : Vector version for arrays
    :func:`~hiten.algorithms.dynamics.utils.linalg._remove_infinitesimals_in_place` : In-place vector cleanup
    """
    if abs(eig_val.imag) < tol:
        return complex(eig_val.real, 0.0)
    return eig_val


def _totime(t, tf):
    r"""Find indices of closest time values in array.

    Searches time array for indices where values are closest to specified
    target times. Useful for extracting trajectory points at specific times.

    Parameters
    ----------
    t : array_like
        Time array to search.
    tf : float or array_like
        Target time value(s) to locate.

    Returns
    -------
    ndarray
        Indices where t values are closest to corresponding tf values.

    Notes
    -----
    - Uses absolute time values, so signs are ignored
    - Particularly useful for periodic orbit analysis
    - Returns single index for scalar tf, array of indices for array tf
    
    Examples
    --------
    >>> import numpy as np
    >>> from hiten.algorithms.dynamics.utils.linalg import _totime
    >>> t = np.linspace(0, 10, 101)  # Time array
    >>> tf = [2.5, 7.1]  # Target times
    >>> indices = _totime(t, tf)
    >>> t[indices]  # Closest actual times
    array([2.5, 7.1])
    """
    # Convert to absolute values and ensure tf is array
    t = np.abs(t)
    tf = np.atleast_1d(tf)
    
    # Find closest indices
    I = np.empty(tf.shape, dtype=int)
    for k, target in enumerate(tf):
        diff = np.abs(target - t)
        I[k] = np.argmin(diff)
    
    return I
