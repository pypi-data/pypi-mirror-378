# Copyright 2025 The safeincave community.
#
# This file is part of safeincave.
#
# Licensed under the GNU GENERAL PUBLIC LICENSE, Version 3 (the "License"); you may not
# use this file except in compliance with the License.  You may obtain a copy
# of the License at
#
#     https://spdx.org/licenses/GPL-3.0-or-later.html
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# License for the specific language governing permissions and limitations under
# the License.
from abc import ABC, abstractmethod
import torch as to
import numpy as np
import sys
import os
from mpi4py import MPI


from .Utils import numpy2torch
from .HeatEquation import HeatDiffusion
from .MomentumEquation import LinearMomentum
from .TimeHandler import TimeControllerBase, TimeController
from .OutputHandler import SaveFields
from .ScreenOutput import ScreenPrinter

from .Grid import GridHandlerGMSH
from .MaterialProps import *
# from .MomentumBC import BcHandler, NeumannBC, DirichletBC
from . import MomentumBC as momBC
from petsc4py import PETSc

class Simulator(ABC):
	"""
    Abstract simulation driver interface.

    Subclasses implement a concrete `run()` method that advances one or more
    coupled PDE solvers in time, handles I/O, and updates material/internal
    variables as needed.
    """
	@abstractmethod
	def run(self):
		"""
        Execute the simulation.

        Returns
        -------
        None
        """
		pass


class Simulator_TM(Simulator):
	"""
	Run the coupled thermo–mechanical simulation.

	Workflow
	--------
	1. Initialize outputs.
	2. Initialize momentum temperature from the heat solution and update BCs.
	3. Optionally solve a purely elastic response.
	4. Initialize non-elastic rates.
	5. For each time step:

	   - Advance time and update boundary conditions for both equations.
	   - Solve the heat equation for ``(t, dt)`` and set temperatures in momentum.
	   - Iterate the momentum step (assemble/solve, update internal variables and rates).
	   - Save requested fields.

	Returns
	-------
	None
	"""
	def __init__(self, eq_mom: LinearMomentum, 
					   eq_heat: HeatDiffusion, 
					   t_control: TimeControllerBase, 
					   outputs: list[SaveFields],
					   compute_elastic_response: bool=True):
		self.eq_mom = eq_mom
		self.eq_heat = eq_heat
		self.t_control = t_control
		self.outputs = outputs
		self.compute_elastic_response = compute_elastic_response
		
		ScreenPrinter.reset_instance()
		self.screen = ScreenPrinter(self.eq_mom.grid, self.eq_mom.solver, self.eq_mom.mat, self.outputs, t_control.time_unit)

	def run(self) -> None:
		"""
		Run the coupled thermo–mechanical simulation.

		Workflow
		--------
		1. Initialize outputs.
		2. Initialize momentum temperature history from the heat solution.
		3. Update BCs and optionally solve a purely elastic step.
		4. Initialize non-elastic rates.
		5. Time loop:

		   - Advance time, update BCs, solve heat step.
		   - Fixed-point (or single-pass) iterate the momentum step with the
		     current temperature, updating internal variables and rates.
		   - Save requested fields.

		Convergence
		-----------
		Uses a relative change in total strain between iterations as error.
		If ``theta == 1.0`` (backward Euler) or there are no non-elastic
		elements, iteration terminates immediately.

		Returns
		-------
		None

		Notes
		-----
		- Calls ``SaveFields.initialize()`` once and ``save_fields(t)`` at each
		  saved time, followed by ``save_mesh()`` after the loop.
		- Printing of progress occurs on rank 0 only.
		- The first ``output.save_fields(0)`` call targets the last ``output``
		  from the preceding loop variable; ensure all outputs are saved by
		  iterating over ``self.outputs``.
		"""
		# Output field
		for output in self.outputs:
			output.initialize()

		# Set initial temperature
		T_elems = self.eq_heat.get_T_elems()
		self.eq_mom.set_T0(T_elems)

		# Update boundary conditions
		self.eq_mom.bc.update_dirichlet(self.t_control.t)
		self.eq_mom.bc.update_neumann(self.t_control.t)

		if self.compute_elastic_response:
			# Solve elasticity
			self.eq_mom.solve_elastic_response()

			# Calculate total (elastic) strain
			eps_tot_to = self.eq_mom.compute_total_strain()

			# Compute stress
			stress_to = self.eq_mom.compute_elastic_stress(eps_tot_to)

		else:
			# Calculate total strain
			eps_tot_to = self.eq_mom.compute_total_strain()

			# Retrieve stress
			stress_to = numpy2torch(self.eq_mom.sig.x.array.reshape((self.eq_mom.n_elems, 3, 3)))

		# Set new temperature to momentum equation
		T_elems = self.eq_heat.get_T_elems()
		self.eq_mom.set_T(T_elems)
		self.eq_mom.set_T0(T_elems)

		# Calculate and eps_ie_rate_old
		self.eq_mom.compute_eps_ne_rate(stress_to, self.t_control.t)
		self.eq_mom.update_eps_ne_rate_old()


		# self.eq_heat.solve(0, self.t_control.dt)

		# Save fields
		self.eq_mom.compute_p_elems()
		self.eq_mom.compute_q_elems()
		self.eq_mom.compute_p_nodes()
		self.eq_mom.compute_q_nodes()
		output.save_fields(0)

		# Time loop
		while self.t_control.keep_looping():

			# Advance time
			self.t_control.advance_time()
			t = self.t_control.t
			dt = self.t_control.dt

			# Update boundary conditions
			self.eq_mom.bc.update_dirichlet(t)
			self.eq_mom.bc.update_neumann(t)
			self.eq_heat.bc.update_dirichlet(t)
			self.eq_heat.bc.update_neumann(t)

			# Solve heat
			self.eq_heat.solve(t, dt)

			# Set new temperature to momentum equation
			T_elems = self.eq_heat.get_T_elems()
			self.eq_mom.set_T(T_elems)

			# Iterative loop settings
			tol = 1e-6
			error = 2*tol
			ite = 0
			maxiter = 20

			while error > tol and ite < maxiter:

				# Update total strain of previous iteration (eps_tot_k <-- eps_tot)
				eps_tot_k_to = eps_tot_to.clone()

				# Update stress
				stress_k_to = stress_to.clone()

				# Build bi-linear form
				self.eq_mom.solve(stress_k_to, t, dt)

				# Compute total strain
				eps_tot_to = self.eq_mom.compute_total_strain()

				# Compute stress
				stress_to = self.eq_mom.compute_stress(eps_tot_to)

				# Increment internal variables
				self.eq_mom.increment_internal_variables(stress_to, stress_k_to, dt)

				# Compute inelastic strain rates
				self.eq_mom.compute_eps_ne_rate(stress_to, dt)

				# Compute error
				if self.eq_mom.theta == 1.0:
					error = 0.0
				elif len(self.eq_mom.mat.elems_ne) == 0:
					error = 0.0
				else:
					eps_tot_k_flat = to.flatten(eps_tot_k_to)
					eps_tot_flat = to.flatten(eps_tot_to)
					local_error =  np.linalg.norm(eps_tot_k_flat - eps_tot_flat) / np.linalg.norm(eps_tot_flat)
					error = self.eq_mom.grid.mesh.comm.allreduce(local_error, op=MPI.SUM)

				ite += 1

			# Update internal variables
			self.eq_mom.update_internal_variables()

			# Update strain rates
			self.eq_mom.update_eps_ne_rate_old()

			# Update strain
			self.eq_mom.update_eps_ne_old(stress_to, stress_k_to, dt)

			# Save fields
			self.eq_mom.compute_p_elems()
			self.eq_mom.compute_q_elems()
			self.eq_mom.compute_p_nodes()
			self.eq_mom.compute_q_nodes()
			for output in self.outputs:
				output.save_fields(t)

			# Print stuff
			current_time = "%.3f"%(t/self.t_control.time_conversion)
			screen_output_row = [
									self.t_control.step_counter, 
									self.t_control.dt/self.t_control.time_conversion,
									f"{current_time} / {self.t_control.t_final/self.t_control.time_conversion}",
									ite,
									error,
			]
			self.screen.print_row(screen_output_row)

		self.screen.close()

		for output in self.outputs:
			output.save_mesh()


class Simulator_M(Simulator):
	"""
    Mechanical-only simulator (linear momentum).

    Solves the momentum equation with possible non-elastic behavior using a
    θ-method loop and fixed-point iterations per step. No thermal coupling.

    Parameters
    ----------
    eq_mom : LinearMomentum
        Configured momentum equation (materials, BCs, solver set).
    t_control : TimeControllerBase
        Time controller providing `t`, `dt`, and loop control.
    outputs : list of SaveFields
        Output writers to initialize and use at each saved time.
    compute_elastic_response : bool, default=True
        If True, starts with a purely elastic solve to initialize fields.

    Attributes
    ----------
    eq_mom : LinearMomentum
    t_control : TimeControllerBase
    outputs : list[SaveFields]
    compute_elastic_response : bool
    """
	def __init__(self, eq_mom: LinearMomentum, 
					   t_control: TimeControllerBase,
					   outputs: list[SaveFields],
					   compute_elastic_response: bool=True):
		self.eq_mom = eq_mom
		self.t_control = t_control
		self.outputs = outputs
		self.compute_elastic_response = compute_elastic_response
		
		ScreenPrinter.reset_instance()
		self.screen = ScreenPrinter(self.eq_mom.grid, self.eq_mom.solver, self.eq_mom.mat, self.outputs, t_control.time_unit)

	def run(self) -> None:
		"""
        Run the mechanical simulation.

        Workflow
        --------
        1. Initialize outputs and boundary conditions.
        2. Optionally solve a purely elastic step.
        3. Initialize non-elastic rates.
        4. For each time step: assemble/solve, update internal variables and
           rates, compute relevant quantities, and save fields.

        Convergence
        -----------
        Uses a relative change in total strain between iterations as error.
        If `theta == 1.0` or no non-elastic elements exist, iteration ends
        immediately.

        Returns
        -------
        None

        Notes
        -----
        - Printing occurs on rank 0 only.
        - The first `output.save_fields(0)` call uses the last `output`
          from the preceding loop variable.
        """
		# Output field
		for output in self.outputs:
			output.initialize()

		# Update boundary conditions
		self.eq_mom.bc.update_dirichlet(self.t_control.t)
		self.eq_mom.bc.update_neumann(self.t_control.t)

		if self.compute_elastic_response:
			# Solve elasticity
			self.eq_mom.solve_elastic_response()

			# Calculate total (elastic) strain
			eps_tot_to = self.eq_mom.compute_total_strain()

			# Compute stress
			stress_to = self.eq_mom.compute_elastic_stress(eps_tot_to)

		else:
			# Calculate total strain
			eps_tot_to = self.eq_mom.compute_total_strain()

			# Retrieve stress
			stress_to = numpy2torch(self.eq_mom.sig.x.array.reshape((self.eq_mom.n_elems, 3, 3)))

		# Calculate and eps_ie_rate_old
		self.eq_mom.compute_eps_ne_rate(stress_to, self.t_control.t)
		self.eq_mom.update_eps_ne_rate_old()

		# Save fields
		self.eq_mom.compute_p_elems()
		self.eq_mom.compute_q_elems()
		self.eq_mom.compute_p_nodes()
		self.eq_mom.compute_q_nodes()
		output.save_fields(0)

		# Time loop
		while self.t_control.keep_looping():

			# Advance time
			self.t_control.advance_time()
			t = self.t_control.t
			dt = self.t_control.dt

			# Update boundary conditions
			self.eq_mom.bc.update_dirichlet(t)
			self.eq_mom.bc.update_neumann(t)

			# Iterative loop settings
			tol = 1e-8
			error = 2*tol
			ite = 0
			maxiter = 40

			while error > tol and ite < maxiter:

				# Update total strain of previous iteration (eps_tot_k <-- eps_tot)
				eps_tot_k_to = eps_tot_to.clone()

				# Update stress
				stress_k_to = stress_to.clone()

				# Build bi-linear form
				self.eq_mom.solve(stress_k_to, t, dt)

				# Compute total strain
				eps_tot_to = self.eq_mom.compute_total_strain()

				# Compute stress
				stress_to = self.eq_mom.compute_stress(eps_tot_to)

				# Increment internal variables
				self.eq_mom.increment_internal_variables(stress_to, stress_k_to, dt)

				# Compute inelastic strain rates
				self.eq_mom.compute_eps_ne_rate(stress_to, dt)

				# Compute error
				if self.eq_mom.theta == 1.0:
					error = 0.0
				elif len(self.eq_mom.mat.elems_ne) == 0:
					error = 0.0
				else:
					eps_tot_k_flat = to.flatten(eps_tot_k_to)
					eps_tot_flat = to.flatten(eps_tot_to)
					local_error =  np.linalg.norm(eps_tot_k_flat - eps_tot_flat) / np.linalg.norm(eps_tot_flat)
					error = self.eq_mom.grid.mesh.comm.allreduce(local_error, op=MPI.SUM)

				ite += 1

			# Update internal variables
			self.eq_mom.update_internal_variables()

			# Update strain rates
			self.eq_mom.update_eps_ne_rate_old()

			# Update strain
			self.eq_mom.update_eps_ne_old(stress_to, stress_k_to, dt)

			# Save fields
			self.eq_mom.compute_p_elems()
			self.eq_mom.compute_q_elems()
			self.eq_mom.compute_p_nodes()
			self.eq_mom.compute_q_nodes()
			for output in self.outputs:
				output.save_fields(t)

			# Print stuff
			current_time = "%.3f"%(t/self.t_control.time_conversion)
			screen_output_row = [
									self.t_control.step_counter, 
									self.t_control.dt/self.t_control.time_conversion,
									f"{current_time} / {self.t_control.t_final/self.t_control.time_conversion}",
									ite,
									error,
			]
			self.screen.print_row(screen_output_row)

		self.screen.close()

		for output in self.outputs:
			output.save_mesh()


class Simulator_T(Simulator):
	"""
    Thermal-only simulator (heat diffusion).

    Advances the heat equation with fully-implicit time loop and writes fields.

    Parameters
    ----------
    eq_heat : HeatDiffusion
        Configured heat equation (materials, BCs, solver set).
    t_control : TimeControllerBase
        Time controller providing `t`, `dt`, and loop control.
    outputs : list of SaveFields
        Output writers to initialize and use at each saved time.
    compute_elastic_response : bool, default=True
        Unused placeholder kept for interface parity.

    Attributes
    ----------
    eq_heat : HeatDiffusion
    t_control : TimeControllerBase
    outputs : list[SaveFields]
    """
	def __init__(self, eq_heat: HeatDiffusion,
					   t_control: TimeControllerBase,
					   outputs: list[SaveFields],
					   compute_elastic_response: bool=True):
		self.eq_heat = eq_heat
		self.t_control = t_control
		self.outputs = outputs

		ScreenPrinter.reset_instance()
		self.screen = ScreenPrinter(self.eq_heat.grid, self.eq_heat.solver, self.eq_heat.mat, self.outputs, t_control.time_unit)

	def run(self) -> None:
		"""
        Run the thermal simulation.

        Workflow
        --------
        1. Initialize outputs.
        2. (Optionally) solve an initial step.
        3. Time loop: update BCs, solve heat equation for `(t, dt)`, and save.

        Returns
        -------
        None

        Notes
        -----
        Printing of progress occurs on rank 0 only.
        """
		# Output field
		for output in self.outputs:
			output.initialize()

		# # Solve initial T field
		# self.eq_heat.solve(0, self.t_control.dt)

		# Save fields
		output.save_fields(0)

		# Time loop
		while self.t_control.keep_looping():

			# Advance time
			self.t_control.advance_time()
			t = self.t_control.t
			dt = self.t_control.dt

			# Update boundary conditions
			self.eq_heat.bc.update_dirichlet(t)
			self.eq_heat.bc.update_neumann(t)

			# Solve heat
			self.eq_heat.solve(t, dt)

			# Save fields
			for output in self.outputs:
				output.save_fields(t)

			# Print stuff
			current_time = "%.3f"%(t/self.t_control.time_conversion)
			screen_output_row = [
									self.t_control.step_counter, 
									self.t_control.dt/self.t_control.time_conversion,
									f"{current_time} / {self.t_control.t_final/self.t_control.time_conversion}",
									0,
									0,
			]
			self.screen.print_row(screen_output_row)

		self.screen.close()

		for output in self.outputs:
			output.save_mesh()






class Simulator_Mout(Simulator):
	"""
    Mechanical-only simulator (linear momentum).

    Solves the momentum equation with possible non-elastic behavior using a
    θ-method loop and fixed-point iterations per step. No thermal coupling.

    Parameters
    ----------
    eq_mom : LinearMomentum
        Configured momentum equation (materials, BCs, solver set).
    t_control : TimeControllerBase
        Time controller providing `t`, `dt`, and loop control.
    outputs : list of SaveFields
        Output writers to initialize and use at each saved time.
    compute_elastic_response : bool, default=True
        If True, starts with a purely elastic solve to initialize fields.

    Attributes
    ----------
    eq_mom : LinearMomentum
    t_control : TimeControllerBase
    outputs : list[SaveFields]
    compute_elastic_response : bool
    """
	def __init__(self, eq_mom: LinearMomentum, 
					   t_control: TimeControllerBase,
					   outputs: list[SaveFields],
					   compute_elastic_response: bool=True):
		self.eq_mom = eq_mom
		self.t_control = t_control
		self.outputs = outputs
		self.compute_elastic_response = compute_elastic_response

		ScreenPrinter.reset_instance()
		self.screen = ScreenPrinter(self.eq_mom.grid, self.eq_mom.solver, self.eq_mom.mat, self.outputs, t_control.time_unit)

	def run(self) -> None:
		"""
        Run the mechanical simulation.

        Workflow
        --------
        1. Initialize outputs and boundary conditions.
        2. Optionally solve a purely elastic step.
        3. Initialize non-elastic rates.
        4. For each time step: assemble/solve, update internal variables and
           rates, compute relevant quantities, and save fields.

        Convergence
        -----------
        Uses a relative change in total strain between iterations as error.
        If `theta == 1.0` or no non-elastic elements exist, iteration ends
        immediately.

        Returns
        -------
        None

        Notes
        -----
        - Printing occurs on rank 0 only.
        - The first `output.save_fields(0)` call uses the last `output`
          from the preceding loop variable.
        """
		# Output field
		for output in self.outputs:
			output.initialize()

		# Update boundary conditions
		self.eq_mom.bc.update_dirichlet(self.t_control.t)
		self.eq_mom.bc.update_neumann(self.t_control.t)

		if self.compute_elastic_response:
			# Solve elasticity
			self.eq_mom.solve_elastic_response()

			# Calculate total (elastic) strain
			eps_tot_to = self.eq_mom.compute_total_strain()

			# Compute stress
			stress_to = self.eq_mom.compute_elastic_stress(eps_tot_to)

		else:
			# Calculate total strain
			eps_tot_to = self.eq_mom.compute_total_strain()

			# Retrieve stress
			stress_to = numpy2torch(self.eq_mom.sig.x.array.reshape((self.eq_mom.n_elems, 3, 3)))

		# Calculate and eps_ie_rate_old
		self.eq_mom.compute_eps_ne_rate(stress_to, self.t_control.t)
		self.eq_mom.update_eps_ne_rate_old()

		# Save fields
		self.eq_mom.compute_p_elems()
		self.eq_mom.compute_q_elems()
		self.eq_mom.compute_p_nodes()
		self.eq_mom.compute_q_nodes()
		output.save_fields(0)

		# Time loop
		while self.t_control.keep_looping():

			# Advance time
			self.t_control.advance_time()
			t = self.t_control.t
			dt = self.t_control.dt

			# Update boundary conditions
			self.eq_mom.bc.update_dirichlet(t)
			self.eq_mom.bc.update_neumann(t)

			# Iterative loop settings
			tol = 1e-8
			error = 2*tol
			ite = 0
			maxiter = 40

			while error > tol and ite < maxiter:

				# Update total strain of previous iteration (eps_tot_k <-- eps_tot)
				eps_tot_k_to = eps_tot_to.clone()

				# Update stress
				stress_k_to = stress_to.clone()

				# Build bi-linear form
				self.eq_mom.solve(stress_k_to, t, dt)

				# Compute total strain
				eps_tot_to = self.eq_mom.compute_total_strain()

				# Compute stress
				stress_to = self.eq_mom.compute_stress(eps_tot_to)

				# Increment internal variables
				self.eq_mom.increment_internal_variables(stress_to, stress_k_to, dt)

				# Compute inelastic strain rates
				self.eq_mom.compute_eps_ne_rate(stress_to, dt)

				# Compute error
				if self.eq_mom.theta == 1.0:
					error = 0.0
				elif len(self.eq_mom.mat.elems_ne) == 0:
					error = 0.0
				else:
					eps_tot_k_flat = to.flatten(eps_tot_k_to)
					eps_tot_flat = to.flatten(eps_tot_to)
					local_error =  np.linalg.norm(eps_tot_k_flat - eps_tot_flat) / np.linalg.norm(eps_tot_flat)
					error = self.eq_mom.grid.mesh.comm.allreduce(local_error, op=MPI.SUM)

				ite += 1

			# Update internal variables
			self.eq_mom.update_internal_variables()

			# Update strain rates
			self.eq_mom.update_eps_ne_rate_old()

			# Update strain
			self.eq_mom.update_eps_ne_old(stress_to, stress_k_to, dt)

			# Save fields
			self.eq_mom.compute_p_elems()
			self.eq_mom.compute_q_elems()
			self.eq_mom.compute_p_nodes()
			self.eq_mom.compute_q_nodes()
			for output in self.outputs:
				output.save_fields(t)

			# Print stuff
			screen_output_row = [
									self.t_control.step_counter, 
									self.t_control.dt/self.t_control.time_conversion,
									f"{t/self.t_control.time_conversion} / {self.t_control.t_final/self.t_control.time_conversion}",
									ite,
									error,
			]
			self.screen.print_row(screen_output_row)

			# if self.eq_mom.grid.mesh.comm.rank == 0:
			# 	print(t/self.t_control.time_unit, ite, error)
			# 	sys.stdout.flush()
			# 	try:
			# 		print(float(self.eq_mom.mat.elems_ne[-1].Fvp.max()))
			# 		sys.stdout.flush()
			# 	except:
			# 		pass

		self.screen.close()
		for output in self.outputs:
			output.save_mesh()





class Simulator_GUI(Simulator):
	"""
	High-level driver to set up and run mechanical simulations from a
	dictionary-based input specification.

	This GUI-friendly wrapper builds the grid, initializes the linear
	momentum equation, sets up PETSc solvers, configures material models
	(elastic and nonelastic), applies gravity and boundary conditions,
	and runs equilibrium and operation stages.

	Parameters
	----------
	input_file : dict
	    Nested configuration dictionary. The following keys are expected:

	    - ``output.path`` : str
	        Root folder where results will be written.
	    - ``grid.path`` : str
	        Directory containing the mesh.
	    - ``grid.name`` : str
	        Mesh base name (without extension) understood by ``GridHandlerGMSH``.
	    - ``time_settings.theta`` : float
	        Generalized-α/θ method parameter for time integration in momentum.
	    - ``time_settings.time_list`` : array_like of float
	        Monotone time stamps (seconds) for the operation stage.
	    - ``body_force.direction`` : int
	        Index of gravity direction (0, 1, or 2).
	    - ``body_force.gravity`` : float
	        Gravity magnitude (consistent units with the model).
	    - ``body_force.density`` : Any
	        Identifier resolvable by ``grid.get_parameter`` to element-wise density.
	    - ``constitutive_model.elastic`` : dict
	        Mapping from element-set names to parameters:
	        ``{"<set>": {"parameters": {"E": <Any>, "nu": <Any>}}}``.
	    - ``constitutive_model.nonelastic`` : dict
	        Mapping from element-set names to nonelastic models. Each entry must
	        define ``"type"`` (``"KelvinVoigt"``, ``"DislocationCreep"``,
	        or ``"ViscoplasticDesai"``), an ``"active"`` flag, optional
	        ``"equilibrium"`` flag, and a ``"parameters"`` block whose keys
	        depend on the chosen model.
	    - ``solver_settings.type`` : {"LU", "KrylovSolver"}
	        Solver family. ``"LU"`` uses a preonly KSP with LU PC.
	    - ``solver_settings.method`` : str, optional
	        PETSc KSP type (e.g., ``"cg"``, ``"gmres"``, ``"bicg"``) if
	        ``type="KrylovSolver"``.
	    - ``solver_settings.preconditioner`` : str, optional
	        PETSc PC type (e.g., ``"asm"``, ``"hypre"``, ``"ilu"``) if
	        ``type="KrylovSolver"``.
	    - ``solver_settings.relative_tolerance`` : float, optional
	        KSP relative tolerance if ``type="KrylovSolver"``.
	    - ``simulation_settings.equilibrium.active`` : bool
	        Whether to run an initial equilibrium stage.
	    - ``simulation_settings.equilibrium.dt_max`` : float
	        Time step for the equilibrium pseudo-time march.
	    - ``simulation_settings.equilibrium.ite_max`` : int
	        Number of pseudo-time iterations for equilibrium.
	    - ``simulation_settings.operation.dt_max`` : float
	        Maximum time step for the operation stage.
	    - ``simulation_settings.operation.hardening`` : bool, optional
	        If ``True`` and using Desai, initialize hardening from current stress.
	    - ``boundary_conditions`` : dict
	        Mapping from boundary names to BC definitions:
	        - Neumann: ``{"type": "neumann", "direction": int, "density": float,
	          "reference_position": array_like (3,), "values": array_like,
	          "component": (ignored), ...}``
	        - Dirichlet: ``{"type": "dirichlet", "component": int,
	          "values": array_like, ...}``

	Attributes
	----------
	input_file : dict
	    Original configuration.
	output_folder : str
	    Output directory (``output.path``).
	grid : GridHandlerGMSH
	    Mesh/grid handler.
	mom_eq : LinearMomentum
	    Linear momentum equation object.
	mat : Material
	    Material container attached to ``mom_eq``.
	g : float
	    Gravity magnitude (signed) used to assemble body forces.

	Notes
	-----
	- This class *mutates* the filesystem by writing results inside
	  ``output_folder`` via the registered output handlers.
	- All parameters referenced with ``grid.get_parameter`` can be scalars,
	  arrays, or field identifiers understood by the grid handler.

	See Also
	--------
	GridHandlerGMSH
	LinearMomentum
	Material
	PETSc.KSP
	"""
	def __init__(self, input_file: dict):
		"""
		Construct the simulator and perform basic initialization steps.

		The initializer stores the input dictionary, sets the output folder,
		builds the grid, initializes the equation, configures the solver,
		sets material properties, and applies gravity.

		Parameters
		----------
		input_file : dict
		    Configuration dictionary. See class docstring for the expected schema.

		Raises
		------
		KeyError
		    If any required key is missing from ``input_file``.
		"""
		self.input_file = input_file

		self.output_folder = self.input_file["output"]["path"]

		self.build_grid()
		self.initialize_equation()
		self.build_solver()
		self.initialize_material()
		self.set_gravity()


	def build_grid(self):
		"""
		Create and attach the grid handler from the input configuration.

		Uses ``grid.path`` and ``grid.name`` to instantiate a ``GridHandlerGMSH``
		object and assigns it to ``self.grid``.

		Raises
		------
		KeyError
		    If ``grid.path`` or ``grid.name`` is missing.
		"""
		grid_path = self.input_file["grid"]["path"]
		grid_name = self.input_file["grid"]["name"]
		self.grid = GridHandlerGMSH(grid_name, grid_path)

	def initialize_equation(self):
		"""
		Initialize the linear momentum equation object.

		Reads the generalized-θ parameter from ``time_settings.theta`` and
		creates ``self.mom_eq = LinearMomentum(self.grid, theta=theta)``.

		Raises
		------
		KeyError
		    If ``time_settings.theta`` is missing.
		"""
		theta = self.input_file["time_settings"]["theta"]
		self.mom_eq = LinearMomentum(self.grid, theta=theta)

	def set_gravity(self):
		"""
		Define and assemble body force due to gravity.

		Constructs a gravity vector aligned with the axis specified by
		``body_force.direction`` and magnitude ``body_force.gravity``.
		The vector is passed to ``self.mom_eq.build_body_force``.

		Raises
		------
		KeyError
		    If ``body_force.direction`` or ``body_force.gravity`` is missing.
		ValueError
		    If the gravity direction is not 0, 1, or 2.
		"""
		g_vec = [0.0, 0.0, 0.0]
		i = self.input_file["body_force"]["direction"]
		self.g = self.input_file["body_force"]["gravity"]
		g_vec[i] = self.g
		self.mom_eq.build_body_force(g_vec)

	def initialize_material(self):
		"""
		Build and attach the elastic material model(s).

		- Creates a ``Material`` container sized to the number of elements.
		- Sets element-wise density from ``body_force.density`` via
		  ``grid.get_parameter``.
		- For each entry in ``constitutive_model.elastic``, queries ``E`` and
		  ``nu``, creates a ``Spring`` element, and registers it into
		  ``self.mat``. Finally, the material is attached to ``self.mom_eq``.

		Raises
		------
		KeyError
		    If required keys under ``constitutive_model.elastic`` or
		    ``body_force.density`` are missing.
		"""
		self.mat = Material(self.grid.n_elems)
		density = self.grid.get_parameter(self.input_file["body_force"]["density"])
		self.mat.set_density(density)

		for elem_name in self.input_file["constitutive_model"]["elastic"].keys():
			E = self.grid.get_parameter(self.input_file["constitutive_model"]["elastic"][elem_name]["parameters"]["E"])
			nu = self.grid.get_parameter(self.input_file["constitutive_model"]["elastic"][elem_name]["parameters"]["nu"])
			spring_0 = Spring(E, nu, elem_name)
			self.mat.add_to_elastic(spring_0)

		self.mom_eq.set_material(self.mat)

	def build_solver(self):
		"""
		Configure and attach the PETSc linear solver.

		Behavior
		--------
		- If ``solver_settings.type == "LU"``:
		  Uses a preonly KSP with LU preconditioner.
		- If ``solver_settings.type == "KrylovSolver"``:
		  Reads ``method``, ``preconditioner``, and ``relative_tolerance``
		  and sets them on the KSP.

		Notes
		-----
		The maximum number of iterations for Krylov solvers is set to 100.

		Raises
		------
		KeyError
		    If required ``solver_settings`` keys are missing.
		ValueError
		    If an unsupported solver type is requested.
		"""
		solver = PETSc.KSP().create(self.grid.mesh.comm)
		if self.input_file["solver_settings"]["type"] == "LU":
			solver.setType("preonly")
			solver.getPC().setType("lu")
		elif self.input_file["solver_settings"]["type"] == "KrylovSolver":
			method = self.input_file["solver_settings"]["method"]
			prec = self.input_file["solver_settings"]["preconditioner"]
			tol = self.input_file["solver_settings"]["relative_tolerance"]
			solver.setType(method)
			solver.getPC().setType(prec)
			solver.setTolerances(rtol=tol, max_it=100)
		self.mom_eq.set_solver(solver)


	def run_equilibrium(self):
		"""
		Run the equilibrium (pseudo-time) stage, if enabled.

		This stage optionally activates nonelastic models flagged with
		``equilibrium: True`` and marches a pseudo-time controller until
		``ite_max`` steps, applying time-constant boundary conditions.
		Results are written under ``<output_folder>/equilibrium``.

		Side Effects
		------------
		- Modifies ``self.mom_eq.mat`` by adding nonelastic elements
		  as specified in the input.
		- Writes displacement and stress fields via ``SaveFields``.

		Raises
		------
		Exception
		    If an unsupported nonelastic element type or BC type is found.
		KeyError
		    If required keys under ``simulation_settings.equilibrium`` or
		    ``boundary_conditions`` are missing.
		"""
		# Build material: non-elastic element
		for elem_name in self.input_file["constitutive_model"]["nonelastic"].keys():
			if self.input_file["constitutive_model"]["nonelastic"][elem_name]["active"]:
				if self.input_file["constitutive_model"]["nonelastic"][elem_name]["equilibrium"]:
					if self.input_file["constitutive_model"]["nonelastic"][elem_name]["type"] == "KelvinVoigt":
						E = self.grid.get_parameter(self.input_file["constitutive_model"]["nonelastic"][elem_name]["parameters"]["E"])
						nu = self.grid.get_parameter(self.input_file["constitutive_model"]["nonelastic"][elem_name]["parameters"]["nu"])
						eta = self.grid.get_parameter(self.input_file["constitutive_model"]["nonelastic"][elem_name]["parameters"]["eta"])
						kelvin = Viscoelastic(eta, E, nu, elem_name)
						self.mom_eq.mat.add_to_non_elastic(kelvin)
					elif self.input_file["constitutive_model"]["nonelastic"][elem_name]["type"] == "DislocationCreep":
						A = self.grid.get_parameter(self.input_file["constitutive_model"]["nonelastic"][elem_name]["parameters"]["A"])
						n = self.grid.get_parameter(self.input_file["constitutive_model"]["nonelastic"][elem_name]["parameters"]["n"])
						Q = self.grid.get_parameter(self.input_file["constitutive_model"]["nonelastic"][elem_name]["parameters"]["Q"])
						creep_0 = DislocationCreep(A, Q, n, elem_name)
						self.mom_eq.mat.add_to_non_elastic(creep_0)
						T = self.grid.get_parameter(self.input_file["constitutive_model"]["nonelastic"][elem_name]["parameters"]["T"])
						self.mom_eq.set_T0(T)
						self.mom_eq.set_T(T)
					elif self.input_file["constitutive_model"]["nonelastic"][elem_name]["type"] == "ViscoplasticDesai":
						mu_1 = self.grid.get_parameter(self.input_file["constitutive_model"]["nonelastic"][elem_name]["parameters"]["mu_1"])
						N_1 = self.grid.get_parameter(self.input_file["constitutive_model"]["nonelastic"][elem_name]["parameters"]["N_1"])
						n = self.grid.get_parameter(self.input_file["constitutive_model"]["nonelastic"][elem_name]["parameters"]["n"])
						a_1 = self.grid.get_parameter(self.input_file["constitutive_model"]["nonelastic"][elem_name]["parameters"]["a_1"])
						eta = self.grid.get_parameter(self.input_file["constitutive_model"]["nonelastic"][elem_name]["parameters"]["eta"])
						beta_1 = self.grid.get_parameter(self.input_file["constitutive_model"]["nonelastic"][elem_name]["parameters"]["beta_1"])
						beta = self.grid.get_parameter(self.input_file["constitutive_model"]["nonelastic"][elem_name]["parameters"]["beta"])
						m = self.grid.get_parameter(self.input_file["constitutive_model"]["nonelastic"][elem_name]["parameters"]["m"])
						gamma = self.grid.get_parameter(self.input_file["constitutive_model"]["nonelastic"][elem_name]["parameters"]["gamma"])
						alpha_0 = self.grid.get_parameter(self.input_file["constitutive_model"]["nonelastic"][elem_name]["parameters"]["alpha_0"])
						sigma_t = self.grid.get_parameter(self.input_file["constitutive_model"]["nonelastic"][elem_name]["parameters"]["sigma_t"])
						desai = ViscoplasticDesai(mu_1, N_1, a_1, eta, n, beta_1, beta, m, gamma, sigma_t, alpha_0, elem_name)
						self.mom_eq.mat.add_to_non_elastic(desai)
					else:
						elem_type = self.input_file["constitutive_model"]["nonelastic"][elem_name]["type"]
						raise Exception(f"Element type {elem_type} not supported.")


		# Time settings for equilibrium stage
		dt = self.input_file["simulation_settings"]["equilibrium"]["dt_max"]
		tf = self.input_file["simulation_settings"]["equilibrium"]["ite_max"]*dt
		tc_equilibrium = TimeController(dt=dt, initial_time=0.0, final_time=tf, time_unit="second")

		# Loop over boundaries
		bc_equilibrium = momBC.BcHandler(self.mom_eq)
		t_values = [0.0, tc_equilibrium.t_final]
		for b_name in self.input_file["boundary_conditions"].keys():
			bc_value = self.input_file["boundary_conditions"][b_name]["values"][0]
			bc_values = bc_value*np.ones(len(t_values))
			if self.input_file["boundary_conditions"][b_name]["type"] == "neumann":
				bc = momBC.NeumannBC(boundary_name = b_name,
									 direction = self.input_file["boundary_conditions"][b_name]["direction"],
									 density = self.input_file["boundary_conditions"][b_name]["density"],
									 ref_pos = self.input_file["boundary_conditions"][b_name]["reference_position"],
									 values = bc_values,
									 time_values = t_values,
									 g = self.g)
			elif self.input_file["boundary_conditions"][b_name]["type"] == "dirichlet":
				bc = momBC.DirichletBC(boundary_name = b_name, 
								 	   component = self.input_file["boundary_conditions"][b_name]["component"],
									   values = bc_values,
									   time_values = t_values)
			else:
				b_type = self.input_file["boundary_conditions"][b_name]["type"]
				raise Exception(f"Boundary condition type {b_type} not supported.")
			bc_equilibrium.add_boundary_condition(bc)

		# Set boundary conditions
		self.mom_eq.set_boundary_conditions(bc_equilibrium)

		# Create output handlers
		output_mom = SaveFields(self.mom_eq)
		output_mom.set_output_folder(os.path.join(self.output_folder, "equilibrium"))
		output_mom.add_output_field("u", "Displacement (m)")
		output_mom.add_output_field("p_elems", "Mean Stress (MPa)")
		outputs = [output_mom]

		# Define simulator
		sim = Simulator_M(self.mom_eq, tc_equilibrium, outputs, compute_elastic_response=True)
		sim.run()

	def element_exist(self, elem_name: str):
		"""
		Check whether a nonelastic element with a given name exists.

		Parameters
		----------
		elem_name : str
		    Element set/name to query.

		Returns
		-------
		bool
		    ``True`` if an element with ``elem_name`` is present in
		    ``self.mom_eq.mat.elems_ne``, ``False`` otherwise.
		"""
		for elem in self.mom_eq.mat.elems_ne:
			if elem.name == elem_name:
				return True
		return False

	def run_operation(self):
		"""
		Run the operation (transient) stage.

		Activates any nonelastic models flagged ``active: True`` (adding only if
		not already present), configures the time controller using
		``time_settings.time_list`` and ``simulation_settings.operation.dt_max``,
		applies time-varying boundary conditions, registers outputs, and runs
		the simulator.

		Side Effects
		------------
		- May add nonelastic elements to the material model.
		- Writes displacement, mean stress, and von Mises stress fields under
		  ``<output_folder>/operation``.

		Raises
		------
		Exception
		    If an unsupported nonelastic element type or BC type is found.
		KeyError
		    If required time, BC, or simulation settings are missing.
		"""
		# Build material: non-elastic element
		for elem_name in self.input_file["constitutive_model"]["nonelastic"].keys():
			if self.input_file["constitutive_model"]["nonelastic"][elem_name]["active"]:
				if self.input_file["constitutive_model"]["nonelastic"][elem_name]["type"] == "KelvinVoigt":
					if not self.element_exist(elem_name):
						E = self.grid.get_parameter(self.input_file["constitutive_model"]["nonelastic"][elem_name]["parameters"]["E"])
						nu = self.grid.get_parameter(self.input_file["constitutive_model"]["nonelastic"][elem_name]["parameters"]["nu"])
						eta = self.grid.get_parameter(self.input_file["constitutive_model"]["nonelastic"][elem_name]["parameters"]["eta"])
						kelvin = Viscoelastic(eta, E, nu, elem_name)
						self.mom_eq.mat.add_to_non_elastic(kelvin)
				elif self.input_file["constitutive_model"]["nonelastic"][elem_name]["type"] == "DislocationCreep":
					if not self.element_exist(elem_name):
						A = self.grid.get_parameter(self.input_file["constitutive_model"]["nonelastic"][elem_name]["parameters"]["A"])
						n = self.grid.get_parameter(self.input_file["constitutive_model"]["nonelastic"][elem_name]["parameters"]["n"])
						Q = self.grid.get_parameter(self.input_file["constitutive_model"]["nonelastic"][elem_name]["parameters"]["Q"])
						creep_0 = DislocationCreep(A, Q, n, elem_name)
						self.mom_eq.mat.add_to_non_elastic(creep_0)
						T = self.grid.get_parameter(self.input_file["constitutive_model"]["nonelastic"][elem_name]["parameters"]["T"])
						self.mom_eq.set_T0(T)
						self.mom_eq.set_T(T)
				elif self.input_file["constitutive_model"]["nonelastic"][elem_name]["type"] == "ViscoplasticDesai":
					if not self.element_exist(elem_name):
						mu_1 = self.grid.get_parameter(self.input_file["constitutive_model"]["nonelastic"][elem_name]["parameters"]["mu_1"])
						N_1 = self.grid.get_parameter(self.input_file["constitutive_model"]["nonelastic"][elem_name]["parameters"]["N_1"])
						n = self.grid.get_parameter(self.input_file["constitutive_model"]["nonelastic"][elem_name]["parameters"]["n"])
						a_1 = self.grid.get_parameter(self.input_file["constitutive_model"]["nonelastic"][elem_name]["parameters"]["a_1"])
						eta = self.grid.get_parameter(self.input_file["constitutive_model"]["nonelastic"][elem_name]["parameters"]["eta"])
						beta_1 = self.grid.get_parameter(self.input_file["constitutive_model"]["nonelastic"][elem_name]["parameters"]["beta_1"])
						beta = self.grid.get_parameter(self.input_file["constitutive_model"]["nonelastic"][elem_name]["parameters"]["beta"])
						m = self.grid.get_parameter(self.input_file["constitutive_model"]["nonelastic"][elem_name]["parameters"]["m"])
						gamma = self.grid.get_parameter(self.input_file["constitutive_model"]["nonelastic"][elem_name]["parameters"]["gamma"])
						alpha_0 = self.grid.get_parameter(self.input_file["constitutive_model"]["nonelastic"][elem_name]["parameters"]["alpha_0"])
						sigma_t = self.grid.get_parameter(self.input_file["constitutive_model"]["nonelastic"][elem_name]["parameters"]["sigma_t"])
						desai = ViscoplasticDesai(mu_1, N_1, a_1, eta, n, beta_1, beta, m, gamma, sigma_t, alpha_0, elem_name)

						if self.input_file["simulation_settings"]["operation"]["hardening"]:
							# Compute initial hardening parameter
							stress_to = numpy2torch(self.mom_eq.sig.x.array.reshape((self.mom_eq.n_elems, 3, 3)))
							desai.compute_initial_hardening(stress_to, Fvp_0=0.0)

						self.mom_eq.mat.add_to_non_elastic(desai)
				else:
					elem_type = self.input_file["constitutive_model"]["nonelastic"][elem_name]["type"]
					raise Exception(f"Element type {elem_type} not supported.")


		# Time settings for operation stage
		t_values = self.input_file["time_settings"]["time_list"]
		dt = self.input_file["simulation_settings"]["operation"]["dt_max"]
		tf = t_values[-1]
		tc_op = TimeController(dt=dt, initial_time=0.0, final_time=tf, time_unit="second")

		# Loop over boundaries
		bc_op = momBC.BcHandler(self.mom_eq)
		for b_name in self.input_file["boundary_conditions"].keys():
			bc_values = self.input_file["boundary_conditions"][b_name]["values"]
			if self.input_file["boundary_conditions"][b_name]["type"] == "neumann":
				bc = momBC.NeumannBC(boundary_name = b_name,
									 direction = self.input_file["boundary_conditions"][b_name]["direction"],
									 density = self.input_file["boundary_conditions"][b_name]["density"],
									 ref_pos = self.input_file["boundary_conditions"][b_name]["reference_position"],
									 values = bc_values,
									 time_values = t_values,
									 g = self.g)
			elif self.input_file["boundary_conditions"][b_name]["type"] == "dirichlet":
				bc = momBC.DirichletBC(boundary_name = b_name, 
								 	   component = self.input_file["boundary_conditions"][b_name]["component"],
									   values = bc_values,
									   time_values = t_values)
			else:
				b_type = self.input_file["boundary_conditions"][b_name]["type"]
				raise Exception(f"Boundary condition type {b_type} not supported.")
			bc_op.add_boundary_condition(bc)

		# Set boundary conditions
		self.mom_eq.set_boundary_conditions(bc_op)

		# Create output handlers
		output_mom = SaveFields(self.mom_eq)
		output_mom.set_output_folder(os.path.join(self.output_folder, "operation"))
		output_mom.add_output_field("u", "Displacement (m)")
		output_mom.add_output_field("p_elems", "Mean Stress (MPa)")
		output_mom.add_output_field("q_elems", "Von Mises Stress (MPa)")
		outputs = [output_mom]

		# Define simulator
		compute_elastic_response = True
		if self.input_file["simulation_settings"]["equilibrium"]["active"] == True:
			compute_elastic_response = False
		sim = Simulator_M(self.mom_eq, tc_op, outputs, compute_elastic_response=compute_elastic_response)
		sim.run()


	def run(self):
		"""
		Execute the full simulation workflow.

		If ``simulation_settings.equilibrium.active`` is ``True``, runs the
		equilibrium stage first and then the operation stage; otherwise,
		runs only the operation stage.

		Returns
		-------
		None
		"""
		if self.input_file["simulation_settings"]["equilibrium"]["active"] == True:
			self.run_equilibrium()
		self.run_operation()