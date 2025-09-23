import re
from typing import List

class MetadataHeuristicDetector:
    """Detect metadata-based heuristics for package analysis"""
    
    def __init__(self):
        self.popular_packages = [
            'lodash', 'react', 'express', 'axios', 'moment', 'webpack',
            'babel', 'typescript', 'eslint', 'prettier', 'vue', 'angular'
        ]
    
    def detect_empty_information(self, package_data: dict) -> List[str]:
        """Identify packages with empty description field"""
        findings = []
        
        description = package_data.get('description', '')
        if not description or description.strip() == '':
            findings.append("[EMPTY-INFORMATION] Empty description field")
        
        return findings
    
    def detect_release_zero(self, package_data: dict) -> List[str]:
        """Identify packages with release version 0.0 or 0.0.0"""
        findings = []
        
        version = package_data.get('version', '')
        if version in ['0.0', '0.0.0', '0.0.0.0']:
            findings.append(f"[RELEASE-ZERO] Zero version detected: {version}")
        
        return findings
    
    def detect_typosquatting(self, package_name: str) -> List[str]:
        """Identify packages that are named closely to highly popular packages"""
        findings = []
        
        for popular in self.popular_packages:
            if self._levenshtein_distance(package_name.lower(), popular.lower()) == 1:
                findings.append(f"[TYPOSQUATTING] Similar to popular package '{popular}': {package_name}")
        
        return findings
    
    def detect_compromised_email_domain(self, package_data: dict) -> List[str]:
        """Identify when a package maintainer email domain might be compromised"""
        findings = []
        
        # This would require external domain validation
        # For now, check for suspicious email patterns
        author = package_data.get('author', {})
        if isinstance(author, dict):
            email = author.get('email', '')
        else:
            email = str(author)
        
        if email:
            suspicious_domains = ['tempmail.com', '10minutemail.com', 'guerrillamail.com']
            for domain in suspicious_domains:
                if domain in email.lower():
                    findings.append(f"[COMPROMISED-EMAIL] Suspicious email domain: {email}")
        
        return findings
    
    def detect_unclaimed_email_domain(self, package_data: dict) -> List[str]:
        """Identify when a package maintainer email domain is unclaimed"""
        findings = []
        
        # This would require external domain validation
        # For now, check for obviously fake domains
        author = package_data.get('author', {})
        if isinstance(author, dict):
            email = author.get('email', '')
        else:
            email = str(author)
        
        if email:
            fake_domains = ['example.com', 'test.com', 'localhost', 'invalid']
            for domain in fake_domains:
                if domain in email.lower():
                    findings.append(f"[UNCLAIMED-EMAIL] Potentially fake email domain: {email}")
        
        return findings
    
    def detect_repository_integrity_mismatch(self, package_data: dict) -> List[str]:
        """Identify packages with linked GitHub repository where package has extra unexpected files"""
        findings = []
        
        # This would require comparing package contents with repository
        # For now, check for suspicious repository URLs
        repo_url = package_data.get('repository', {}).get('url', '') if isinstance(package_data.get('repository'), dict) else ''
        
        if repo_url:
            suspicious_repos = ['github.com/example', 'github.com/test', 'github.com/fake']
            for suspicious in suspicious_repos:
                if suspicious in repo_url.lower():
                    findings.append(f"[REPOSITORY-INTEGRITY] Suspicious repository URL: {repo_url}")
        
        return findings
    
    def detect_single_python_file(self, package_data: dict) -> List[str]:
        """Identify packages that have only a single Python file"""
        findings = []
        
        # This would require analyzing package contents
        # For now, check for minimal package structure
        files = package_data.get('files', [])
        if len(files) == 1 and files[0].endswith('.py'):
            findings.append("[SINGLE-PYTHON-FILE] Package contains only a single Python file")
        
        return findings
    
    def detect_bundled_binary(self, package_data: dict) -> List[str]:
        """Identify packages bundling binaries"""
        findings = []
        
        # Check for binary file extensions in package
        files = package_data.get('files', [])
        binary_extensions = ['.exe', '.dll', '.so', '.dylib', '.bin']
        
        for file_path in files:
            for ext in binary_extensions:
                if file_path.endswith(ext):
                    findings.append(f"[BUNDLED-BINARY] Binary file detected: {file_path}")
                    break
        
        return findings
    
    def detect_deceptive_author(self, package_data: dict) -> List[str]:
        """Detect when an author is using a disposable email"""
        findings = []
        
        author = package_data.get('author', {})
        if isinstance(author, dict):
            email = author.get('email', '')
        else:
            email = str(author)
        
        if email:
            disposable_domains = [
                'tempmail.com', '10minutemail.com', 'guerrillamail.com',
                'mailinator.com', 'yopmail.com', 'temp-mail.org'
            ]
            
            for domain in disposable_domains:
                if domain in email.lower():
                    findings.append(f"[DECEPTIVE-AUTHOR] Disposable email detected: {email}")
        
        return findings
    
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
