#!/usr/bin/env python3
"""
Test script for DataGuild Snowflake Connector package

This script tests the package installation, CLI functionality, and basic features.
"""

import subprocess
import sys
import os
import tempfile
import json
from pathlib import Path


def run_command(cmd, description):
    """Run a command and return the result"""
    print(f"\n🔧 {description}")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ {description} - SUCCESS")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"Error: {e.stderr}")
        return False


def test_package_installation():
    """Test package installation"""
    print("📦 Testing package installation...")
    
    # Test pip install
    success = run_command(
        [sys.executable, "-m", "pip", "install", "-e", "."],
        "Installing package in development mode"
    )
    
    if not success:
        return False
    
    # Test import
    try:
        import dataguild
        from dataguild.source.snowflake.main import SnowflakeV2Source
        from dataguild.source.snowflake.config import SnowflakeV2Config
        print("✅ Package import successful")
        print(f"Version: {dataguild.__version__}")
        return True
    except ImportError as e:
        print(f"❌ Package import failed: {e}")
        return False


def test_cli_functionality():
    """Test CLI functionality"""
    print("\n🖥️  Testing CLI functionality...")
    
    # Test help command
    success = run_command(
        [sys.executable, "-m", "dataguild.cli", "--help"],
        "Testing CLI help command"
    )
    
    if not success:
        return False
    
    # Test version command
    success = run_command(
        [sys.executable, "-m", "dataguild.cli", "version"],
        "Testing CLI version command"
    )
    
    if not success:
        return False
    
    # Test init-config command
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = os.path.join(temp_dir, "test_config.yml")
        
        success = run_command(
            [sys.executable, "-m", "dataguild.cli", "init-config", "--output", config_file],
            "Testing CLI init-config command"
        )
        
        if not success:
            return False
        
        # Verify config file was created
        if os.path.exists(config_file):
            print("✅ Config file created successfully")
        else:
            print("❌ Config file not created")
            return False
    
    return True


def test_basic_functionality():
    """Test basic package functionality"""
    print("\n🧪 Testing basic functionality...")
    
    try:
        # Test imports
        from dataguild.source.snowflake.main import SnowflakeV2Source
        from dataguild.source.snowflake.config import SnowflakeV2Config
        from dataguild.api.common import PipelineContext
        print("✅ Core imports successful")
        
        # Test configuration creation
        config = SnowflakeV2Config(
            account_id="test-account",
            username="test-user",
            password="test-password",
            warehouse="test-warehouse",
            database="test-database"
        )
        print("✅ Configuration creation successful")
        
        # Test context creation
        ctx = PipelineContext(run_id="test")
        print("✅ Context creation successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False


def test_examples():
    """Test example scripts"""
    print("\n📚 Testing example scripts...")
    
    examples_dir = Path("examples")
    if not examples_dir.exists():
        print("❌ Examples directory not found")
        return False
    
    # Test basic usage example
    basic_example = examples_dir / "basic_usage.py"
    if basic_example.exists():
        print("✅ Basic usage example found")
    else:
        print("❌ Basic usage example not found")
        return False
    
    # Test advanced usage example
    advanced_example = examples_dir / "advanced_usage.py"
    if advanced_example.exists():
        print("✅ Advanced usage example found")
    else:
        print("❌ Advanced usage example not found")
        return False
    
    # Test sample config
    sample_config = examples_dir / "sample_config.yml"
    if sample_config.exists():
        print("✅ Sample configuration found")
    else:
        print("❌ Sample configuration not found")
        return False
    
    return True


def test_documentation():
    """Test documentation files"""
    print("\n📖 Testing documentation...")
    
    # Check README
    if Path("README.md").exists():
        print("✅ README.md found")
    else:
        print("❌ README.md not found")
        return False
    
    # Check LICENSE
    if Path("LICENSE").exists():
        print("✅ LICENSE found")
    else:
        print("❌ LICENSE not found")
        return False
    
    # Check CHANGELOG
    if Path("CHANGELOG.md").exists():
        print("✅ CHANGELOG.md found")
    else:
        print("❌ CHANGELOG.md not found")
        return False
    
    return True


def run_tests():
    """Run the test suite"""
    print("\n🧪 Running test suite...")
    
    success = run_command(
        [sys.executable, "-m", "pytest", "tests/", "-v"],
        "Running pytest test suite"
    )
    
    return success


def main():
    """Main test function"""
    print("🚀 DataGuild Snowflake Connector Package Test")
    print("=" * 50)
    
    tests = [
        ("Package Installation", test_package_installation),
        ("CLI Functionality", test_cli_functionality),
        ("Basic Functionality", test_basic_functionality),
        ("Examples", test_examples),
        ("Documentation", test_documentation),
        ("Test Suite", run_tests)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if success:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Package is ready for distribution.")
        return 0
    else:
        print("⚠️  Some tests failed. Please fix issues before distribution.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
