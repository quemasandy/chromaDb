#!/usr/bin/env python3
"""
Script to verify Ubuntu's global Python environment is working properly
Tests core functionality, system integration, and essential modules
"""

import sys
import os
import subprocess
import importlib
import tempfile
import json
from pathlib import Path


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def print_success(message):
    """Print success message"""
    print(f"✅ {message}")


def print_error(message):
    """Print error message"""
    print(f"❌ {message}")


def print_warning(message):
    """Print warning message"""
    print(f"⚠️  {message}")


def test_python_basics():
    """Test basic Python functionality"""
    print_section("BASIC PYTHON FUNCTIONALITY")

    # Test Python version
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Platform: {sys.platform}")

    # Test basic operations
    try:
        # Arithmetic operations
        result = 2 + 2 * 3
        assert result == 8
        print_success("Basic arithmetic operations work")

        # String operations
        text = "Hello " + "World"
        assert text == "Hello World"
        print_success("String operations work")

        # List operations
        numbers = [1, 2, 3]
        numbers.append(4)
        assert len(numbers) == 4
        print_success("List operations work")

        # Dictionary operations
        data = {"key": "value"}
        data["new_key"] = "new_value"
        assert len(data) == 2
        print_success("Dictionary operations work")

    except Exception as e:
        print_error(f"Basic operations failed: {e}")
        return False

    return True


def test_core_modules():
    """Test essential Python modules"""
    print_section("CORE PYTHON MODULES")

    essential_modules = [
        "os", "sys", "json", "datetime", "pathlib", "tempfile",
        "subprocess", "importlib", "collections", "itertools",
        "functools", "operator", "math", "random", "re"
    ]

    failed_modules = []

    for module_name in essential_modules:
        try:
            importlib.import_module(module_name)
            print_success(f"Module '{module_name}' imports successfully")
        except ImportError as e:
            print_error(f"Module '{module_name}' failed to import: {e}")
            failed_modules.append(module_name)

    return len(failed_modules) == 0


def test_system_integration():
    """Test Ubuntu system integration"""
    print_section("UBUNTU SYSTEM INTEGRATION")

    # Test file system operations
    try:
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            temp_path = f.name

        # Read the file
        with open(temp_path, 'r') as f:
            content = f.read()

        assert content == "test content"
        os.unlink(temp_path)
        print_success("File system operations work")

    except Exception as e:
        print_error(f"File system operations failed: {e}")
        return False

    # Test environment variables
    try:
        test_var = "PYTHON_TEST_VAR"
        os.environ[test_var] = "test_value"
        assert os.getenv(test_var) == "test_value"
        del os.environ[test_var]
        print_success("Environment variable operations work")

    except Exception as e:
        print_error(f"Environment variable operations failed: {e}")
        return False

    # Test subprocess execution
    try:
        result = subprocess.run(
            ["echo", "test"],
            capture_output=True,
            text=True,
            check=True
        )
        assert result.stdout.strip() == "test"
        print_success("Subprocess execution works")

    except Exception as e:
        print_error(f"Subprocess execution failed: {e}")
        return False

    return True


def test_ubuntu_specific_modules():
    """Test Ubuntu-specific Python modules"""
    print_section("UBUNTU-SPECIFIC MODULES")

    ubuntu_modules = [
        ("apt", "Python APT integration"),
        ("dbus", "D-Bus system integration"),
        ("gi", "GObject introspection (PyGObject)"),
    ]

    working_modules = 0

    for module_name, description in ubuntu_modules:
        try:
            if module_name == "apt":
                import apt
                cache = apt.Cache()
                print_success(f"{description} - APT cache accessible")
                working_modules += 1

            elif module_name == "dbus":
                import dbus
                print_success(f"{description} - D-Bus module available")
                working_modules += 1

            elif module_name == "gi":
                import gi
                print_success(
                    f"{description} - GObject introspection available")
                working_modules += 1

        except ImportError:
            print_warning(
                f"{description} - Module not available (this might be normal)")
        except Exception as e:
            print_warning(f"{description} - Available but test failed: {e}")

    return working_modules > 0


def test_package_management():
    """Test pip and package management functionality"""
    print_section("PACKAGE MANAGEMENT")

    try:
        # Test pip list command
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--format=json"],
            capture_output=True,
            text=True,
            check=True
        )

        packages = json.loads(result.stdout)
        print_success(f"pip list works - Found {len(packages)} packages")

        # Check for essential packages
        package_names = [pkg["name"].lower() for pkg in packages]
        essential_packages = ["pip", "setuptools", "wheel"]

        for pkg in essential_packages:
            if pkg in package_names:
                print_success(f"Essential package '{pkg}' is installed")
            else:
                print_warning(f"Essential package '{pkg}' not found")

        return True

    except subprocess.CalledProcessError as e:
        print_error(f"pip command failed: {e}")
        return False
    except json.JSONDecodeError as e:
        print_error(f"Failed to parse pip output: {e}")
        return False


def test_network_capabilities():
    """Test network-related functionality"""
    print_section("NETWORK CAPABILITIES")

    try:
        # Test socket creation (basic network capability)
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.close()
        print_success("Socket creation works")

        # Test DNS resolution
        import socket
        socket.gethostbyname("localhost")
        print_success("DNS resolution works")

        # Test if urllib is available
        import urllib.request
        print_success("urllib module available for HTTP requests")

        return True

    except Exception as e:
        print_error(f"Network functionality test failed: {e}")
        return False


def run_comprehensive_test():
    """Run all tests and provide summary"""
    print("🔍 UBUNTU PYTHON ENVIRONMENT VERIFICATION")
    print("This script verifies that Ubuntu's global Python environment is working correctly")

    tests = [
        ("Basic Python Functionality", test_python_basics),
        ("Core Python Modules", test_core_modules),
        ("System Integration", test_system_integration),
        ("Ubuntu-Specific Modules", test_ubuntu_specific_modules),
        ("Package Management", test_package_management),
        ("Network Capabilities", test_network_capabilities),
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print_error(f"Test '{test_name}' crashed: {e}")
            results[test_name] = False

    # Summary
    print_section("VERIFICATION SUMMARY")

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")

    print(f"\nOverall Result: {passed}/{total} tests passed")

    if passed == total:
        print_success("🎉 Ubuntu Python environment is working perfectly!")
        print("Your system is ready for development work.")
    elif passed >= total * 0.8:
        print_warning("⚠️  Ubuntu Python environment is mostly working.")
        print("Some advanced features may not be available, but basic functionality works.")
    else:
        print_error("❌ Ubuntu Python environment has significant issues.")
        print("You may need to reinstall or repair your Python installation.")

    return passed == total


if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
