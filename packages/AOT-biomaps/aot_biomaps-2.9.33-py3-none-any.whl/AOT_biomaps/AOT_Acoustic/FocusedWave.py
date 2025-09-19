from ._mainAcoustic import AcousticField
from .AcousticEnums import WaveType
from AOT_biomaps.Config import config
import ctypes
import os
import numpy as np
import matplotlib.pyplot as plt
from kwave.ksource import kSource
from kwave.ksensor import kSensor
from kwave.kspaceFirstOrder3D import kspaceFirstOrder3D
from kwave.kspaceFirstOrder2D import kspaceFirstOrder2D
from kwave.options.simulation_options import SimulationOptions
from kwave.options.simulation_execution_options import SimulationExecutionOptions
from tempfile import gettempdir


class FocusedWave(AcousticField):

    def __init__(self, focal_line, **kwargs):
        """
        Initialize the FocusedWave object.

        Parameters:
        - focal_line (tuple): The focal line coordinates (x) in meters.
        - **kwargs: Additional keyword arguments for AcousticField initialization.
        """
        super().__init__(**kwargs)
        self.waveType = WaveType.FocusedWave
        self.kgrid.setTime(int(self.kgrid.Nt*2),self.kgrid.dt) # Extend the time grid to allow for delays
        self.focal_line = focal_line
        self.delayedSignal = self._apply_delay()

    def getName_field(self):
        """
        Generate the name for the field file based on the focal line.

        Returns:
            str: File name for the system matrix file.
        """
        try:
            return f"field_focused_X{self.focal_line*1000:.2f}"
        except Exception as e:
            print(f"Error generating file name: {e}")
            return None

    def _apply_delay(self):
        """
        Apply a temporal delay to focus the wave at a given lateral position (x_focal) and fixed focal depth (Foc).
        Returns:
            ndarray: Delayed signals, shape (nbPiezo, len(burst) + max_delay).
        """
        try:
            # 1. Positions latérales de tous les éléments (en mètres)
            element_positions = np.linspace(self.params['Xrange'][0], self.params['Xrange'][1], self.params['num_elements'])

            # 2. Trouver l'indice de l'élément le plus proche de self.focal_line
            center_idx = np.argmin(np.abs(element_positions - self.focal_line))

            start_idx = max(0, center_idx - self.params['N_piezoFocal'] // 2)
            end_idx = min(self.params['num_elements'] - 1, start_idx + self.params['N_piezoFocal'] - 1)

            # 4. Positions des éléments sélectionnés (en mètres)
            selected_indices = np.arange(start_idx, end_idx + 1)
            selected_positions = element_positions[selected_indices]

            # 5. Distance entre chaque élément sélectionné et le point focal (self.focal_line, self.params['Foc'])
            distances = np.sqrt((self.focal_line - selected_positions)**2 + self.params['Foc']**2)

            # 6. Délais en secondes : (distance_max - distance) / self.params['c0']
            max_distance = np.max(distances)
            delays = (max_distance - distances) / self.params['c0']

            # 7. Conversion en échantillons (vérifier que self.kgrid.dt est en secondes)
            delay_samples = np.round(delays / self.kgrid.dt).astype(int)
            max_delay = np.max(delay_samples)

            # 8. Application des délais
            delayed_signals = np.zeros((self.params['num_elements'], len(self.burst) + max_delay))
            for i, idx in enumerate(selected_indices):
                shift = delay_samples[i]
                delayed_signals[idx, shift:shift + len(self.burst)] = self.burst

            return delayed_signals

        except Exception as e:
            print(f"Error applying delay: {e}")
            return None




        
    def plot_delay(self):
        """
        Plot the time of the maximum of each delayed signal to visualize the wavefront.
        """
        try:
            # Find the index of the maximum for each delayed signal
            max_indices = np.argmax(self.delayedSignal, axis=1)
            element_indices = np.linspace(0, self.params['num_elements'] - 1, self.delayedSignal.shape[0])
            # Convert indices to time
            max_times = max_indices / self.params['f_AQ']

            # Plot the times of the maxima
            plt.figure(figsize=(10, 6))
            plt.plot(element_indices, max_times, 'o-')
            plt.title('Time of Maximum for Each Delayed Signal')
            plt.xlabel('Transducer Element Index')
            plt.ylabel('Time of Maximum (s)')
            plt.grid(True)
            plt.show()
        except Exception as e:
            print(f"Error plotting max times: {e}")


    def _generate_2Dacoustic_field_KWAVE(self, isGPU=True if config.get_process() == 'gpu' else False, show_log=True):
        """
        Generate a 2D acoustic field using k-Wave simulation for a focused wave.
        Parameters:
            - isGPU (bool): Flag indicating whether to use GPU for simulation.
            - show_log (bool): Flag to show simulation logs.
        Returns:
            ndarray: Simulated acoustic field data.
        """
        try:
            # Get the active Conda environment path
            conda_prefix = os.environ.get('CONDA_PREFIX', '')
            if not conda_prefix:
                raise RuntimeError("CONDA_PREFIX not set. Activate your Conda environment first.")

            # Path to libsz.so.2 in the active environment
            libsz_path = os.path.join(conda_prefix, 'lib', 'libsz.so.2')

            # Load the library globally to make it available for kspaceFirstOrder-CUDA
            try:
                ctypes.CDLL(libsz_path, mode=ctypes.RTLD_GLOBAL)
                print(f"Successfully loaded libsz.so.2 from {libsz_path}")
            except OSError as e:
                raise RuntimeError(f"Failed to load libsz.so.2 from {libsz_path}. Install it with: conda install -c conda-forge libaec")

            # Create a source mask for the transducer
            source = kSource()
            source.p_mask = np.zeros((self.params['Nx'], self.params['Nz']))
            source.p = np.zeros((self.params['num_elements'], self.delayedSignal.shape[1]))  # Initialize source pressure

            # Calculate the center of the transducer
            center_index = self.params['Nx'] // 2
            coeff = self.delayedSignal.shape[0] // self.params['num_elements']

            if self.delayedSignal.shape[0] % self.params['num_elements'] != 0:
                raise ValueError("The number of elements must be a divisor of the delayed signal length.")

            # Set the active elements in the source mask
            element_width_grid_points = int(round(self.params['element_width'] / self.params['dx']))

            for i in range(self.params['num_elements']):
                source.p[i] = self.delayedSignal[i * coeff]
                x_pos = center_index - (self.params['num_elements'] // 2) * element_width_grid_points + i * element_width_grid_points
                source.p_mask[x_pos, 0] = 1

            # Define sensors to observe acoustic fields
            sensor = kSensor()
            sensor.mask = np.ones((self.params['Nx'], self.params['Nz']))

            # Simulation options
            simulation_options = SimulationOptions(
                pml_inside=False,
                pml_x_size=20,
                pml_z_size=20,
                use_sg=False,
                save_to_disk=True,
                input_filename=os.path.join(gettempdir(), "KwaveIN.h5"),
                output_filename=os.path.join(gettempdir(), "KwaveOUT.h5")
            )

            execution_options = SimulationExecutionOptions(
                is_gpu_simulation=config.get_process() == 'gpu' and isGPU,
                device_num=config.bestGPU,
                show_sim_log=show_log
            )

            # Run the simulation
            print("Starting simulation...")
            sensor_data = kspaceFirstOrder2D(
                kgrid=self.kgrid,
                medium=self.medium,
                source=source,
                sensor=sensor,
                simulation_options=simulation_options,
                execution_options=execution_options,
            )

            print("Simulation completed successfully.")
            return sensor_data['p'].reshape(self.kgrid.Nt, self.params['Nz'], self.params['Nx'])

        except Exception as e:
            print(f"Error generating 2D acoustic field: {e}")
            return None


    def _generate_3Dacoustic_field_KWAVE(self, isGPU=True if config.get_process() == 'gpu' else False, show_log = True):
        """
        Generate a 3D acoustic field using k-Wave simulation for a focused wave.

        Parameters:
        - isGpu (bool): Flag indicating whether to use GPU for simulation.

        Returns:
            ndarray: Simulated acoustic field data.
        """
        try:
            # Create a source mask for the transducer
            source = kSource()
            source.p_mask = np.zeros((self.params['Nx'], self.params['Ny'], self.params['Nz']))

            # Calculate the center of the transducer
            center_index_x = self.params['Nx'] // 2
            center_index_y = self.params['Ny'] // 2

            # Set the active elements in the source mask
            element_width_grid_points = int(round(self.params['element_width'] / self.params['dx']))
            for i in range(self.params['num_elements']):
                x_pos = center_index_x - (self.params['num_elements'] // 2) * element_width_grid_points + i * element_width_grid_points
                source.p_mask[x_pos, center_index_y, 0] = 1

            # Apply delays to the burst signal using the _apply_delay method
            delayed_signals = self._apply_delay()

            source.p = delayed_signals.T

            # Define sensors to observe acoustic fields
            sensor = kSensor()
            sensor.mask = np.ones((self.params['Nx'], self.params['Ny'], self.params['Nz']))

            # Simulation options
            simulation_options = SimulationOptions(
                pml_inside=False,
                pml_auto=True,
                use_sg=False,
                save_to_disk=True,
                input_filename=os.path.join(gettempdir(), "KwaveIN.h5"),
                output_filename=os.path.join(gettempdir(), "KwaveOUT.h5")
            )

            execution_options = SimulationExecutionOptions(
                is_gpu_simulation=config.get_process() == 'gpu' and isGPU,
                device_num=config.bestGPU,
                show_sim_log= show_log
            )

            # Run the simulation
            print("Starting simulation...")
            sensor_data = kspaceFirstOrder3D(
                kgrid=self.kgrid,
                medium=self.medium,
                source=source,
                sensor=sensor,
                simulation_options=simulation_options,
                execution_options=execution_options,
            )
            print("Simulation completed successfully.")

            return sensor_data['p'].reshape(self.kgrid.Nt, self.params['Nz'], self.params['Ny'], self.params['Nx'])
        except Exception as e:
            print(f"Error generating 3D acoustic field: {e}")
            return None

    def _save2D_HDR_IMG(self, filePath):
        """
        Save the acoustic field to .img and .hdr files.

        Parameters:
        - filePath (str): Path to the folder where files will be saved.
        """
        try:
            t_ex = 1 / self.params['f_US']
            x_focal, z_focal = self.focal_point

            # Define file names (img and hdr)
            file_name = f"field_focused_{x_focal:.2f}_{z_focal:.2f}"

            img_path = os.path.join(filePath, file_name + ".img")
            hdr_path = os.path.join(filePath, file_name + ".hdr")

            # Save the acoustic field to the .img file
            with open(img_path, "wb") as f_img:
                self.field.astype('float32').tofile(f_img)

            # Generate headerFieldGlob
            headerFieldGlob = (
                f"!INTERFILE :=\n"
                f"modality : AOT\n"
                f"voxels number transaxial: {self.field.shape[2]}\n"
                f"voxels number transaxial 2: {self.field.shape[1]}\n"
                f"voxels number axial: {1}\n"
                f"field of view transaxial: {(self.params['Xrange'][1] - self.params['Xrange'][0]) * 1000}\n"
                f"field of view transaxial 2: {(self.params['Zrange'][1] - self.params['Zrange'][0]) * 1000}\n"
                f"field of view axial: {1}\n"
            )

            # Generate header
            header = (
                f"!INTERFILE :=\n"
                f"!imaging modality := AOT\n\n"
                f"!GENERAL DATA :=\n"
                f"!data offset in bytes := 0\n"
                f"!name of data file := system_matrix/{file_name}.img\n\n"
                f"!GENERAL IMAGE DATA\n"
                f"!total number of images := {self.field.shape[0]}\n"
                f"imagedata byte order := LITTLEENDIAN\n"
                f"!number of frame groups := 1\n\n"
                f"!STATIC STUDY (General) :=\n"
                f"number of dimensions := 3\n"
                f"!matrix size [1] := {self.field.shape[2]}\n"
                f"!matrix size [2] := {self.field.shape[1]}\n"
                f"!matrix size [3] := {self.field.shape[0]}\n"
                f"!number format := short float\n"
                f"!number of bytes per pixel := 4\n"
                f"scaling factor (mm/pixel) [1] := {self.params['dx'] * 1000}\n"
                f"scaling factor (mm/pixel) [2] := {self.params['dx'] * 1000}\n"
                f"scaling factor (s/pixel) [3] := {1 / self.params['f_AQ']}\n"
                f"first pixel offset (mm) [1] := {self.params['Xrange'][0] * 1e3}\n"
                f"first pixel offset (mm) [2] := {self.params['Zrange'][0] * 1e3}\n"
                f"first pixel offset (s) [3] := 0\n"
                f"data rescale offset := 0\n"
                f"data rescale slope := 1\n"
                f"quantification units := 1\n\n"
                f"!SPECIFIC PARAMETERS :=\n"
                f"focal point (x, z) := {x_focal}, {z_focal}\n"
                f"number of US transducers := {self.params['num_elements']}\n"
                f"delay (s) := 0\n"
                f"us frequency (Hz) := {self.params['f_US']}\n"
                f"excitation duration (s) := {t_ex}\n"
                f"!END OF INTERFILE :=\n"
            )

            # Save the .hdr file
            with open(hdr_path, "w") as f_hdr:
                f_hdr.write(header)

            with open(os.path.join(filePath, "field.hdr"), "w") as f_hdr2:
                f_hdr2.write(headerFieldGlob)
        except Exception as e:
            print(f"Error saving HDR/IMG files: {e}")
 
