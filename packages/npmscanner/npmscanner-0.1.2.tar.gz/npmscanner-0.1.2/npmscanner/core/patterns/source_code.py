import re
from typing import List
from urllib.parse import urlparse

class SourceCodeHeuristicDetector:
    """Detects malicious patterns in source code"""
    
    def __init__(self, malicious_packages: dict):
        self.malicious_packages = malicious_packages
        self.suspicious_domains = [
            'pastebin.com', 'file.io', 'transfer.sh', 'anonfiles.com',
            'temporary-files.com', 'tmpfiles.org', 'filebin.net'
        ]
        self.suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.onion', '.bit']
    
    def detect_shady_links(self, content: str) -> List[str]:
        """Identify when a package contains URLs to domains with suspicious extensions"""
        findings = []
        
        # Find all URLs in content
        url_pattern = r'https?://[^\s\'"<>]+'
        urls = re.findall(url_pattern, content)
        
        for url in urls:
            try:
                parsed = urlparse(url)
                domain = parsed.netloc.lower()
                
                # Check for suspicious TLDs
                for tld in self.suspicious_tlds:
                    if domain.endswith(tld):
                        findings.append(f"[SHADY-LINKS] Suspicious TLD detected: {url}")
                
                # Check for suspicious domains
                for suspicious_domain in self.suspicious_domains:
                    if suspicious_domain in domain:
                        findings.append(f"[SHADY-LINKS] Suspicious domain detected: {url}")
                
                # Check for IP addresses (often suspicious)
                if re.match(r'^\d+\.\d+\.\d+\.\d+', domain):
                    findings.append(f"[SHADY-LINKS] IP address in URL: {url}")
                    
            except Exception:
                continue
        
        return findings
    
    def detect_obfuscation(self, content: str) -> List[str]:
        """Identify when a package uses common obfuscation methods"""
        findings = []
        
        # Check for hex-encoded variables (common in JS obfuscation)
        hex_vars = re.findall(r'_0x[0-9a-f]{4,}', content)
        if len(hex_vars) > 10:
            findings.append(f"[OBFUSCATION] Heavy hex variable usage: {len(hex_vars)} variables")
        
        # Check for string encryption patterns
        encrypted_strings = re.findall(r'atob\(|btoa\(|fromCharCode|String\.fromCharCode', content)
        if len(encrypted_strings) > 20:
            findings.append(f"[OBFUSCATION] String encryption detected: {len(encrypted_strings)} operations")
        
        # Check for eval usage (common obfuscation technique)
        eval_usage = re.findall(r'eval\s*\(', content)
        if len(eval_usage) > 5:
            findings.append(f"[OBFUSCATION] Excessive eval usage: {len(eval_usage)} calls")
        
        # Check for Function constructor usage
        function_constructor = re.findall(r'new\s+Function\s*\(', content)
        if len(function_constructor) > 3:
            findings.append(f"[OBFUSCATION] Function constructor usage: {len(function_constructor)} calls")
        
        # Check for base64 encoded content
        base64_patterns = re.findall(r'[A-Za-z0-9+/]{20,}={0,2}', content)
        if len(base64_patterns) > 10:
            findings.append(f"[OBFUSCATION] Multiple base64 encoded strings: {len(base64_patterns)}")
        
        return findings
    
    def detect_clipboard_access(self, content: str) -> List[str]:
        """Identify when a package reads or writes data from the clipboard"""
        findings = []
        
        # Check for clipboard API usage
        clipboard_patterns = [
            r'navigator\.clipboard',
            r'clipboard\.writeText',
            r'clipboard\.readText',
            r'document\.execCommand.*copy',
            r'document\.execCommand.*paste'
        ]
        
        for pattern in clipboard_patterns:
            matches = re.findall(pattern, content)
            if matches:
                findings.append(f"[CLIPBOARD-ACCESS] Clipboard operation detected: {pattern}")
        
        return findings
    
    def detect_exfiltrate_sensitive_data(self, content: str) -> List[str]:
        """Identify when a package reads and exfiltrates sensitive data"""
        findings = []
        
        # Check for environment variable access
        env_access = re.findall(r'process\.env\.[A-Z_]+', content)
        if len(env_access) > 5:
            findings.append(f"[EXFILTRATE-SENSITIVE] Environment variable access: {len(env_access)} variables")
        
        # Check for file system access to sensitive locations
        sensitive_paths = [
            r'/etc/passwd', r'/etc/shadow', r'/etc/hosts',
            r'C:\\Windows\\System32', r'C:\\Users',
            r'\.ssh/', r'\.aws/', r'\.npmrc'
        ]
        
        for path_pattern in sensitive_paths:
            if re.search(path_pattern, content):
                findings.append(f"[EXFILTRATE-SENSITIVE] Sensitive path access: {path_pattern}")
        
        # Check for credential-related patterns
        credential_patterns = [
            r'password', r'secret', r'token', r'key', r'credential',
            r'api[_-]?key', r'access[_-]?token'
        ]
        
        for pattern in credential_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if len(matches) > 3:
                findings.append(f"[EXFILTRATE-SENSITIVE] Credential-related patterns: {len(matches)} matches")
        
        return findings
    
    def detect_download_executable(self, content: str) -> List[str]:
        """Identify when a package downloads and makes executable a remote binary"""
        findings = []
        
        # Check for download patterns
        download_patterns = [
            r'fetch\s*\(', r'axios\.get', r'XMLHttpRequest',
            r'wget', r'curl', r'http\.get'
        ]
        
        # Check for executable patterns
        executable_patterns = [
            r'chmod\s*\+x', r'executable', r'\.exe', r'\.bin',
            r'child_process\.exec', r'child_process\.spawn'
        ]
        
        download_found = any(re.search(pattern, content) for pattern in download_patterns)
        executable_found = any(re.search(pattern, content) for pattern in executable_patterns)
        
        if download_found and executable_found:
            findings.append("[DOWNLOAD-EXECUTABLE] Download and execution patterns detected")
        
        return findings
    
    def detect_exec_base64(self, content: str) -> List[str]:
        """Identify when a package dynamically executes base64-encoded code"""
        findings = []
        
        # Look for base64 decode followed by eval/exec
        base64_exec_patterns = [
            r'atob\s*\([^)]+\)\s*\)\s*\)\s*eval',
            r'btoa\s*\([^)]+\)\s*\)\s*\)\s*eval',
            r'base64.*decode.*eval',
            r'eval\s*\(\s*atob\s*\('
        ]
        
        for pattern in base64_exec_patterns:
            if re.search(pattern, content):
                findings.append("[EXEC-BASE64] Base64 decode and execution detected")
        
        return findings
    
    def detect_silent_process_execution(self, content: str) -> List[str]:
        """Identify when a package silently executes an executable"""
        findings = []
        
        # Check for silent execution patterns
        silent_exec_patterns = [
            r'child_process\.exec.*{.*silent.*true',
            r'child_process\.spawn.*{.*stdio.*ignore',
            r'exec.*2>/dev/null',
            r'spawn.*{.*detached.*true'
        ]
        
        for pattern in silent_exec_patterns:
            if re.search(pattern, content):
                findings.append("[SILENT-PROCESS-EXECUTION] Silent process execution detected")
        
        return findings
    
    def detect_dll_hijacking(self, content: str) -> List[str]:
        """Identify when a malicious package manipulates a trusted application into loading a malicious DLL"""
        findings = []
        
        # Check for DLL manipulation patterns
        dll_patterns = [
            r'\.dll', r'LoadLibrary', r'GetProcAddress',
            r'kernel32\.dll', r'user32\.dll'
        ]
        
        for pattern in dll_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                findings.append("[DLL-HIJACKING] DLL manipulation patterns detected")
        
        return findings
    
    def detect_steganography(self, content: str) -> List[str]:
        """Identify when a package retrieves hidden data from an image and executes it"""
        findings = []
        
        # Check for image processing and data extraction
        stego_patterns = [
            r'canvas\.getImageData', r'ImageData', r'getContext.*2d',
            r'hidden.*data', r'steganography', r'extract.*from.*image'
        ]
        
        for pattern in stego_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                findings.append("[STEGANOGRAPHY] Image data extraction patterns detected")
        
        return findings
    
    def detect_code_execution(self, content: str) -> List[str]:
        """Identify when an OS command is executed in setup.py or similar files"""
        findings = []
        
        # Check for OS command execution
        exec_patterns = [
            r'os\.system\s*\(', r'subprocess\.call', r'subprocess\.run',
            r'os\.popen', r'commands\.getoutput'
        ]
        
        for pattern in exec_patterns:
            if re.search(pattern, content):
                findings.append("[CODE-EXECUTION] OS command execution detected")
        
        return findings
    
    def detect_cmd_overwrite(self, content: str) -> List[str]:
        """Identify when the 'install' command is overwritten in setup.py"""
        findings = []
        
        # Check for install command overwriting
        if re.search(r'install.*=.*', content) and 'setup.py' in content:
            findings.append("[CMD-OVERWRITE] Install command overwrite detected in setup.py")
        
        return findings
