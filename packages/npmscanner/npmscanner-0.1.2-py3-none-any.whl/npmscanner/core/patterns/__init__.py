"""
Pattern detection utilities for the Crimson7 NPM Security Scanner
Enhanced with comprehensive heuristic detection for Python and npm packages
"""

import re
import json
import base64
import hashlib
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse

# Import the original PatternDetector and other classes for backward compatibility
from .source_code import SourceCodeHeuristicDetector
from .metadata import MetadataHeuristicDetector
from .npm_specific import NPMHeuristicDetector
from .unified_analyzer import UnifiedHeuristicAnalyzer

# Re-export the original classes for backward compatibility
class PatternDetector:
    """Detects malicious patterns in JavaScript code - Legacy compatibility"""
    
    def __init__(self, malicious_packages: dict):
        self.malicious_packages = malicious_packages
        self.source_code_detector = SourceCodeHeuristicDetector(malicious_packages)
    
    def test_malicious_package(self, package_name: str, version: str) -> dict:
        """Check if package version is malicious"""
        for malicious_pkg in self.malicious_packages['malicious_packages']:
            if malicious_pkg['name'] == package_name:
                # Check new format (malicious_versions array)
                if 'malicious_versions' in malicious_pkg:
                    if version in malicious_pkg['malicious_versions']:
                        incident = malicious_pkg.get('incident', 'unknown')
                        return {
                            'Status': 'MALICIOUS',
                            'Details': f"Exact match for compromised version {version} (Incident: {incident})",
                            'Severity': malicious_pkg.get('severity', 'high'),
                            'Incident': incident
                        }
                # Check old format (malicious_version string)
                elif 'malicious_version' in malicious_pkg and malicious_pkg['malicious_version'] == version:
                    incident = malicious_pkg.get('incident', 'unknown')
                    return {
                        'Status': 'MALICIOUS',
                        'Details': f"Exact match for compromised version {version} (Incident: {incident})",
                        'Severity': malicious_pkg.get('severity', 'high'),
                        'Incident': incident
                    }
        return None
    
    def test_obfuscation_patterns(self, content: str) -> List[str]:
        """Scan JavaScript content for obfuscation patterns"""
        return self.source_code_detector.detect_obfuscation(content)
    
    def test_shai_hulud_patterns(self, content: str) -> List[str]:
        """Detect Shai Hulud worm patterns"""
        suspicious_patterns = []
        
        # Check for GitHub Actions manipulation
        if re.search(r'github\.actions|workflow_dispatch|\.github/workflows', content):
            suspicious_patterns.append("[SHAI-HULUD] GitHub Actions manipulation detected")
        
        # Check for secret stealing patterns
        if re.search(r'secrets\.GITHUB_TOKEN|npm_token|NPM_TOKEN|process\.env\.(NPM|GITHUB)', content):
            suspicious_patterns.append("[SHAI-HULUD] Token/secret stealing code detected")
        
        # Check for repository manipulation
        if re.search(r'repos/.*/actions|repos/.*/secrets|repos/.*/visibility|repository\.public', content):
            suspicious_patterns.append("[SHAI-HULUD] Repository manipulation API calls detected")
        
        # Check for npm publish automation
        if re.search(r'npm\s+publish|npm\s+version|npm\s+login', content):
            suspicious_patterns.append("[SHAI-HULUD] Automated npm publishing code detected")
        
        # Check for self-propagation patterns
        if re.search(r'self-propagat|worm|shai-?hulud|exfiltrat', content):
            suspicious_patterns.append("[SHAI-HULUD] Self-propagation indicators found")
        
        # Check for octokit (GitHub API library)
        if re.search(r'octokit|@octokit/rest|github\.com/api', content):
            suspicious_patterns.append("[SHAI-HULUD] GitHub API manipulation library detected")
        
        return suspicious_patterns
    
    def comprehensive_scan(self, content: str) -> dict:
        """Perform comprehensive malware scan using all detection methods"""
        all_findings = []
        
        # Run all detection methods
        all_findings.extend(self.test_obfuscation_patterns(content))
        all_findings.extend(self.test_shai_hulud_patterns(content))
        
        # Calculate risk score
        risk_score, risk_level = self._calculate_risk_score(all_findings)
        
        return {
            'findings': all_findings,
            'risk_score': risk_score,
            'risk_level': risk_level,
            'total_findings': len(all_findings),
            'categories': {
                'obfuscation': len([f for f in all_findings if 'obfuscation' in f.lower()]),
                'worm': len([f for f in all_findings if 'shai-hulud' in f.lower()]),
            }
        }
    
    def _calculate_risk_score(self, findings: List[str]) -> tuple:
        """Calculate risk score based on findings"""
        if not findings:
            return 0, "LOW"
        
        # Weight different types of findings
        critical_patterns = ['malicious', 'shai-hulud']
        high_patterns = ['obfuscation']
        
        score = 0
        for finding in findings:
            finding_lower = finding.lower()
            if any(pattern in finding_lower for pattern in critical_patterns):
                score += 10
            elif any(pattern in finding_lower for pattern in high_patterns):
                score += 7
            else:
                score += 1
        
        # Determine risk level
        if score >= 50:
            return score, "CRITICAL"
        elif score >= 30:
            return score, "HIGH"
        elif score >= 15:
            return score, "MEDIUM"
        else:
            return score, "LOW"

class BehavioralAnalyzer:
    """Analyzes package behavior for suspicious activities"""
    
    def __init__(self, malicious_packages: dict):
        self.malicious_packages = malicious_packages
    
    def analyze_package_metadata(self, package_json: dict) -> List[str]:
        """Analyze package.json for suspicious metadata"""
        findings = []
        
        # Check for suspicious package names
        name = package_json.get('name', '')
        if any(suspicious in name.lower() for suspicious in ['test', 'temp', 'tmp', 'debug', 'hack', 'exploit']):
            findings.append(f"[BEHAVIORAL] Suspicious package name: {name}")
        
        # Check for missing or suspicious author
        author = package_json.get('author', '')
        if not author or len(str(author)) < 3:
            findings.append("[BEHAVIORAL] Missing or suspicious author information")
        
        # Check for suspicious version patterns
        version = package_json.get('version', '')
        if re.match(r'^\d+\.\d+\.\d+liberty-\d+$', version):
            findings.append(f"[BEHAVIORAL] Suspicious version pattern: {version}")
        
        # Check for excessive dependencies
        deps = package_json.get('dependencies', {})
        dev_deps = package_json.get('devDependencies', {})
        total_deps = len(deps) + len(dev_deps)
        
        if total_deps > 50:
            findings.append(f"[BEHAVIORAL] Excessive dependencies: {total_deps} total dependencies")
        
        # Check for suspicious scripts
        scripts = package_json.get('scripts', {})
        for script_name, script_content in scripts.items():
            if any(suspicious in script_content.lower() for suspicious in ['curl', 'wget', 'powershell', 'cmd', 'bash']):
                findings.append(f"[BEHAVIORAL] Suspicious script '{script_name}': {script_content}")
        
        return findings
    
    def calculate_behavioral_risk(self, package_json: dict, content: str) -> dict:
        """Calculate overall behavioral risk score"""
        all_findings = []
        
        # Run all behavioral analysis
        all_findings.extend(self.analyze_package_metadata(package_json))
        
        # Calculate risk score
        risk_score = len(all_findings) * 5  # Each finding adds 5 points
        
        if risk_score >= 50:
            risk_level = "CRITICAL"
        elif risk_score >= 30:
            risk_level = "HIGH"
        elif risk_score >= 15:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return {
            'behavioral_findings': all_findings,
            'behavioral_risk_score': risk_score,
            'behavioral_risk_level': risk_level,
            'total_behavioral_issues': len(all_findings)
        }

class VulnerabilityChecker:
    """Check packages against vulnerability databases"""
    
    def __init__(self):
        self.known_vulnerabilities = {
            'lodash': ['4.17.20', '4.17.19', '4.17.18'],
            'axios': ['0.21.0', '0.20.0'],
            'express': ['4.17.0', '4.16.4'],
            'react': ['16.13.0', '16.12.0'],
            'moment': ['2.29.1', '2.29.0']
        }
    
    def check_known_vulnerabilities(self, package_name: str, version: str) -> List[str]:
        """Check against known vulnerability database"""
        findings = []
        
        if package_name in self.known_vulnerabilities:
            vulnerable_versions = self.known_vulnerabilities[package_name]
            if version in vulnerable_versions:
                findings.append(f"[VULNERABILITY] Known vulnerable version: {package_name}@{version}")
        
        return findings
    
    def check_version_patterns(self, package_name: str, version: str) -> List[str]:
        """Check for suspicious version patterns"""
        findings = []
        
        # Check for pre-release versions with suspicious patterns
        if re.match(r'.*-(alpha|beta|rc)\d*$', version):
            findings.append(f"[VULNERABILITY] Pre-release version: {package_name}@{version}")
        
        # Check for very old versions
        if re.match(r'^0\.[0-9]\.[0-9]$', version):
            findings.append(f"[VULNERABILITY] Very old version: {package_name}@{version}")
        
        return findings

class DependencyAnalyzer:
    """Analyze dependency chains for risks"""
    
    def __init__(self, malicious_packages: dict):
        self.malicious_packages = malicious_packages
    
    def analyze_dependency_tree(self, package_json: dict) -> List[str]:
        """Analyze the entire dependency tree"""
        findings = []
        
        dependencies = package_json.get('dependencies', {})
        dev_dependencies = package_json.get('devDependencies', {})
        
        # Check for dependency confusion risks
        for dep_name in dependencies.keys():
            if self._is_potential_typosquatting(dep_name):
                findings.append(f"[DEPENDENCY] Potential typosquatting: {dep_name}")
        
        # Check for circular dependencies
        if self._has_circular_dependencies(dependencies):
            findings.append("[DEPENDENCY] Potential circular dependencies detected")
        
        # Check for excessive transitive dependencies
        total_deps = len(dependencies) + len(dev_dependencies)
        if total_deps > 100:
            findings.append(f"[DEPENDENCY] Excessive dependencies: {total_deps} total")
        
        return findings
    
    def _is_potential_typosquatting(self, package_name: str) -> bool:
        """Check if package name might be typosquatting"""
        popular_packages = ['lodash', 'react', 'express', 'axios', 'moment', 'webpack']
        
        for popular in popular_packages:
            # Check for similar names with small differences
            if self._levenshtein_distance(package_name, popular) == 1 and package_name != popular:
                return True
        
        return False
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def _has_circular_dependencies(self, dependencies: dict) -> bool:
        """Simple check for potential circular dependencies"""
        # This is a simplified check - in practice, would need full dependency resolution
        dep_names = list(dependencies.keys())
        
        # Check if any dependency name appears to reference the current package
        for dep in dep_names:
            if any(other_dep in dep for other_dep in dep_names if other_dep != dep):
                return True
        
        return False

# Export all classes
__all__ = [
    'PatternDetector', 'BehavioralAnalyzer', 'VulnerabilityChecker', 'DependencyAnalyzer',
    'SourceCodeHeuristicDetector', 'MetadataHeuristicDetector', 'NPMHeuristicDetector',
    'UnifiedHeuristicAnalyzer'
]
