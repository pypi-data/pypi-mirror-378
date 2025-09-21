"""
ipSAE: Calculate ipSAE scores for protein-protein interactions in AlphaFold models.

This package provides tools for scoring pairwise protein-protein interactions 
in AlphaFold2 and AlphaFold3 models using the ipSAE metric.
"""

__version__ = "1.0.1"
__author__ = "sameeullah"
__email__ = "sameeullah@bs.qau.edu.pk"

from .core import calculate_ipsae, IpsaeCalculator

__all__ = ["calculate_ipsae", "IpsaeCalculator", "__version__"]
