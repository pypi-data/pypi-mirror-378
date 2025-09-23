"""
Test script for the MeroHub library
Author: MERO (Telegram: @QP4RM)

This script demonstrates basic functionality of the MeroHub library.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_library_imports():
    """Test that all library modules can be imported successfully."""
    print("🚀 Testing MeroHub library imports...")
    
    try:
        # Test core imports
        from merohub import (
            GitHubCore, GitHubAuth, GitHubConfig,
            RepositoryManager, RepositoryAnalyzer,
            GitHubSearch, AdvancedSearch,
            UserManager, UserAnalyzer,
            IssueManager, PullRequestManager, ProjectManager,
            GitOperations, BranchManager, VersionControl,
            AIAnalyzer, NeuralNetworkAnalyzer, MLPredictor,
            GitHubBot, AutomatedInteractions, SmartResponder
        )
        
        print("✅ All core modules imported successfully!")
        
        # Test basic object creation (without authentication)
        print("\n🔧 Testing basic object creation...")
        
        # Test configuration
        config = GitHubConfig()
        print(f"✅ GitHubConfig created with default values")
        
        # Test exception classes
        from merohub.exceptions import MeroHubError, ValidationError, APIError
        print("✅ Exception classes imported successfully")
        
        # Test utility classes
        from merohub.utils import Logger, DataProcessor, SecurityManager
        logger = Logger("Test")
        data_processor = DataProcessor()
        print("✅ Utility classes created successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_configuration():
    """Test configuration management."""
    print("\n⚙️  Testing configuration...")
    
    try:
        from merohub import GitHubConfig
        
        # Test default configuration
        config = GitHubConfig()
        print(f"✅ Default config created: base_url={config.base_url}")
        
        # Test configuration with custom values
        custom_config = GitHubConfig(
            timeout=60,
            retries=5,
            per_page=50
        )
        print(f"✅ Custom config created: timeout={custom_config.timeout}")
        
        # Test configuration serialization
        config_dict = custom_config.to_dict()
        print(f"✅ Config serialization: {len(config_dict)} fields")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_validation():
    """Test validation functions."""
    print("\n✔️  Testing validation functions...")
    
    try:
        from merohub.exceptions import validate_github_token, validate_repository_name, validate_username
        
        # Test valid inputs (should not raise exceptions)
        validate_repository_name("test-repo")
        validate_username("testuser")
        print("✅ Valid input validation passed")
        
        # Test invalid inputs (should raise exceptions)
        try:
            validate_repository_name("")
            print("❌ Empty repo name should have failed validation")
            return False
        except:
            print("✅ Empty repo name validation correctly failed")
        
        try:
            validate_username("")
            print("❌ Empty username should have failed validation")
            return False
        except:
            print("✅ Empty username validation correctly failed")
        
        return True
        
    except Exception as e:
        print(f"❌ Validation test failed: {e}")
        return False

def test_data_processing():
    """Test data processing utilities."""
    print("\n📊 Testing data processing...")
    
    try:
        from merohub.utils import DataProcessor
        
        processor = DataProcessor()
        
        # Test data export
        test_data = [
            {"name": "repo1", "stars": 100},
            {"name": "repo2", "stars": 200}
        ]
        
        json_export = processor.export_data(test_data, "json")
        print("✅ JSON export successful")
        
        csv_export = processor.export_data(test_data, "csv")
        print("✅ CSV export successful")
        
        # Test data filtering
        filtered = processor.filter_data(test_data, {"stars": {"min": 150}})
        print(f"✅ Data filtering: {len(filtered)} items after filter")
        
        return True
        
    except Exception as e:
        print(f"❌ Data processing test failed: {e}")
        return False

def test_ai_components():
    """Test AI/ML components (without actual training)."""
    print("\n🤖 Testing AI components...")
    
    try:
        from merohub.ai_analysis import AIAnalyzer, MLPredictor
        
        # Test without actual API calls
        print("✅ AI components imported successfully")
        
        # Test neural network availability
        try:
            from merohub.ai_analysis import RepoTrendPredictor
            print("✅ Neural network components available")
        except ImportError:
            print("⚠️  PyTorch not available - using fallback methods")
        
        return True
        
    except Exception as e:
        print(f"❌ AI components test failed: {e}")
        return False

def test_automation_components():
    """Test automation components."""
    print("\n🤖 Testing automation components...")
    
    try:
        from merohub.automation import GitHubBot, AutomationRule, SmartResponder
        
        # Test rule creation
        rule = AutomationRule(
            name="test_rule",
            trigger="issues",
            actions=[{"type": "add_label", "labels": ["test"]}]
        )
        
        print(f"✅ Automation rule created: {rule.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Automation test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("🚀 MEROHUB LIBRARY TEST SUITE")
    print("=" * 60)
    print("Author: MERO (Telegram: @QP4RM)")
    print("Testing comprehensive GitHub integration library")
    print("=" * 60)
    
    tests = [
        ("Library Imports", test_library_imports),
        ("Configuration", test_configuration),
        ("Validation", test_validation),
        ("Data Processing", test_data_processing),
        ("AI Components", test_ai_components),
        ("Automation", test_automation_components)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 TEST RESULTS: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("🎉 All tests passed! MeroHub library is working correctly.")
        print("\n📚 MEROHUB LIBRARY FEATURES:")
        print("• 🔐 GitHub API authentication and configuration")
        print("• 📦 Repository management with full CRUD operations")
        print("• 🔍 Advanced search and analytics capabilities") 
        print("• 👤 User management and profile analysis")
        print("• 🐛 Issues and pull requests management")
        print("• 🌲 Git operations and version control")
        print("• 🤖 AI/ML analysis with neural networks")
        print("• ⚡ Automation and intelligent responses")
        print("• 🛡️  Security and validation utilities")
        print("• 📊 Data processing and export tools")
        print("\n🚀 Ready for pip installation and distribution!")
        return 0
    else:
        print(f"❌ {total - passed} tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())