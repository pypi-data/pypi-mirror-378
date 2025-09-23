__version__ = "0.1.1"
__author__ = "Crimson7 Security"
__description__ = "Advanced NPM Security Scanner for supply chain analysis"

from .core import NPMSecurityScanner, PatternDetector
from .reports import HTMLReportGenerator
from .utils import Colors, ColorOutput, load_malicious_packages

__all__ = [
    'NPMSecurityScanner',
    'PatternDetector', 
    'HTMLReportGenerator',
    'Colors',
    'ColorOutput',
    'load_malicious_packages'
]
