import re
from typing import List

class NPMHeuristicDetector:
    """Enhanced npm-specific heuristic detection"""
    
    def __init__(self):
        pass
    
    def detect_npm_serialize_environment(self, content: str) -> List[str]:
        """Identify when a package serializes 'process.env' to exfiltrate environment variables"""
        findings = []
        
        # Check for process.env serialization
        env_serialize_patterns = [
            r'JSON\.stringify\s*\(\s*process\.env',
            r'JSON\.parse\s*\(\s*process\.env',
            r'process\.env.*JSON',
            r'serialize.*process\.env'
        ]
        
        for pattern in env_serialize_patterns:
            if re.search(pattern, content):
                findings.append("[NPM-SERIALIZE-ENVIRONMENT] Environment variable serialization detected")
        
        return findings
    
    def detect_npm_obfuscation(self, content: str) -> List[str]:
        """Identify when a package uses common obfuscation methods"""
        findings = []
        
        # Check for npm-specific obfuscation patterns
        npm_obfuscation_patterns = [
            r'require\s*\(\s*["\'][^"\']*["\']\s*\)',
            r'eval\s*\(\s*require\s*\(',
            r'Function\s*\(\s*["\'][^"\']*["\']\s*\)'
        ]
        
        for pattern in npm_obfuscation_patterns:
            matches = re.findall(pattern, content)
            if len(matches) > 5:
                findings.append(f"[NPM-OBFUSCATION] NPM obfuscation patterns: {len(matches)} matches")
        
        return findings
    
    def detect_npm_install_script(self, content: str) -> List[str]:
        """Identify when a package has pre or post-install scripts"""
        findings = []
        
        # Check for install scripts in package.json
        if 'package.json' in content or 'scripts' in content:
            install_scripts = [
                r'"preinstall"', r'"postinstall"', r'"install"',
                r'"prepublish"', r'"prepack"', r'"postpack"'
            ]
            
            for script in install_scripts:
                if re.search(script, content):
                    findings.append(f"[NPM-INSTALL-SCRIPT] Install script detected: {script}")
        
        return findings
    
    def detect_npm_steganography(self, content: str) -> List[str]:
        """Identify when a package retrieves hidden data from an image and executes it"""
        findings = []
        
        # Check for image processing in npm context
        npm_stego_patterns = [
            r'canvas.*getImageData', r'ImageData.*canvas',
            r'hidden.*data.*image', r'steganography.*npm'
        ]
        
        for pattern in npm_stego_patterns:
            if re.search(pattern, content):
                findings.append("[NPM-STEGANOGRAPHY] Image steganography patterns detected")
        
        return findings
    
    def detect_npm_dll_hijacking(self, content: str) -> List[str]:
        """Identify when a malicious package manipulates a trusted application into loading a malicious DLL"""
        findings = []
        
        # Check for DLL manipulation in npm context
        npm_dll_patterns = [
            r'\.dll.*require', r'require.*\.dll',
            r'LoadLibrary.*npm', r'npm.*LoadLibrary'
        ]
        
        for pattern in npm_dll_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                findings.append("[NPM-DLL-HIJACKING] DLL manipulation in npm context detected")
        
        return findings
    
    def detect_npm_exfiltrate_sensitive_data(self, content: str) -> List[str]:
        """Identify when a package reads and exfiltrates sensitive data"""
        findings = []
        
        # Check for npm-specific sensitive data access
        npm_sensitive_patterns = [
            r'\.npmrc', r'npm.*config', r'npm.*token',
            r'package-lock\.json', r'yarn\.lock'
        ]
        
        for pattern in npm_sensitive_patterns:
            if re.search(pattern, content):
                findings.append(f"[NPM-EXFILTRATE-SENSITIVE] NPM sensitive data access: {pattern}")
        
        return findings
