import json
import os
import webbrowser
from datetime import datetime
from typing import Dict

from ..utils.colors import ColorOutput

class HTMLReportGenerator:
    """HTML Report Generator for NPM Security Scanner results"""
    
    def __init__(self, json_path: str, output_path: str = "npm_scan_report.html"):
        self.json_path = json_path
        self.output_path = output_path
        self.scan_data = None
    
    def load_scan_data(self) -> Dict:
        """Load scan data from JSON file"""
        if not os.path.exists(self.json_path):
            ColorOutput.critical(f"JSON report file not found: {self.json_path}")
            return None
        
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                self.scan_data = json.load(f)
            return self.scan_data
        except Exception as e:
            ColorOutput.critical(f"Failed to load JSON report: {e}")
            return None
    
    def calculate_summary_stats(self) -> Dict:
        """Calculate summary statistics from scan data"""
        total_malicious = len(self.scan_data.get('MaliciousPackagesFound', []))
        total_suspicious = len(self.scan_data.get('SuspiciousPackagesFound', []))
        total_clean = len(self.scan_data.get('CleanPackages', []))
        total_manual_check = len(self.scan_data.get('RequireManualCheck', []))
        total_scanned = self.scan_data.get('TotalPackagesScanned', 0)
        
        # Determine overall risk level
        risk_level = "LOW"
        risk_color = "#28a745"
        if total_malicious > 0:
            risk_level = "CRITICAL"
            risk_color = "#dc3545"
        elif total_suspicious > 0:
            risk_level = "HIGH"
            risk_color = "#fd7e14"
        elif total_manual_check > 0:
            risk_level = "MEDIUM"
            risk_color = "#ffc107"
        
        return {
            'total_malicious': total_malicious,
            'total_suspicious': total_suspicious,
            'total_clean': total_clean,
            'total_manual_check': total_manual_check,
            'total_scanned': total_scanned,
            'risk_level': risk_level,
            'risk_color': risk_color
        }
    
    def generate_html(self) -> str:
        """Generate HTML report"""
        stats = self.calculate_summary_stats()
        
        # Get repository name for display
        repository = self.scan_data.get('Repository', 'Unknown')
        if '/' in repository:
            repository = repository.split('/')[-2] if repository.endswith('/') else repository.split('/')[-1]
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Crimson7 NPM Package Security Scan Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #8b0000 0%, #dc143c 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #8b0000 0%, #b22222 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 300;
        }}
        
        .header .subtitle {{
            font-size: 1.1em;
            opacity: 0.8;
        }}
        
        .scan-info {{
            background: #f8f9fa;
            padding: 20px 30px;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .scan-info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }}
        
        .scan-info-item {{
            text-align: center;
        }}
        
        .scan-info-value {{
            font-size: 1.5em;
            font-weight: bold;
            color: #2c3e50;
        }}
        
        .scan-info-label {{
            font-size: 0.9em;
            color: #6c757d;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-top: 5px;
        }}
        
        .risk-assessment {{
            padding: 30px;
            text-align: center;
            background: #f8f9fa;
        }}
        
        .risk-badge {{
            display: inline-block;
            padding: 15px 30px;
            border-radius: 50px;
            color: white;
            font-size: 1.3em;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 15px;
        }}
        
        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 30px;
        }}
        
        .summary-card {{
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            transition: transform 0.2s;
        }}
        
        .summary-card:hover {{
            transform: translateY(-5px);
        }}
        
        .card-number {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        
        .card-label {{
            font-size: 1.1em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .malicious {{ color: #dc3545; }}
        .suspicious {{ color: #fd7e14; }}
        .manual-check {{ color: #ffc107; }}
        .clean {{ color: #28a745; }}
        
        .findings {{
            padding: 30px;
        }}
        
        .findings h2 {{
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: 1.8em;
        }}
        
        .finding-section {{
            margin-bottom: 30px;
        }}
        
        .finding-section h3 {{
            color: #495057;
            margin-bottom: 15px;
            padding-bottom: 5px;
            border-bottom: 2px solid #e9ecef;
        }}
        
        .package-card {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
            border-left: 5px solid;
        }}
        
        .package-card.malicious {{
            border-left-color: #dc3545;
            background: #f8d7da;
        }}
        
        .package-card.suspicious {{
            border-left-color: #fd7e14;
            background: #ffeaa7;
        }}
        
        .package-card.manual-check {{
            border-left-color: #ffc107;
            background: #fff3cd;
        }}
        
        .package-name {{
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 10px;
            color: #2c3e50;
        }}
        
        .package-version {{
            color: #6c757d;
            font-size: 0.9em;
            margin-bottom: 10px;
        }}
        
        .package-path {{
            font-size: 0.8em;
            color: #6c757d;
            font-family: monospace;
            background: white;
            padding: 5px 10px;
            border-radius: 4px;
            margin-bottom: 10px;
        }}
        
        .package-details {{
            margin-top: 15px;
        }}
        
        .detail-item {{
            background: white;
            padding: 8px 12px;
            margin: 5px 0;
            border-radius: 4px;
            font-size: 0.9em;
            border-left: 3px solid #dc3545;
        }}
        
        .no-findings {{
            text-align: center;
            color: #6c757d;
            font-style: italic;
            padding: 20px;
        }}
        
        .footer {{
            background: #2c3e50;
            color: white;
            text-align: center;
            padding: 20px;
            font-size: 0.9em;
        }}
        
        .timestamp {{
            opacity: 0.7;
        }}
        
        @media (max-width: 768px) {{
            .summary-cards {{
                grid-template-columns: 1fr;
            }}
            
            .scan-info-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>Crimson7 NPM Security Scanner</h1>
            <div class="subtitle">Advanced Supply Chain Security Analysis | crimson7.io</div>
        </header>
        
        <div class="scan-info">
            <div class="scan-info-grid">
                <div class="scan-info-item">
                    <div class="scan-info-value">{self.scan_data.get('ScanDate', 'Unknown')}</div>
                    <div class="scan-info-label">Scan Date</div>
                </div>
                <div class="scan-info-item">
                    <div class="scan-info-value">{stats['total_scanned']}</div>
                    <div class="scan-info-label">Packages Scanned</div>
                </div>
                <div class="scan-info-item">
                    <div class="scan-info-value">{repository}</div>
                    <div class="scan-info-label">Repository</div>
                </div>
            </div>
        </div>
        
        <div class="risk-assessment">
            <div class="risk-badge" style="background-color: {stats['risk_color']};">
                Risk Level: {stats['risk_level']}
            </div>
            <div>Based on the analysis of {stats['total_scanned']} package(s)</div>
        </div>
        
        <div class="summary-cards">
            <div class="summary-card">
                <div class="card-number malicious">{stats['total_malicious']}</div>
                <div class="card-label malicious">Malicious Packages</div>
            </div>
            <div class="summary-card">
                <div class="card-number suspicious">{stats['total_suspicious']}</div>
                <div class="card-label suspicious">Suspicious Packages</div>
            </div>
            <div class="summary-card">
                <div class="card-number manual-check">{stats['total_manual_check']}</div>
                <div class="card-label manual-check">Manual Check Required</div>
            </div>
            <div class="summary-card">
                <div class="card-number clean">{stats['total_clean']}</div>
                <div class="card-label clean">Clean Packages</div>
            </div>
        </div>
        
        <div class="findings">
            <h2>Detailed Findings</h2>"""
        
        # Add findings sections
        if stats['total_malicious'] > 0:
            html += f"""
            <div class="finding-section">
                <h3>Malicious Packages ({stats['total_malicious']})</h3>"""
            
            for package in self.scan_data.get('MaliciousPackagesFound', []):
                package_name = package.get('Name', package.get('Package', 'Unknown'))
                package_version = package.get('Version', 'Unknown')
                package_path = package.get('Path', 'Unknown')
                details = package.get('Details', [])
                
                html += f"""
                <div class="package-card malicious">
                    <div class="package-name">{package_name}</div>
                    <div class="package-version">Version: {package_version}</div>
                    <div class="package-path">{package_path}</div>
                    <div class="package-details">"""
                
                for detail in details:
                    html += f"                        <div class='detail-item'>{detail}</div>\n"
                
                html += """
                    </div>
                </div>"""
            
            html += "            </div>\n"
        else:
            html += """
            <div class="finding-section">
                <h3>Malicious Packages</h3>
                <div class="no-findings">No malicious packages detected</div>
            </div>"""
        
        # Add other sections similarly...
        html += f"""
        </div>

        <footer class="footer">
            <div>Crimson7 NPM Security Scanner v0.1.1 | <a href="https://crimson7.io" style="color: #ffc107; text-decoration: none;">crimson7.io</a></div>
            <div class="timestamp">Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Shai Hulud Update</div>
        </footer>
    </div>
</body>
</html>"""
        
        return html
    
    def generate_report(self):
        """Generate and save HTML report"""
        ColorOutput.info(f"Generating HTML report from {self.json_path}...")
        
        # Load scan data
        if not self.load_scan_data():
            return False
        
        # Generate HTML
        html_content = self.generate_html()
        
        # Write HTML to file
        with open(self.output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        ColorOutput.info(f"HTML report generated: {self.output_path}")
        
        # Try to open the report in default browser
        try:
            webbrowser.open(f"file://{os.path.abspath(self.output_path)}")
        except Exception:
            pass  # Silently fail if browser can't be opened
        
        return True
