"""
Wizard module for automated processing of mass spectrometry studies.

This module provides the Wizard class for fully automated processing of MS data
from raw files to final study results, including batch conversion, assembly,
alignment, merging, plotting, and export.

The create_script() function allows immediate generation of standalone analysis
scripts without creating a Wizard instance first.

The execute() function combines create_script() with immediate execution of the
generated script for fully automated processing.
"""

from .wizard import Wizard, wizard_def, create_script, execute

__all__ = ["Wizard", "wizard_def", "create_script", "execute"]
