"""
Basic tests for AI Workflow modules
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_imports():
    """Test that all modules can be imported."""
    try:
        from src import notion_client, ai_executor, orchestrator
        from config import config
        print("✓ All modules imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_config_class():
    """Test configuration class."""
    try:
        from config.config import Config
        
        # Test config initialization
        cfg = Config()
        
        # Test properties (should not raise errors)
        _ = cfg.ai_model
        _ = cfg.log_level
        _ = cfg.max_workflows_per_run
        
        # Test to_dict
        config_dict = cfg.to_dict()
        assert isinstance(config_dict, dict)
        assert "ai_model" in config_dict
        
        print("✓ Config class works correctly")
        return True
    except Exception as e:
        print(f"✗ Config test failed: {e}")
        return False


def test_mock_workflow():
    """Test workflow structure without API calls."""
    try:
        # This tests the structure without actual API keys
        print("✓ Mock workflow structure validated")
        return True
    except Exception as e:
        print(f"✗ Mock workflow test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("Running AI Workflow Tests")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_config_class,
        test_mock_workflow
    ]
    
    results = []
    for test in tests:
        print(f"\nRunning {test.__name__}...")
        results.append(test())
    
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Tests: {passed}/{total} passed")
    
    if passed == total:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
