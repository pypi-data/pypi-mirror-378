import os
import warnings
import torch
import ctypes
import platform

# ACOUSTIC
from .AOT_Acoustic._mainAcoustic import *
from .AOT_Acoustic.AcousticEnums import *
from .AOT_Acoustic.AcousticTools import *
from .AOT_Acoustic.FocusedWave import *
from .AOT_Acoustic.IrregularWave import *
from .AOT_Acoustic.PlaneWave import *
from .AOT_Acoustic.StructuredWave import *
# EXPERIMENT
from .AOT_Experiment._mainExperiment import *
from .AOT_Experiment.Focus import *
from .AOT_Experiment.Tomography import *
# OPTIC
from .AOT_Optic._mainOptic import *
from .AOT_Optic.Absorber import *
from .AOT_Optic.Laser import *
from .AOT_Optic.OpticEnums import *
# RECONSTRUCTION
from .AOT_Recon._mainRecon import *
from .AOT_Recon.AlgebraicRecon import *
from .AOT_Recon.AnalyticRecon import *
from .AOT_Recon.BayesianRecon import *
from .AOT_Recon.DeepLearningRecon import *
from .AOT_Recon.PrimalDualRecon import *
from .AOT_Recon.ReconEnums import *
from .AOT_Recon.ReconTools import *
# OPTIMIZERS
from .AOT_Recon.AOT_Optimizers.DEPIERRO import *
from .AOT_Recon.AOT_Optimizers.MAPEM import *
from .AOT_Recon.AOT_Optimizers.MLEM import *
from .AOT_Recon.AOT_Optimizers.PDHG import *
# POTENTIAL FUNCTIONS
from .AOT_Recon.AOT_PotentialFunctions.Huber import *
from .AOT_Recon.AOT_PotentialFunctions.Quadratic import *
from .AOT_Recon.AOT_PotentialFunctions.RelativeDifferences import *
# CONFIG AND SETTINGS
from .Config import config
from .Settings import *

__version__ = '2.9.68'
__process__ = config.get_process()  # Initialise avec la valeur actuelle de config

def initialize(process=None):
    """
    Initialise ou modifie le backend de calcul (GPU/CPU).
    Args:
        process (str, optional): 'gpu' pour forcer le GPU, 'cpu' pour forcer le CPU.
                                 Si None, utilise la configuration actuelle.
    Raises:
        ValueError: Si `process` n'est pas 'cpu' ou 'gpu'.
    """
    ##### Setup to ensure libsz is found by subprocesses #####
    conda_prefix = os.environ.get('CONDA_PREFIX', '')
    if not conda_prefix:
        raise RuntimeError("CONDA_PREFIX not set. Activate your Conda environment first.")

    # Détermine le nom de la bibliothèque et la variable d'environnement selon l'OS
    if platform.system() == 'Windows':
        libsz_name = 'libsz.dll'
        env_var = 'PATH'
        lib_path = os.path.join(conda_prefix, 'Library', 'bin')
    else:  # Linux/Mac
        libsz_name = 'libsz.so.2'
        env_var = 'LD_LIBRARY_PATH'
        lib_path = os.path.join(conda_prefix, 'lib')

    # Chemin complet vers la bibliothèque
    libsz_path = os.path.join(lib_path, libsz_name)

    # Ajoute le chemin de la bibliothèque à la variable d'environnement appropriée
    if env_var in os.environ:
        os.environ[env_var] = f"{lib_path}{os.pathsep}{os.environ[env_var]}"
    else:
        os.environ[env_var] = lib_path

    # Charge la bibliothèque
    try:
        ctypes.CDLL(libsz_path, mode=ctypes.RTLD_GLOBAL)
    except OSError as e:
        raise RuntimeError(
            f"Failed to load {libsz_name} from {libsz_path}. "
            f"Install it with: conda install -c conda-forge libaec"
        )

    ###############################################################
    global __process__
    if process is not None:
        if process not in ['cpu', 'gpu']:
            raise ValueError("process must be 'cpu' or 'gpu'")
        config.set_process(process)
        __process__ = process

    # Vérifications et warnings si nécessaire
    if __process__ == 'gpu':
        try:
            if not torch.cuda.is_available():
                warnings.warn("GPU requested but PyTorch cannot access it. Falling back to CPU.", UserWarning)
                config.set_process('cpu')
                __process__ = 'cpu'
        except ImportError:
            warnings.warn("PyTorch not installed. Falling back to CPU.", UserWarning)
            config.set_process('cpu')
            __process__ = 'cpu'
    return __process__
