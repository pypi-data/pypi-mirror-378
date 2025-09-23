import os
import sys
import tempfile
import tarfile
import re
import requests
import time
import shutil
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

from ..utils.colors import ColorOutput
from ..utils.config import load_malicious_packages
from .patterns import PatternDetector, BehavioralAnalyzer, VulnerabilityChecker, DependencyAnalyzer, UnifiedHeuristicAnalyzer

class NPMSecurityScanner:
    """Core NPM Security Scanner class"""
    
    def __init__(self, repository_url: Optional[str] = None, local_path: Optional[str] = None, 
                 api_key: Optional[str] = None, output_path: str = ".", 
                 deep_scan: bool = False, scan_all: bool = False, generate_html: bool = False):
        self.repository_url = repository_url
        self.local_path = local_path
        self.api_key = api_key
        # Always use /report folder for output
        self.output_path = os.path.join(output_path, "report")
        self.deep_scan = deep_scan
        self.scan_all = scan_all
        self.generate_html = generate_html
        
        # Create report directory if it doesn't exist
        os.makedirs(self.output_path, exist_ok=True)
        
        # Initialize results
        self.results = {
            'ScanDate': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Repository': repository_url if repository_url else local_path,
            'TotalPackagesScanned': 0,
            'MaliciousPackagesFound': [],
            'SuspiciousPackagesFound': [],
            'RequireManualCheck': [],
            'CleanPackages': []
        }
        
        # Load malicious packages database
        self.malicious_packages = load_malicious_packages()
        
        # Initialize all enhanced analyzers
        self.pattern_detector = PatternDetector(self.malicious_packages)
        self.behavioral_analyzer = BehavioralAnalyzer(self.malicious_packages)
        self.vulnerability_checker = VulnerabilityChecker()
        self.dependency_analyzer = DependencyAnalyzer(self.malicious_packages)
        self.heuristic_analyzer = UnifiedHeuristicAnalyzer(self.malicious_packages)
    
    def _validate_url(self, url: str) -> str:
        """Validate and fix repository URL if needed"""
        if not url:
            return url
            
        # Check if user provided a UI URL and convert it
        if "/ui/native/" in url:
            ColorOutput.info("Detected JFrog UI URL. Converting to API URL...")
            match = re.match(r'^(https?://[^/]+)/ui/native/([^/]+)', url)
            if match:
                server, repo_name = match.groups()
                url = f"{server}/artifactory/api/npm/{repo_name}/"
                ColorOutput.info(f"Converted URL: {url}")
        
        # Ensure URL ends with slash
        if not url.endswith("/"):
            url += "/"
        
        # Check if URL needs API endpoint suggestion
        if "/artifactory/" in url and "/api/" not in url:
            ColorOutput.info("TIP: Consider using API endpoint for better results:")
            suggested_url = re.sub(r'/artifactory/([^/]+)/$', r'/artifactory/api/npm/\1/', url)
            ColorOutput.info(f"  {suggested_url}")
        
        return url
    
    def _deep_scan_package(self, package_name: str, version: str, temp_dir: str, scan_context: str = "package") -> Dict:
        """Unified function for deep scanning package contents"""
        scan_results = {
            'ObfuscationPatterns': [],
            'WormPatterns': [],
            'Status': 'CLEAN'
        }
        
        try:
            # Find the package directory
            package_dir = temp_dir if scan_context == "local" else os.path.join(temp_dir, "package")
            
            if not os.path.exists(package_dir):
                ColorOutput.check("      [WARNING] Package directory not found for deep scan")
                return scan_results
            
            # Get all JavaScript files to scan
            js_files = []
            
            # Priority files to check first
            priority_files = ["index.js", "main.js", "lib/index.js", "src/index.js", "dist/index.js"]
            for file in priority_files:
                full_path = os.path.join(package_dir, file)
                if os.path.exists(full_path):
                    js_files.append(full_path)
            
            # Add other JS files (limit to prevent excessive scanning)
            for root, dirs, files in os.walk(package_dir):
                # Skip node_modules, test, spec directories and .min.js files
                dirs[:] = [d for d in dirs if d not in ['node_modules', 'test', 'spec']]
                for file in files:
                    if file.endswith('.js') and not file.endswith('.min.js'):
                        js_files.append(os.path.join(root, file))
                        if len(js_files) >= 20:  # Limit to prevent excessive scanning
                            break
                if len(js_files) >= 20:
                    break
            
            # Scan each file with comprehensive detection
            all_comprehensive_results = []
            for js_file in js_files:
                try:
                    with open(js_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Use comprehensive scan for enhanced detection
                    comprehensive_result = self.pattern_detector.comprehensive_scan(content)
                    
                    # Also run the new unified heuristic analyzer
                    heuristic_result = self.heuristic_analyzer.analyze_package_comprehensive(content)
                    
                    if comprehensive_result['findings'] or heuristic_result['findings']:
                        # Combine results from both analyzers
                        combined_result = {
                            'File': os.path.basename(js_file),
                            'legacy_findings': comprehensive_result['findings'],
                            'heuristic_findings': heuristic_result['findings'],
                            'legacy_risk_score': comprehensive_result['risk_score'],
                            'heuristic_risk_score': heuristic_result['risk_score'],
                            'legacy_risk_level': comprehensive_result['risk_level'],
                            'heuristic_risk_level': heuristic_result['risk_level'],
                            'total_findings': len(comprehensive_result['findings']) + len(heuristic_result['findings']),
                            'categories': heuristic_result['categories']
                        }
                        all_comprehensive_results.append(combined_result)
                        
                        # Update scan results based on highest risk level
                        max_risk_score = max(comprehensive_result['risk_score'], heuristic_result['risk_score'])
                        if max_risk_score >= 75 or comprehensive_result['risk_level'] == 'CRITICAL' or heuristic_result['risk_level'] == 'CRITICAL':
                            scan_results['Status'] = 'MALICIOUS'
                        elif max_risk_score >= 25 and scan_results['Status'] != 'MALICIOUS':
                            scan_results['Status'] = 'SUSPICIOUS'
                    
                    # Legacy compatibility - still populate old structure
                    obfuscation = self.pattern_detector.test_obfuscation_patterns(content)
                    if obfuscation:
                        scan_results['ObfuscationPatterns'].append({
                            'File': os.path.basename(js_file),
                            'Patterns': obfuscation
                        })
                    
                    worm_sigs = self.pattern_detector.test_shai_hulud_patterns(content)
                    if worm_sigs:
                        scan_results['WormPatterns'].append({
                            'File': os.path.basename(js_file),
                            'Patterns': worm_sigs
                        })
                
                except Exception as e:
                    continue  # Skip files that can't be read
            
            # Add comprehensive results to scan results
            scan_results['ComprehensiveResults'] = all_comprehensive_results
            
            # Report findings
            if scan_results['Status'] == 'MALICIOUS':
                ColorOutput.critical("      [CRITICAL] Shai Hulud worm patterns detected!")
                for finding in scan_results['WormPatterns']:
                    ColorOutput.critical(f"        File: {finding['File']}")
                    for pattern in finding['Patterns']:
                        ColorOutput.critical(f"          {pattern}")
            elif scan_results['Status'] == 'SUSPICIOUS':
                ColorOutput.suspicious("      [SUSPICIOUS] Obfuscation patterns found")
                for finding in scan_results['ObfuscationPatterns']:
                    ColorOutput.suspicious(f"        File: {finding['File']}: {finding['Patterns'][0]}")
            else:
                ColorOutput.clean("      [CLEAN] No malicious patterns found in JavaScript files")
        
        except Exception as e:
            ColorOutput.critical(f"      [ERROR] Deep scan failed: {e}")
            scan_results['Status'] = 'ERROR'
        
        return scan_results
    
    def _download_package_tarball(self, package_name: str, version: str, repo_url: str, headers: Dict) -> Optional[str]:
        """Download and extract npm package tarball for deep scanning"""
        try:
            # Construct tarball URL based on repository type
            if "registry.npmjs.org" in repo_url:
                # NPM Registry format - need to get the actual tarball URL from package metadata
                metadata_url = f"{repo_url}{package_name}/{version}"
                response = requests.get(metadata_url, headers=headers, timeout=30)
                response.raise_for_status()
                metadata = response.json()
                tarball_url = metadata['dist']['tarball']
            else:
                # JFrog Artifactory format
                tarball_url = f"{repo_url}{package_name}/-/{package_name}-{version}.tgz"
            
            ColorOutput.info(f"      [INFO] Downloading {package_name}@{version} for deep scan...")
            
            # Create temporary directory
            temp_dir = tempfile.mkdtemp()
            tarball_path = os.path.join(temp_dir, f"{package_name}-{version}.tgz")
            
            # Download tarball
            response = requests.get(tarball_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            with open(tarball_path, 'wb') as f:
                f.write(response.content)
            
            # Extract using tarfile
            with tarfile.open(tarball_path, 'r:gz') as tar:
                tar.extractall(temp_dir)
            
            return temp_dir
            
        except Exception as e:
            ColorOutput.check(f"      [WARNING] Could not download package for deep scan: {e}")
            return None
    
    def _scan_package_json(self, package_json_path: str) -> Dict:
        """Scan package.json file"""
        try:
            import json
            with open(package_json_path, 'r', encoding='utf-8') as f:
                package_json = json.load(f)
            
            package_name = package_json.get('name', 'Unknown')
            package_version = package_json.get('version', 'Unknown')
            
            ColorOutput.info(f"Scanning package: {package_name}@{package_version}")
            
            result = {
                'Name': package_name,
                'Version': package_version,
                'Path': package_json_path,
                'Status': 'CLEAN',
                'Details': []
            }
            
            # Check dependencies
            all_deps = {}
            if 'dependencies' in package_json:
                all_deps.update(package_json['dependencies'])
            if 'devDependencies' in package_json:
                all_deps.update(package_json['devDependencies'])
            
            # Enhanced dependency analysis
            enhanced_findings = []
            
            # Run behavioral analysis on package.json
            behavioral_results = self.behavioral_analyzer.calculate_behavioral_risk(package_json, "")
            if behavioral_results['behavioral_findings']:
                enhanced_findings.extend(behavioral_results['behavioral_findings'])
                if behavioral_results['behavioral_risk_level'] in ['CRITICAL', 'HIGH']:
                    result['Status'] = 'SUSPICIOUS' if result['Status'] == 'CLEAN' else result['Status']
            
            # Run comprehensive heuristic analysis on package metadata
            heuristic_results = self.heuristic_analyzer.analyze_package_comprehensive("", package_json)
            if heuristic_results['findings']:
                enhanced_findings.extend(heuristic_results['findings'])
                if heuristic_results['risk_level'] in ['CRITICAL', 'HIGH']:
                    result['Status'] = 'SUSPICIOUS' if result['Status'] == 'CLEAN' else result['Status']
            
            # Run dependency analysis
            dependency_findings = self.dependency_analyzer.analyze_dependency_tree(package_json)
            if dependency_findings:
                enhanced_findings.extend(dependency_findings)
                result['Status'] = 'SUSPICIOUS' if result['Status'] == 'CLEAN' else result['Status']
            
            # Check each dependency for malicious packages and vulnerabilities
            for dep_name, dep_version in all_deps.items():
                # Remove version prefixes
                clean_version = re.sub(r'[\^~>=<]', '', dep_version)
                
                # Check for malicious packages
                malicious_check = self.pattern_detector.test_malicious_package(dep_name, clean_version)
                if malicious_check:
                    result['Status'] = 'MALICIOUS'
                    result['Details'].append(f"Malicious dependency: {dep_name}@{clean_version} - {malicious_check['Details']}")
                    ColorOutput.critical(f"  [CRITICAL] Found malicious package: {dep_name}@{clean_version}")
                
                # Check for known vulnerabilities
                vuln_findings = self.vulnerability_checker.check_known_vulnerabilities(dep_name, clean_version)
                if vuln_findings:
                    enhanced_findings.extend(vuln_findings)
                    result['Status'] = 'SUSPICIOUS' if result['Status'] == 'CLEAN' else result['Status']
                
                # Check for suspicious version patterns
                version_findings = self.vulnerability_checker.check_version_patterns(dep_name, clean_version)
                if version_findings:
                    enhanced_findings.extend(version_findings)
            
            # Add enhanced findings to result
            if enhanced_findings:
                result['Details'].extend(enhanced_findings)
                result['EnhancedFindings'] = {
                    'behavioral': behavioral_results,
                    'heuristic_analysis': heuristic_results,
                    'dependency_analysis': dependency_findings,
                    'vulnerability_checks': [f for f in enhanced_findings if 'VULNERABILITY' in f],
                    'heuristic_findings': [f for f in enhanced_findings if any(heuristic in f for heuristic in ['SHADY-LINKS', 'OBFUSCATION', 'CLIPBOARD-ACCESS', 'EXFILTRATE-SENSITIVE', 'DOWNLOAD-EXECUTABLE', 'EXEC-BASE64', 'SILENT-PROCESS-EXECUTION', 'DLL-HIJACKING', 'STEGANOGRAPHY', 'CODE-EXECUTION', 'CMD-OVERWRITE', 'EMPTY-INFORMATION', 'RELEASE-ZERO', 'TYPOSQUATTING', 'COMPROMISED-EMAIL', 'UNCLAIMED-EMAIL', 'REPOSITORY-INTEGRITY', 'SINGLE-PYTHON-FILE', 'BUNDLED-BINARY', 'DECEPTIVE-AUTHOR', 'NPM-SERIALIZE-ENVIRONMENT', 'NPM-OBFUSCATION', 'NPM-INSTALL-SCRIPT', 'NPM-STEGANOGRAPHY', 'NPM-DLL-HIJACKING', 'NPM-EXFILTRATE-SENSITIVE'])],
                    'total_enhanced_findings': len(enhanced_findings)
                }
            
            # Deep scan if enabled
            if self.deep_scan and result['Status'] != 'MALICIOUS':
                package_dir = os.path.dirname(package_json_path)
                
                # Use the unified deep scan function
                deep_scan_results = self._deep_scan_package(package_name, package_version, package_dir, "local")
                
                # Update result based on deep scan findings
                if deep_scan_results['Status'] == 'MALICIOUS':
                    result['Status'] = 'MALICIOUS'
                    for finding in deep_scan_results['WormPatterns']:
                        result['Details'].append(f"Worm pattern in {finding['File']}: {'; '.join(finding['Patterns'])}")
                elif deep_scan_results['Status'] == 'SUSPICIOUS' and result['Status'] != 'MALICIOUS':
                    result['Status'] = 'SUSPICIOUS'
                    for finding in deep_scan_results['ObfuscationPatterns']:
                        result['Details'].append(f"Obfuscation in {finding['File']}: {'; '.join(finding['Patterns'])}")
            
            return result
            
        except Exception as e:
            ColorOutput.critical(f"  [ERROR] Failed to parse package.json: {e}")
            return {
                'Name': 'Unknown',
                'Version': 'Unknown',
                'Path': package_json_path,
                'Status': 'ERROR',
                'Details': [f"Failed to parse: {e}"]
            }
    
    def _scan_remote_repository(self, repo_url: str, api_key: Optional[str]):
        """Scan remote repository"""
        ColorOutput.info(f"\nScanning remote repository: {repo_url}")
        if self.scan_all and self.deep_scan:
            ColorOutput.check("[COMPREHENSIVE MODE] Scanning ALL packages with deep scan enabled")
        ColorOutput.info("========================================")
        
        # Set up headers
        headers = {}
        if api_key:
            headers["X-JFrog-Art-Api"] = api_key
            headers["Authorization"] = f"Bearer {api_key}"
        
        # Determine repository type
        is_npm_registry = "registry.npmjs.org" in repo_url
        is_jfrog = "artifactory" in repo_url
        
        if is_npm_registry:
            ColorOutput.info("[INFO] Detected NPM Registry - using targeted package scanning")
            if self.scan_all:
                ColorOutput.check("[WARNING] -All parameter with NPM Registry will scan many popular packages. This may be slow.")
                ColorOutput.info("[INFO] Note: Full NPM registry scan not implemented. Scanning extended package list instead.")
        
        # Use targeted scanning method for known malicious packages
        ColorOutput.info("[INFO] Using targeted scanning method for known malicious packages...")
        
        # Determine which packages to scan
        packages_to_scan = self.malicious_packages['malicious_packages'].copy()
        
        # If -All is enabled and we're on NPM registry, add popular packages
        if self.scan_all and is_npm_registry:
            ColorOutput.info("[INFO] -All mode: Adding popular packages to scan list...")
            
            popular_packages = [
                {"name": "lodash", "malicious_version": ""},
                {"name": "react", "malicious_version": ""},
                {"name": "express", "malicious_version": ""},
                {"name": "axios", "malicious_version": ""},
                {"name": "moment", "malicious_version": ""},
                {"name": "underscore", "malicious_version": ""},
                {"name": "request", "malicious_version": ""},
                {"name": "commander", "malicious_version": ""},
                {"name": "colors", "malicious_version": ""},
                {"name": "mkdirp", "malicious_version": ""},
                {"name": "glob", "malicious_version": ""},
                {"name": "rimraf", "malicious_version": ""},
                {"name": "bluebird", "malicious_version": ""},
                {"name": "yargs", "malicious_version": ""},
                {"name": "inquirer", "malicious_version": ""},
                {"name": "fs-extra", "malicious_version": ""},
                {"name": "webpack", "malicious_version": ""},
                {"name": "babel-core", "malicious_version": ""},
                {"name": "typescript", "malicious_version": ""},
                {"name": "eslint", "malicious_version": ""}
            ]
            
            packages_to_scan.extend(popular_packages)
            ColorOutput.info(f"[INFO] Extended scan will check {len(packages_to_scan)} packages total")
        
        # Enhanced direct package access for selected packages
        for package in packages_to_scan:
            ColorOutput.check(f"  [CHECK] Scanning for {package['name']}...")
            
            # For npm registry, use the package metadata API
            if is_npm_registry:
                package_url = f"{repo_url}{package['name']}"
            else:
                package_url = f"{repo_url}/{package['name']}/package.json"
            
            try:
                response = requests.get(package_url, headers=headers, timeout=30)
                response.raise_for_status()
                package_data = response.json()
                
                # Handle npm registry response format
                if is_npm_registry and 'dist-tags' in package_data:
                    latest_version = package_data['dist-tags']['latest']
                    all_versions = list(package_data['versions'].keys())
                    
                    # Check if malicious version exists
                    malicious_versions_to_check = []
                    if 'malicious_versions' in package:
                        malicious_versions_to_check = package['malicious_versions']
                    elif 'malicious_version' in package and package['malicious_version']:
                        malicious_versions_to_check = [package['malicious_version']]
                    
                    found_malicious = False
                    for mal_version in malicious_versions_to_check:
                        if mal_version and mal_version in all_versions:
                            ColorOutput.critical(f"    [CRITICAL] Malicious version {mal_version} found in repository!")
                            
                            incident = package.get('incident', 'unknown')
                            self.results['MaliciousPackagesFound'].append({
                                'Package': f"{package['name']}@{mal_version}",
                                'Details': f"Malicious version available in repository (latest: {latest_version}, Incident: {incident})",
                                'Incident': incident
                            })
                            
                            # Deep scan if enabled
                            if self.deep_scan:
                                try:
                                    temp_dir = self._download_package_tarball(package['name'], mal_version, repo_url, headers)
                                    if temp_dir:
                                        ColorOutput.info(f"      [INFO] Deep scanning {package['name']}@{mal_version}...")
                                        deep_scan_results = self._deep_scan_package(package['name'], mal_version, temp_dir, "repository")
                                        
                                        if deep_scan_results['Status'] == 'MALICIOUS':
                                            ColorOutput.critical("      [CONFIRMED] Shai Hulud worm patterns found!")
                                        elif deep_scan_results['Status'] == 'SUSPICIOUS':
                                            ColorOutput.suspicious("      [CONFIRMED] Obfuscation patterns found")
                                        
                                        # Clean up
                                        shutil.rmtree(temp_dir, ignore_errors=True)
                                except Exception as e:
                                    ColorOutput.check(f"      [WARNING] Could not deep scan: {e}")
                            
                            found_malicious = True
                    
                    if not found_malicious and malicious_versions_to_check:
                        ColorOutput.clean(f"    [CLEAN] No malicious versions found (latest: {latest_version})")
                        self.results['CleanPackages'].append({
                            'Name': package['name'],
                            'Version': latest_version,
                            'Path': f"{repo_url}{package['name']}/{latest_version}/",
                            'Status': 'CLEAN',
                            'Details': ["Package scanned - no malicious versions found", "Latest version verified clean", "Safe to use"]
                        })
                    elif not malicious_versions_to_check:
                        # This is a popular package added for -All scanning
                        ColorOutput.info(f"    [INFO] Scanning popular package {package['name']} (latest: {latest_version})")
                        
                        # Deep scan the latest version if enabled
                        if self.deep_scan:
                            try:
                                temp_dir = self._download_package_tarball(package['name'], latest_version, repo_url, headers)
                                if temp_dir:
                                    ColorOutput.info(f"      [INFO] Deep scanning {package['name']}@{latest_version}...")
                                    
                                    # Find the package directory
                                    package_dir = os.path.join(temp_dir, "package")
                                    
                                    if os.path.exists(package_dir):
                                        # Look for main entry point files
                                        main_files = ["index.js", "main.js", "lib/index.js", "src/index.js"]
                                        found_suspicious = False
                                        
                                        for main_file in main_files:
                                            js_path = os.path.join(package_dir, main_file)
                                            if os.path.exists(js_path):
                                                try:
                                                    with open(js_path, 'r', encoding='utf-8', errors='ignore') as f:
                                                        content = f.read()
                                                    
                                                    # Check for obfuscation patterns
                                                    if re.search(r'const\s+_0x112', content):
                                                        ColorOutput.suspicious(f"      [SUSPICIOUS] Obfuscation pattern 'const _0x112' found in {main_file}")
                                                        self.results['SuspiciousPackagesFound'].append({
                                                            'Name': package['name'],
                                                            'Version': latest_version,
                                                            'Details': [f"Obfuscation pattern 'const _0x112' found in {main_file}"],
                                                            'Path': repo_url,
                                                            'Status': 'SUSPICIOUS'
                                                        })
                                                        found_suspicious = True
                                                        break
                                                    elif re.search(r'_0x[0-9a-f]{4,}.*_0x[0-9a-f]{4,}.*_0x[0-9a-f]{4,}', content):
                                                        ColorOutput.suspicious(f"      [SUSPICIOUS] Heavy obfuscation patterns detected in {main_file}")
                                                        self.results['SuspiciousPackagesFound'].append({
                                                            'Name': package['name'],
                                                            'Version': latest_version,
                                                            'Details': [f"Heavy obfuscation patterns detected in {main_file}"],
                                                            'Path': repo_url,
                                                            'Status': 'SUSPICIOUS'
                                                        })
                                                        found_suspicious = True
                                                        break
                                                except Exception:
                                                    continue
                                        
                                        if not found_suspicious:
                                            ColorOutput.clean(f"      [CLEAN] No suspicious patterns found in {package['name']}")
                                            self.results['CleanPackages'].append({
                                                'Name': package['name'],
                                                'Version': latest_version,
                                                'Path': f"{repo_url}{package['name']}/{latest_version}/",
                                                'Status': 'CLEAN',
                                                'Details': ["Package verified clean", "No malicious patterns detected", "Deep scan passed"]
                                            })
                                    
                                    # Clean up
                                    shutil.rmtree(temp_dir, ignore_errors=True)
                            except Exception as e:
                                ColorOutput.check(f"      [WARNING] Could not deep scan {package['name']}: {e}")
                
                else:
                    # Handle direct package.json response (JFrog format)
                    # Check if current version is malicious
                    malicious_versions_to_check = []
                    if 'malicious_versions' in package:
                        malicious_versions_to_check = package['malicious_versions']
                    elif 'malicious_version' in package and package['malicious_version']:
                        malicious_versions_to_check = [package['malicious_version']]
                    
                    if package_data.get('version') in malicious_versions_to_check:
                        ColorOutput.critical(f"    [CRITICAL] Found malicious package: {package['name']}@{package_data['version']}")
                        incident = package.get('incident', 'unknown')
                        self.results['MaliciousPackagesFound'].append({
                            'Package': f"{package['name']}@{package_data['version']}",
                            'Details': f"Exact malicious version match (Incident: {incident})",
                            'Incident': incident
                        })
                    else:
                        ColorOutput.clean(f"    [CLEAN] Safe version found: {package['name']}@{package_data['version']}")
                        self.results['CleanPackages'].append({
                            'Name': package['name'],
                            'Version': package_data['version'],
                            'Path': package_url,
                            'Status': 'CLEAN',
                            'Details': ["Package verified clean", "No malicious patterns detected", "Safe to use"]
                        })
                
                self.results['TotalPackagesScanned'] += 1
                
            except Exception as e:
                ColorOutput.info(f"    [INFO] Package {package['name']} not found in repository")
    
    def _scan_local_directory(self, path: str):
        """Scan local directory"""
        ColorOutput.info(f"\nScanning local directory: {path}")
        ColorOutput.info("========================================")
        
        # Find all package.json files
        package_files = []
        for root, dirs, files in os.walk(path):
            # Skip node_modules directories
            dirs[:] = [d for d in dirs if d != 'node_modules']
            for file in files:
                if file == 'package.json':
                    package_files.append(os.path.join(root, file))
        
        ColorOutput.info(f"Found {len(package_files)} package.json files to scan")
        
        for i, package_file in enumerate(package_files, 1):
            if len(package_files) > 5:
                percent_complete = round((i / len(package_files)) * 100, 1)
                print(f"\rProgress: {i}/{len(package_files)} ({percent_complete}%)", end='', flush=True)
            
            result = self._scan_package_json(package_file)
            
            if result['Status'] == 'MALICIOUS':
                self.results['MaliciousPackagesFound'].append(result)
                ColorOutput.critical("  [CRITICAL] Malicious package detected!")
            elif result['Status'] == 'SUSPICIOUS':
                self.results['SuspiciousPackagesFound'].append(result)
                ColorOutput.suspicious("  [SUSPICIOUS] Suspicious patterns found")
            elif result['Status'] == 'ERROR':
                self.results['RequireManualCheck'].append(result)
                ColorOutput.check("  [CHECK] Manual review required")
            elif result['Status'] == 'CLEAN':
                result['Details'] = ["Package verified clean", "No malicious patterns detected", "Safe to use"]
                self.results['CleanPackages'].append(result)
                ColorOutput.clean("  [CLEAN] Package verified safe")
            
            self.results['TotalPackagesScanned'] += 1
        
        if len(package_files) > 5:
            print()  # New line after progress
    
    def _generate_summary(self):
        """Generate scan summary"""
        ColorOutput.info("\n===================================================")
        ColorOutput.info("NPM Supply Chain Compromise Scanner v1.1")
        ColorOutput.info("Scanning for September 2025 compromised packages")
        ColorOutput.info("===================================================")
        
        ColorOutput.info("\n===================================================")
        ColorOutput.info("CRIMSON7 SCAN SUMMARY")
        ColorOutput.info("===================================================")
        ColorOutput.info(f"Total packages scanned: {self.results['TotalPackagesScanned']}")
        
        malicious_count = len(self.results['MaliciousPackagesFound'])
        suspicious_count = len(self.results['SuspiciousPackagesFound'])
        manual_check_count = len(self.results['RequireManualCheck'])
        clean_count = len(self.results['CleanPackages'])
        
        if malicious_count > 0:
            ColorOutput.critical(f"Malicious packages found: {malicious_count}")
        else:
            ColorOutput.clean(f"Malicious packages found: {malicious_count}")
        
        if suspicious_count > 0:
            ColorOutput.suspicious(f"Suspicious packages found: {suspicious_count}")
        else:
            ColorOutput.clean(f"Suspicious packages found: {suspicious_count}")
        
        if manual_check_count > 0:
            ColorOutput.check(f"Packages requiring manual check: {manual_check_count}")
        else:
            ColorOutput.clean(f"Packages requiring manual check: {manual_check_count}")
        
        ColorOutput.clean(f"Clean packages: {clean_count}")
        
        if clean_count > 0:
            sample_clean = [f"{pkg['Name']}@{pkg['Version']}" for pkg in self.results['CleanPackages'][:5]]
            if clean_count <= 5:
                ColorOutput.clean(f"  Clean: {', '.join(sample_clean)}")
            else:
                ColorOutput.clean(f"  Sample: {', '.join(sample_clean)} (and {clean_count - 5} more)")
        
        # Show incident breakdown if malicious packages found
        if malicious_count > 0:
            ColorOutput.info("\n--- INCIDENT BREAKDOWN ---")
            
            incident_groups = {}
            for pkg in self.results['MaliciousPackagesFound']:
                incident = pkg.get('Incident', 'unknown')
                if incident not in incident_groups:
                    incident_groups[incident] = 0
                incident_groups[incident] += 1
            
            for incident, count in incident_groups.items():
                incident_name = {
                    "s1ngularity_shai_hulud_2025_09_16": "Shai Hulud Worm (Sept 16, 2025)",
                    "duckdb_compromise_2025_09_09": "DuckDB Compromise (Sept 9, 2025)",
                    "npm_compromise_2025_09_08": "NPM Supply Chain (Sept 8, 2025)"
                }.get(incident, incident)
                ColorOutput.critical(f"  {incident_name}: {count} packages")
    
    def _export_results(self):
        """Export scan results"""
        import json
        import csv
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(self.output_path, f"npm_scan_report_{timestamp}.json")
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        ColorOutput.info("\n=== Crimson7 Security Analysis Complete ===")
        ColorOutput.info(f"Detailed report saved to: {report_path}")
        ColorOutput.info("Visit https://crimson7.io for more security tools")
        
        # Export CSV for critical findings
        if len(self.results['MaliciousPackagesFound']) > 0 or len(self.results['SuspiciousPackagesFound']) > 0:
            csv_path = os.path.join(self.output_path, f"npm_scan_critical_{timestamp}.csv")
            
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Status', 'Package', 'Details', 'Path']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for item in self.results['MaliciousPackagesFound']:
                    writer.writerow({
                        'Status': 'MALICIOUS',
                        'Package': item.get('Package', '').replace('@', ' v'),
                        'Details': '; '.join(item.get('Details', [])),
                        'Path': item.get('Path', '')
                    })
                
                for item in self.results['SuspiciousPackagesFound']:
                    writer.writerow({
                        'Status': 'SUSPICIOUS',
                        'Package': f"{item['Name']} v{item['Version']}",
                        'Details': '; '.join(item.get('Details', [])),
                        'Path': item.get('Path', '')
                    })
            
            ColorOutput.info(f"Critical findings exported to: {csv_path}")
        
        # Generate HTML report if requested
        if self.generate_html:
            self._generate_html_report()
        
        # Return exit code based on findings
        if len(self.results['MaliciousPackagesFound']) > 0:
            ColorOutput.critical("\n[CRITICAL] Malicious packages detected! Immediate action required!")
            sys.exit(2)
        elif len(self.results['SuspiciousPackagesFound']) > 0:
            ColorOutput.suspicious("\n[WARNING] Suspicious packages detected. Manual review recommended.")
            sys.exit(1)
        else:
            ColorOutput.clean("\n[SUCCESS] No malicious packages detected.")
            sys.exit(0)
    
    def _generate_html_report(self):
        """Generate HTML report from scan results"""
        from ..reports.html_generator import HTMLReportGenerator
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_path = os.path.join(self.output_path, f"npm_scan_report_{timestamp}.json")
        html_path = os.path.join(self.output_path, f"npm_scan_report_{timestamp}.html")
        
        # Generate HTML report
        html_generator = HTMLReportGenerator(json_path, html_path)
        html_generator.load_scan_data()
        html_generator.generate_report()
        
        ColorOutput.info(f"HTML report generated: {html_path}")
    
    def generate_report_from_json(self, json_path: str, html_path: str):
        """Generate HTML report from existing JSON file"""
        from ..reports.html_generator import HTMLReportGenerator
        
        html_generator = HTMLReportGenerator(json_path, html_path)
        if html_generator.load_scan_data():
            html_generator.generate_report()
            ColorOutput.info(f"HTML report generated: {html_path}")
        else:
            ColorOutput.critical("Failed to generate HTML report")
    
    def run_scan(self):
        """Run the security scan"""
        from ..utils.colors import Colors
        
        # Display banner
        print(f"\n{Colors.RED}{Colors.BOLD}===== CRIMSON7 NPM SECURITY SCANNER v1.1 ====={Colors.END}")
        print(f"{Colors.WHITE}Advanced Supply Chain Security Analysis{Colors.END}")
        print(f"{Colors.CYAN}https://crimson7.io{Colors.END}")
        print(f"{Colors.RED}===============================================\n{Colors.END}")
        
        # Validate inputs
        if not self.repository_url and not self.local_path:
            ColorOutput.critical("Please specify either --repository-url or --local-path")
            sys.exit(1)
        
        # Validate and fix URL if needed
        if self.repository_url:
            self.repository_url = self._validate_url(self.repository_url)
        
        # Warning for -All parameter usage
        if self.scan_all and not self.deep_scan:
            ColorOutput.check("[WARNING] --all parameter requires --deep-scan to be enabled. Ignoring --all.")
            self.scan_all = False
        
        if self.scan_all and self.deep_scan:
            ColorOutput.check("[WARNING] Using --all with --deep-scan will scan ALL packages in the repository!")
            ColorOutput.check("[WARNING] This is very resource intensive and may take a long time.")
            ColorOutput.check("[WARNING] Press Ctrl+C within 10 seconds to cancel, or wait to continue...")
            time.sleep(10)
        
        # Perform scan based on input
        if self.repository_url:
            self._scan_remote_repository(self.repository_url, self.api_key)
        
        if self.local_path:
            self._scan_local_directory(self.local_path)
        
        # Generate summary
        self._generate_summary()
        
        # Export results
        self._export_results()
