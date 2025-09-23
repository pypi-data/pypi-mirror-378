from typing import List, Dict, Tuple
from .source_code import SourceCodeHeuristicDetector
from .metadata import MetadataHeuristicDetector
from .npm_specific import NPMHeuristicDetector

class UnifiedHeuristicAnalyzer:
    """Unified analyzer that combines all heuristic detection methods"""
    
    def __init__(self, malicious_packages: dict):
        self.source_code_detector = SourceCodeHeuristicDetector(malicious_packages)
        self.metadata_detector = MetadataHeuristicDetector()
        self.npm_detector = NPMHeuristicDetector()
    
    def analyze_package_comprehensive(self, content: str, package_data: dict = None) -> Dict:
        """Perform comprehensive heuristic analysis on a package"""
        all_findings = []
        
        # Source code heuristics
        all_findings.extend(self.source_code_detector.detect_shady_links(content))
        all_findings.extend(self.source_code_detector.detect_obfuscation(content))
        all_findings.extend(self.source_code_detector.detect_clipboard_access(content))
        all_findings.extend(self.source_code_detector.detect_exfiltrate_sensitive_data(content))
        all_findings.extend(self.source_code_detector.detect_download_executable(content))
        all_findings.extend(self.source_code_detector.detect_exec_base64(content))
        all_findings.extend(self.source_code_detector.detect_silent_process_execution(content))
        all_findings.extend(self.source_code_detector.detect_dll_hijacking(content))
        all_findings.extend(self.source_code_detector.detect_steganography(content))
        all_findings.extend(self.source_code_detector.detect_code_execution(content))
        all_findings.extend(self.source_code_detector.detect_cmd_overwrite(content))
        
        # NPM-specific heuristics
        all_findings.extend(self.npm_detector.detect_npm_serialize_environment(content))
        all_findings.extend(self.npm_detector.detect_npm_obfuscation(content))
        all_findings.extend(self.npm_detector.detect_npm_install_script(content))
        all_findings.extend(self.npm_detector.detect_npm_steganography(content))
        all_findings.extend(self.npm_detector.detect_npm_dll_hijacking(content))
        all_findings.extend(self.npm_detector.detect_npm_exfiltrate_sensitive_data(content))
        
        # Metadata heuristics (if package_data provided)
        if package_data:
            all_findings.extend(self.metadata_detector.detect_empty_information(package_data))
            all_findings.extend(self.metadata_detector.detect_release_zero(package_data))
            all_findings.extend(self.metadata_detector.detect_typosquatting(package_data.get('name', '')))
            all_findings.extend(self.metadata_detector.detect_compromised_email_domain(package_data))
            all_findings.extend(self.metadata_detector.detect_unclaimed_email_domain(package_data))
            all_findings.extend(self.metadata_detector.detect_repository_integrity_mismatch(package_data))
            all_findings.extend(self.metadata_detector.detect_single_python_file(package_data))
            all_findings.extend(self.metadata_detector.detect_bundled_binary(package_data))
            all_findings.extend(self.metadata_detector.detect_deceptive_author(package_data))
        
        # Calculate risk score
        risk_score, risk_level = self._calculate_heuristic_risk_score(all_findings)
        
        return {
            'findings': all_findings,
            'risk_score': risk_score,
            'risk_level': risk_level,
            'total_findings': len(all_findings),
            'categories': self._categorize_findings(all_findings)
        }
    
    def _calculate_heuristic_risk_score(self, findings: List[str]) -> Tuple[int, str]:
        """Calculate risk score based on heuristic findings"""
        if not findings:
            return 0, "LOW"
        
        # Weight different types of findings
        critical_patterns = ['malicious', 'exfiltrate', 'download-executable', 'exec-base64']
        high_patterns = ['obfuscation', 'silent-process', 'dll-hijacking', 'steganography']
        medium_patterns = ['shady-links', 'clipboard-access', 'typosquatting']
        
        score = 0
        for finding in findings:
            finding_lower = finding.lower()
            if any(pattern in finding_lower for pattern in critical_patterns):
                score += 15
            elif any(pattern in finding_lower for pattern in high_patterns):
                score += 10
            elif any(pattern in finding_lower for pattern in medium_patterns):
                score += 5
            else:
                score += 2
        
        # Determine risk level
        if score >= 75:
            return score, "CRITICAL"
        elif score >= 50:
            return score, "HIGH"
        elif score >= 25:
            return score, "MEDIUM"
        else:
            return score, "LOW"
    
    def _categorize_findings(self, findings: List[str]) -> Dict:
        """Categorize findings by type"""
        categories = {
            'source_code': 0,
            'metadata': 0,
            'npm_specific': 0,
            'obfuscation': 0,
            'exfiltration': 0,
            'execution': 0,
            'network': 0
        }
        
        for finding in findings:
            finding_lower = finding.lower()
            if 'obfuscation' in finding_lower:
                categories['obfuscation'] += 1
            elif 'exfiltrate' in finding_lower:
                categories['exfiltration'] += 1
            elif any(exec_term in finding_lower for exec_term in ['exec', 'execute', 'eval']):
                categories['execution'] += 1
            elif any(net_term in finding_lower for net_term in ['url', 'http', 'fetch', 'network']):
                categories['network'] += 1
            elif 'npm' in finding_lower:
                categories['npm_specific'] += 1
            elif any(meta_term in finding_lower for meta_term in ['empty', 'version', 'author', 'email']):
                categories['metadata'] += 1
            else:
                categories['source_code'] += 1
        
        return categories
