#!/usr/bin/env python3
"""
Test script for CLI and component detection across different environments.
Can be run locally or in CI/CD.
"""

import subprocess
import sys
import os
import json
from pathlib import Path
from typing import Dict, List, Tuple

def test_cli_detection() -> Dict[str, bool]:
    """Test if various CLIs can be detected."""
    results = {}
    
    # CLIs to test
    clis_to_test = {
        'qwen': ['qwen', '--version'],
        'gemini': ['gemini', '--version'],
        'codex': ['codex', '--version'],
        'claude': ['claude', '--version'],
        'gh': ['gh', '--version'],
        'npm': ['npm', '--version'],
        'node': ['node', '--version'],
        'python': ['python', '--version'],
        'pipx': ['pipx', '--version'],
        'docker': ['docker', '--version']
    }
    
    # Additional paths to check (for CI environments)
    additional_paths = os.environ.get('CLI_TEST_PATHS', '').split(':')
    
    for cli_name, command in clis_to_test.items():
        found = False
        
        # Try direct command
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                found = True
                results[cli_name] = True
                print(f"✅ {cli_name}: Found via PATH")
                continue
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        # Try common installation paths
        common_paths = [
            f"/home/{os.environ.get('USER', 'runner')}/.npm-global/bin/{cli_name}",
            f"/home/{os.environ.get('USER', 'runner')}/.local/bin/{cli_name}",
            f"/usr/local/bin/{cli_name}",
            f"/opt/homebrew/bin/{cli_name}",  # macOS ARM
            f"C:\\Program Files\\{cli_name}\\{cli_name}.exe",  # Windows
        ]
        
        # Add additional paths from environment
        for path in additional_paths:
            if path:
                common_paths.append(f"{path}/{cli_name}")
        
        for path in common_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                found = True
                results[cli_name] = True
                print(f"✅ {cli_name}: Found at {path}")
                break
        
        if not found:
            results[cli_name] = False
            print(f"❌ {cli_name}: Not found")
    
    return results

def test_component_detection() -> Dict[str, Tuple[bool, str]]:
    """Test if multiagent components are installed."""
    results = {}
    
    components = [
        'multiagent-core',
        'multiagent-devops',
        'multiagent-testing',
        'multiagent-agentswarm'
    ]
    
    for component in components:
        try:
            # Try using importlib.metadata (Python 3.8+)
            from importlib import metadata
            version = metadata.version(component)
            results[component] = (True, version)
            print(f"✅ {component}: v{version}")
        except:
            try:
                # Fallback to pkg_resources
                import pkg_resources
                version = pkg_resources.get_distribution(component).version
                results[component] = (True, version)
                print(f"✅ {component}: v{version}")
            except:
                results[component] = (False, "Not installed")
                print(f"❌ {component}: Not installed")
    
    return results

def test_template_structure() -> Dict[str, bool]:
    """Test if template directories exist and have correct structure."""
    results = {}
    
    # Find package location
    try:
        import multiagent_core
        package_dir = Path(multiagent_core.__file__).parent
        templates_dir = package_dir / 'templates'
    except ImportError:
        print("❌ multiagent_core package not found")
        return results
    
    # Expected template structure
    expected_dirs = [
        '.claude',
        '.claude/agents',
        '.claude/commands',
        '.claude/hooks',
        '.github',
        '.github/workflows',
        '.multiagent',
        '.vscode'
    ]
    
    for dir_path in expected_dirs:
        full_path = templates_dir / dir_path
        if full_path.exists() and full_path.is_dir():
            results[dir_path] = True
            print(f"✅ Template {dir_path}: Found")
        else:
            results[dir_path] = False
            print(f"❌ Template {dir_path}: Missing")
    
    # Check specific important files
    important_files = [
        '.github/copilot-instructions.md',
        '.multiagent/.gitmessage',
        '.claude/settings.json.backup'
    ]
    
    for file_path in important_files:
        full_path = templates_dir / file_path
        if full_path.exists() and full_path.is_file():
            results[file_path] = True
            # Check file size to ensure it's not empty
            size = full_path.stat().st_size
            if file_path == '.github/copilot-instructions.md' and size < 5000:
                print(f"⚠️  {file_path}: Found but seems incomplete ({size} bytes)")
                results[file_path] = False
            else:
                print(f"✅ Template {file_path}: Found ({size} bytes)")
        else:
            results[file_path] = False
            print(f"❌ Template {file_path}: Missing")
    
    return results

def test_init_command(test_dir: Path = None) -> bool:
    """Test the multiagent init command."""
    if test_dir is None:
        test_dir = Path("/tmp/multiagent-test")
    
    # Clean up if exists
    if test_dir.exists():
        import shutil
        shutil.rmtree(test_dir)
    
    test_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\nTesting 'multiagent init' in {test_dir}")
    
    # Run init command
    try:
        result = subprocess.run(
            ['multiagent', 'init', '--no-interactive'],
            cwd=test_dir,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"❌ Init command failed: {result.stderr}")
            return False
        
        # Check if expected directories were created
        expected = ['.claude', '.github', '.multiagent', '.vscode']
        for dir_name in expected:
            dir_path = test_dir / dir_name
            if not dir_path.exists():
                print(f"❌ Directory {dir_name} was not created")
                return False
            else:
                print(f"✅ Directory {dir_name} created")
        
        # Check copilot-instructions.md
        copilot_file = test_dir / '.github' / 'copilot-instructions.md'
        if copilot_file.exists():
            lines = copilot_file.read_text().count('\n')
            if lines > 200:
                print(f"✅ copilot-instructions.md created with {lines} lines")
            else:
                print(f"⚠️  copilot-instructions.md only has {lines} lines")
        else:
            print(f"❌ copilot-instructions.md not created")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Exception during init test: {e}")
        return False

def generate_report(results: Dict) -> str:
    """Generate a markdown report of test results."""
    report = ["# MultiAgent Core Detection Test Report\n"]
    
    if 'cli_detection' in results:
        report.append("## CLI Detection Results\n")
        report.append("| CLI | Status |")
        report.append("|-----|--------|")
        for cli, found in results['cli_detection'].items():
            status = "✅ Found" if found else "❌ Not Found"
            report.append(f"| {cli} | {status} |")
        report.append("")
    
    if 'component_detection' in results:
        report.append("## Component Detection Results\n")
        report.append("| Component | Version | Status |")
        report.append("|-----------|---------|--------|")
        for component, (installed, version) in results['component_detection'].items():
            status = "✅ Installed" if installed else "❌ Not Installed"
            report.append(f"| {component} | {version} | {status} |")
        report.append("")
    
    if 'template_structure' in results:
        report.append("## Template Structure Results\n")
        report.append("| Path | Status |")
        report.append("|------|--------|")
        for path, found in results['template_structure'].items():
            status = "✅ Found" if found else "❌ Missing"
            report.append(f"| {path} | {status} |")
        report.append("")
    
    if 'init_test' in results:
        report.append("## Init Command Test\n")
        status = "✅ Passed" if results['init_test'] else "❌ Failed"
        report.append(f"Result: {status}\n")
    
    return "\n".join(report)

def main():
    """Run all tests and generate report."""
    print("=" * 60)
    print("MultiAgent Core Detection Tests")
    print("=" * 60)
    
    all_results = {}
    
    # Run CLI detection
    print("\n📋 Testing CLI Detection...")
    print("-" * 40)
    all_results['cli_detection'] = test_cli_detection()
    
    # Run component detection
    print("\n📦 Testing Component Detection...")
    print("-" * 40)
    all_results['component_detection'] = test_component_detection()
    
    # Run template structure test
    print("\n📁 Testing Template Structure...")
    print("-" * 40)
    all_results['template_structure'] = test_template_structure()
    
    # Run init command test
    print("\n🚀 Testing Init Command...")
    print("-" * 40)
    all_results['init_test'] = test_init_command()
    
    # Generate report
    print("\n" + "=" * 60)
    print("TEST REPORT")
    print("=" * 60)
    report = generate_report(all_results)
    print(report)
    
    # Save report to file
    report_file = Path("test-report.md")
    report_file.write_text(report)
    print(f"\n📄 Report saved to {report_file}")
    
    # Determine exit code
    failures = 0
    if not all(all_results.get('cli_detection', {}).values()):
        failures += 1
    if not all_results.get('init_test', False):
        failures += 1
    
    if failures > 0:
        print(f"\n❌ {failures} test(s) failed")
        sys.exit(1)
    else:
        print("\n✅ All tests passed!")
        sys.exit(0)

if __name__ == "__main__":
    main()