#!/usr/bin/env python3

import argparse
import os
import sys
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from npmscanner.core import NPMSecurityScanner
from npmscanner.reports import HTMLReportGenerator
from npmscanner.utils import ColorOutput
from npmscanner.banner import banner

def main():
    # Display banner
    banner()
    
    parser = argparse.ArgumentParser(
        description="Crimson7 NPM Security Scanner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan local project
  npmscanner --local-path "/path/to/project" --deep-scan
  
  # Scan remote repository
  npmscanner --repository-url "https://artifactory.company.com/artifactory/npm-repo/" --api-key "your-key"
  
  # Generate HTML report from JSON
  npmscanner --json-report scan_results.json --html-report security_report.html
  
  # Scan with HTML report generation
  npmscanner --local-path "/path/to/project" --generate-html
        """
    )
    
    # Scanning options
    parser.add_argument('--repository-url', help='The base URL of the NPM repository to scan')
    parser.add_argument('--local-path', help='Local directory path to scan for package.json files')
    parser.add_argument('--api-key', help='API key for authenticated repository access')
    parser.add_argument('--output-path', default='.', help='Base path for output reports (reports will be saved in /report subfolder)')
    parser.add_argument('--deep-scan', action='store_true', help='Enable deep scanning of .tgz archives for obfuscation patterns')
    parser.add_argument('--all', action='store_true', help='When combined with --deep-scan, scan ALL packages in the repository (very resource intensive)')
    
    # Reporting options
    parser.add_argument('--generate-html', action='store_true', help='Generate HTML report after scanning (default: true)')
    parser.add_argument('--no-html', action='store_true', help='Disable HTML report generation')
    parser.add_argument('--json-report', help='Path to existing JSON scan report to convert to HTML')
    parser.add_argument('--html-report', help='Output HTML file path (default: auto-generated)')
    
    args = parser.parse_args()
    
    # Handle report generation from existing JSON
    if args.json_report:
        if not os.path.exists(args.json_report):
            ColorOutput.critical(f"JSON report file not found: {args.json_report}")
            sys.exit(1)
        
        html_path = args.html_report or "npm_scan_report.html"
        generator = HTMLReportGenerator(args.json_report, html_path)
        if generator.generate_report():
            ColorOutput.info("HTML report generation completed successfully")
        else:
            ColorOutput.critical("Failed to generate HTML report")
            sys.exit(1)
        return
    
    # Validate scanning inputs
    if not args.repository_url and not args.local_path:
        ColorOutput.critical("Please specify either --repository-url or --local-path for scanning")
        ColorOutput.info("Use --json-report to generate HTML from existing JSON file")
        sys.exit(1)
    
    # Determine HTML generation setting
    generate_html = not args.no_html
    if args.generate_html:
        generate_html = True
    
    # Create scanner instance
    scanner = NPMSecurityScanner(
        repository_url=args.repository_url,
        local_path=args.local_path,
        api_key=args.api_key,
        output_path=args.output_path,
        deep_scan=args.deep_scan,
        scan_all=args.all,
        generate_html=generate_html
    )
    
    # Run the scan
    scanner.run_scan()

if __name__ == "__main__":
    main()
