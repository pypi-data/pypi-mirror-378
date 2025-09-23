# Crimson7 NPM Security Scanner

**Advanced supply chain security analysis for NPM repositories with comprehensive threat detection capabilities.**

## **Features**

- **Advanced Pattern Detection**: Crypto mining, credential harvesting, data exfiltration, anti-debugging
- **Behavioral Analysis**: Package metadata, network behavior, file operations
- **Vulnerability Assessment**: CVE database integration, version analysis
- **Dependency Chain Analysis**: Typosquatting detection, circular dependencies
- **Risk Scoring**: Multi-layered risk assessment with weighted scoring
- **Threat Intelligence**: Enhanced malware signatures and patterns

## **Installation from Source**

```bash
# Clone the repository
git clone https://github.com/Crimson7research/npmscanner.git
cd npmscanner

# Install dependencies
pip install -r requirements.txt

# Verify installation
python main.py --help
```

## **Installation via PyPI**

```bash
pip install npmscanner

# Verify installation
npmscanner --help
```


## **Usage**

### **Local Project Scanning**
```bash
# Basic scan
python main.py --local-path "/path/to/project"

# Deep scan with HTML report
python main.py --local-path "/path/to/project" --deep-scan --generate-html
```

### **Remote Repository Scanning**
```bash
# Scan JFrog Artifactory
python main.py --repository-url "https://artifactory.company.com/artifactory/npm-repo/" --api-key "your-key"

# Scan NPM registry
python main.py --repository-url "https://registry.npmjs.org" --deep-scan
```

### **Report Generation**
```bash
# Generate HTML report
python main.py --local-path "/path/to/project" --generate-html

# Convert JSON to HTML
python main.py --json-report scan_results.json --html-report dashboard.html
```

## **Command Line Options**

| Option | Description | Required |
|--------|-------------|----------|
| `--repository-url` | NPM repository URL to scan | No* |
| `--local-path` | Local directory path to scan | No* |
| `--api-key` | API key for authenticated access | No |
| `--output-path` | Base directory for reports (saved in /report subfolder) | No |
| `--deep-scan` | Enable deep content analysis | No |
| `--all` | Scan ALL packages (requires --deep-scan) | No |
| `--generate-html` | Generate HTML report after scanning | No |
| `--json-report` | Path to existing JSON scan report to convert to HTML | No |
| `--html-report` | Output HTML file path | No |

*Either `--repository-url` or `--local-path` must be specified.

## **Output Files**

All reports are automatically saved in a `/report` folder:

```
project/
├── report/
│   ├── npm_scan_report_YYYYMMDD_HHMMSS.json    # Detailed JSON report
│   ├── npm_scan_report_YYYYMMDD_HHMMSS.html    # Interactive HTML dashboard
│   └── npm_scan_critical_YYYYMMDD_HHMMSS.csv   # Critical findings export
└── ...
```

## Patterns
| File | Purpose | Key Features |
|------|---------|--------------|
| `source_code.py` | Source code heuristics | 11 detection methods |
| `metadata.py` | Metadata analysis | 9 detection methods |
| `npm_specific.py` | NPM-specific patterns | 6 detection methods |
| `unified_analyzer.py` | Combined analysis | Risk scoring + categorization |

## **Exit Codes**

| Code | Status | Meaning |
|------|--------|---------|
| 0 | ✅ CLEAN | No malicious packages found |
| 1 | ⚠️ SUSPICIOUS | Suspicious packages found |
| 2 | 🚨 CRITICAL | Malicious packages detected |

## **Troubleshooting**

### **Common Issues**
```bash
# "malicious_packages.json not found"
# Solution: Ensure enhanced database is in project root
ls -la malicious_packages.json

# "Could not download package for deep scan"
# Solution: Check network connectivity and repository access
python main.py --repository-url "https://registry.npmjs.org" --deep-scan
```

### **Performance Tips**
- Use `--deep-scan` only when necessary (resource intensive)
- Avoid `--all` flag unless comprehensive scanning is required
- For CI/CD, use focused scanning with custom output paths

## 🔗 **Enterprise Integration**

### **CI/CD Pipeline Integration**
```yaml
# GitHub Actions workflow
- name: NPM Security Scan
  run: |
    python main.py --local-path . --deep-scan --generate-html
    if [ $? -eq 2 ]; then
      echo "🚨 CRITICAL: Malicious packages detected!"
      exit 1
    fi
```

## **Support**

- **Website**: https://crimson7.io
- **Issues**: Report issues through the GitHub repository

## 📄 **License**

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

**🛡️ Protect your NPM supply chain with enterprise-grade security analysis!**

Visit [crimson7.io](https://crimson7.io) for more security tools
