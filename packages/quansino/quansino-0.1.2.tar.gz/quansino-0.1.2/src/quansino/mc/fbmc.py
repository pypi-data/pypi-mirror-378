"""Module to perform force bias Monte Carlo simulations."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, ClassVar, Final, Literal
from warnings import warn

import numpy as np
from ase.units import kB
from numpy.random import PCG64
from numpy.random import Generator as RNG

from quansino.mc.core import Driver
from quansino.utils.atoms import has_constraint

if TYPE_CHECKING:
    from typing import Any

    from ase.atoms import Atoms
    from numpy.typing import NDArray

    from quansino.type_hints import Displacements, Forces, ShapedMasses


class ForceBias(Driver):
    """
    Force Bias Monte Carlo class to perform simulations as described in
    https://doi.org/10.1063/1.4902136.

    Parameters
    ----------
    atoms : Atoms
        The atomic system being simulated.
    delta : float
        Delta parameter in Ångstrom which influence how much the atoms are moved.
    temperature : float, optional
        The temperature of the simulation in Kelvin, by default 298.15 K.
    seed : int | None, optional
        Seed for the random number generator, by default None. If None, a random seed is generated.
    **driver_kwargs : Any
        Additional keyword arguments to pass to the parent classes. See [`MonteCarlo`][quansino.mc.core.MonteCarlo] and [`Driver`][quansino.mc.driver.Driver] for more information.

    Attributes
    ----------
    gamma_max_value: float
        Maximum value for the gamma parameter, used to avoid overflow errors.
    delta: float
        Delta parameter in Ångstrom which influence how much the atoms are moved.
    temperature: float
        The temperature of the simulation in Kelvin.
    masses_scaling_power: NDArray
        Power to which the mass ratio is raised to scale the displacement.
    mass_scaling: NDArray
        Scaling factors for the atomic displacements based on masses.
    shaped_masses: NDArray
        Masses of the atoms shaped for vectorized calculations.
    """

    gamma_max_value = 709.782712

    def __init__(
        self,
        atoms: Atoms,
        delta: float,
        temperature: float = 298.15,
        seed: int | None = None,
        **driver_kwargs: Any,
    ) -> None:
        """Initialize the Force Bias Monte Carlo object."""
        self.delta = delta
        self.temperature = temperature

        self.__seed: Final = seed or PCG64().random_raw()
        self._rng = RNG(PCG64(self.__seed))

        super().__init__(atoms, **driver_kwargs)

        self.update_masses(atoms.get_masses())
        self.masses_scaling_power = 0.25

        if not has_constraint(self.atoms, "FixCom"):
            warn(
                "No `FixCom` constraint found, `ForceBias` simulations can lead to sustained drift of the center of mass.",
                UserWarning,
                2,
            )

        self.gamma = 0.0

        if self.default_logger:
            self.default_logger.add_mc_fields(self)
            self.default_logger.add_field(
                "Gamma/GammaMax",
                lambda: np.max(np.abs(self.gamma / self.gamma_max_value)),
                str_format="{:>16.2f}",
            )

    def calculate_gamma(self, forces: Forces) -> None:
        """
        Calculate the gamma parameter for the Monte Carlo step, along with the denominator for the trial probability.

        Parameters
        ----------
        forces : Forces
            The forces acting on the atoms.
        """
        self.gamma = np.clip(
            (forces * self.delta) / (2 * self.temperature * kB),
            -self.gamma_max_value,
            self.gamma_max_value,
        )

        self.denominator = np.exp(self.gamma) - np.exp(-self.gamma)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the ForceBias object to a dictionary.

        Returns
        -------
        dict[str, Any]
            A dictionary containing the state of the ForceBias object, including the random number generator state,
        """
        dictionary = super().to_dict()
        dictionary["rng_state"] = self._rng.bit_generator.state

        dictionary.setdefault("kwargs", {})
        dictionary["kwargs"] = {
            "seed": self.__seed,
            "temperature": self.temperature,
            "delta": self.delta,
        }

        dictionary.setdefault("attributes", {})
        dictionary["attributes"]["masses_scaling_power"] = self.masses_scaling_power

        return dictionary

    @property
    def masses_scaling_power(self) -> ShapedMasses | float:
        """
        Get the power to which the mass ratio is raised to scale the displacement.

        Returns
        -------
        ShapedMasses | float
            The power value(s) for each atom and direction.
        """
        return self._masses_scaling_power

    @masses_scaling_power.setter
    def masses_scaling_power(
        self, value: dict[str, float] | ShapedMasses | float
    ) -> None:
        """
        Set the power to which the mass ratio is raised to scale the displacement.

        Parameters
        ----------
        value : dict[str, float] | ShapedMasses | float
            The power value(s). If a dict, keys are element symbols and values are the powers. If ShapedMasses, it must have shape (len(atoms), 3). If a float, the same value is used for all atoms.

        Raises
        ------
        ValueError
            If the value has an invalid type or if an NDArray with incorrect shape is provided.
        """
        size = (len(self.atoms), 3)

        if isinstance(value, dict):
            self._masses_scaling_power = np.full(size, 0.25)

            for el in np.unique(self.atoms.symbols):
                indices = self.atoms.symbols == el
                self._masses_scaling_power[indices, :] = value.get(el, 0.25)

        elif isinstance(value, float | np.floating):
            self._masses_scaling_power = value
        elif isinstance(value, np.ndarray):
            if value.shape != size:
                raise ValueError(
                    f"Invalid shape for masses_scaling_power. Expected {size}, got {value.shape}."
                )

            self._masses_scaling_power = value
        else:
            raise ValueError("Invalid value type for masses_scaling_power.")

    def update_masses(self, masses: ShapedMasses | None = None) -> None:
        """
        Update the masses used for displacement scaling.

        Parameters
        ----------
        masses : ShapedMasses | Masses | None, optional
            The masses to use, by default None. If None, uses the masses from the atoms object.
        """
        if masses is None:
            masses = self.atoms.get_masses()

        if masses.ndim == 1:
            masses = np.broadcast_to(masses[:, np.newaxis], (len(self.atoms), 3))

        self.shaped_masses = masses

    def step(self) -> Forces:
        """
        Perform one Force Bias Monte Carlo step.

        Returns
        -------
        Forces
            The forces acting on the atoms after the Monte Carlo step.
        """
        forces = self.atoms.get_forces()
        positions = self.atoms.get_positions()

        self.current_size = (len(self.atoms), 3)

        self.calculate_gamma(forces)

        self.zeta = self.get_zeta()

        probability_random = self._rng.random(self.current_size)
        converged = self.calculate_trial_probability() > probability_random

        while not np.all(converged):
            self.current_size = probability_random[~converged].shape
            self.zeta[~converged] = self.get_zeta()

            probability_random[~converged] = self._rng.random(self.current_size)

            converged = self.calculate_trial_probability() > probability_random

        displacement = (
            self.zeta
            * self.delta
            * np.power(
                np.min(self.shaped_masses) / self.shaped_masses,
                self.masses_scaling_power,
            )
        )

        self.atoms.set_momenta(self.shaped_masses * displacement)
        corrected_displacement = self.atoms.get_momenta() / self.shaped_masses

        self.atoms.set_positions(positions + corrected_displacement)

        return forces

    def get_zeta(self) -> Displacements:
        """
        Get the zeta parameter for the current step.

        Returns
        -------
        Displacement
            The zeta parameter with values uniformly distributed between -1 and 1.
        """
        return self._rng.uniform(-1, 1, self.current_size)

    def calculate_trial_probability(self) -> NDArray[np.floating]:
        """
        Calculate the trial probability for the Monte Carlo step based on the force bias.

        Returns
        -------
        NDArray[np.floating]
            The trial probability for each atom and direction.
        """
        sign_zeta = np.sign(self.zeta)

        probability_trial = np.exp(sign_zeta * self.gamma) - np.exp(
            self.gamma * (2 * self.zeta - sign_zeta)
        )
        probability_trial *= sign_zeta

        return np.divide(
            probability_trial,
            self.denominator,
            out=np.ones_like(probability_trial),
            where=self.denominator != 0,
        )


class AdaptiveForceBias(ForceBias):
    """
    Adaptive Force Bias Monte Carlo class to perform simulations with adaptive delta parameter. The delta parameter is adjusted based on the variation coefficient of the forces or energies which is calculated based on the variance of the forces or energies. The current class assume that the forces or energies are calculated by a committee of MACECalculator.

    ```python
    model_paths = ["path/to/model_0", "path/to/model_1", "path/to/model_2"]
    mace_calcs = MACECalculator(model_paths=model_paths)
    ```

    The variation of the `delta` parameter allow the simulation to explore the phase space more efficiently based on the variance of the forces or energies. The `delta` parameter is adjusted based on the following formula:

    Parameters
    ----------
    atoms: Atoms
        The atomic system being simulated.
    min_delta: float
        Minimum delta parameter in Angstrom.
    max_delta: float
        Maximum delta parameter in Angstrom.
    temperature: float
        The temperature of the simulation in Kelvin. Default: 298.15.
    scheme: str
        Scheme to use for variation coefficient calculation. Default: "forces".
    reference_variance: float
        Reference variance for the variation coefficient. Default: 0.1.
    update_function: str
        Update function to use for delta parameter adjustment. Default: "tanh".
    **mc_kwargs
        Additional keyword arguments to pass to the ForceBias superclass.
    """

    energies_variance_keyword: ClassVar[str] = "energies"
    forces_variance_keyword: ClassVar[str] = "forces_comm"

    def __init__(
        self,
        atoms: Atoms,
        min_delta: float,
        max_delta: float,
        temperature: float = 298.15,
        scheme: Literal["forces", "energy"] = "forces",
        reference_variance: float = 0.1,
        update_function: str = "tanh",
        **mc_kwargs,
    ):
        self.reference_variance = reference_variance

        self.min_delta = min_delta
        self.max_delta = max_delta

        self.schemes = {
            "forces": self.get_forces_variation_coef,
            "energy": self.get_energy_variation_coef,
        }
        self.scheme = scheme

        self.update_functions = {"tanh": self.tanh_update, "exp": self.exp_update}
        self.update_function = update_function

        self.variation_coef: NDArray[np.floating] | float = 0.0

        super().__init__(
            atoms, (self.min_delta + self.max_delta) / 2, temperature, **mc_kwargs
        )

        if self.default_logger:
            if self.scheme == "forces":
                self.default_logger.add_field(
                    "MeanDelta", lambda: np.mean(self.delta), str_format="{:>16.2f}"
                )
                self.default_logger.add_field(
                    "MinDelta", lambda: np.min(self.delta), str_format="{:>16.2f}"
                )
                self.default_logger.add_field(
                    "MaxDelta", lambda: np.max(self.delta), str_format="{:>16.2f}"
                )
                self.default_logger.add_field(
                    "MeanForcesVar",
                    lambda: np.mean(self.variation_coef),
                    str_format="{:>16.6f}",
                )
            elif self.scheme == "energy":
                self.default_logger.add_field(
                    "Delta", lambda: self.delta, str_format="{:>16.2f}"
                )
                self.default_logger.add_field(
                    "EnergyVar", lambda: self.variation_coef, str_format="{:>16.6f}"
                )

    def update_delta(self) -> None:
        """
        Update the delta parameter based on the current variation coefficient. This method is called automatically during the step process.
        """
        self.variation_coef = self.schemes[self.scheme](self.atoms)

        self.delta = self.min_delta + (
            self.max_delta - self.min_delta
        ) * self.update_functions[self.update_function](self.variation_coef)

    def get_forces_variation_coef(self, atoms: Atoms) -> NDArray:
        """
        Calculate the variation coefficient based on committee forces.

        Parameters
        ----------
        atoms: Atoms
            The atomic system being simulated.

        Returns
        -------
        NDArray
            The variation coefficient for the forces.
        """
        try:
            forces_committee = atoms.calc.results[self.forces_variance_keyword]  # type: ignore[try-attr]
            return np.std(forces_committee, axis=0) / np.mean(
                np.abs(forces_committee), axis=0
            )
        except (KeyError, AttributeError):
            warn(
                "No committee forces available, using default reference variance.",
                stacklevel=2,
            )
            return np.full((len(atoms), 3), self.reference_variance)

    def get_energy_variation_coef(self, atoms: Atoms) -> float:
        """
        Calculate the variation coefficient based on committee energies.

        Parameters
        ----------
        atoms: Atoms
            The atomic system being simulated.

        Returns
        -------
        float
            The variation coefficient for the energies.
        """
        try:
            energies_committee = atoms.calc.results[self.energies_variance_keyword]  # type: ignore[try-attr]

            return np.std(energies_committee, axis=0) / len(atoms)
        except (KeyError, AttributeError):
            warn(
                "No committee energies available, using default reference variance.",
                stacklevel=2,
            )

            return self.reference_variance

    def tanh_update(
        self, variation_coefficient: float | NDArray
    ) -> float | NDArray[np.floating]:
        """
        Update function using the hyperbolic tangent (tanh) function.

        Parameters
        ----------
        variation_coefficient: float | NDArray
            The variation coefficient.

        Returns
        -------
        float | NDArray[np.floating]
            The updated value based on the tanh function.
        """
        return 1 - np.tanh(
            variation_coefficient / self.reference_variance * math.atanh(0.5)
        )

    def exp_update(self, variation_coefficient: float) -> float | NDArray[np.floating]:
        """
        Update function using the exponential function.

        Parameters
        ----------
        variation_coefficient: float
            The variation coefficient.

        Returns
        -------
        float | NDArray[np.floating]
            The updated value based on the exponential function.
        """
        return np.exp(-variation_coefficient / self.reference_variance * math.log(2))

    def step(self) -> Forces:
        """
        Perform one Adaptive Force Bias Monte Carlo step.

        Returns
        -------
        Forces
            The forces acting on the atoms after the Monte Carlo step.
        """
        self.update_delta()
        return super().step()
