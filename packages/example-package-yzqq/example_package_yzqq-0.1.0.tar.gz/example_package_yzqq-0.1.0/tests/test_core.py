"""
Tests for the core module.
"""

import pytest
from simple_package.core import Calculator, greet, fibonacci


class TestCalculator:
    """Test cases for Calculator class."""
    
    def test_add(self):
        calc = Calculator()
        assert calc.add(2, 3) == 5
        assert calc.add(-1, 1) == 0
        assert calc.add(0.1, 0.2) == pytest.approx(0.3)
    
    def test_subtract(self):
        calc = Calculator()
        assert calc.subtract(5, 3) == 2
        assert calc.subtract(0, 5) == -5
    
    def test_multiply(self):
        calc = Calculator()
        assert calc.multiply(4, 5) == 20
        assert calc.multiply(-2, 3) == -6
        assert calc.multiply(0, 100) == 0
    
    def test_divide(self):
        calc = Calculator()
        assert calc.divide(10, 2) == 5
        assert calc.divide(7, 2) == 3.5
        
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            calc.divide(5, 0)
    
    def test_history(self):
        calc = Calculator()
        calc.add(1, 2)
        calc.multiply(3, 4)
        
        history = calc.get_history()
        assert len(history) == 2
        assert "1 + 2 = 3" in history
        assert "3 * 4 = 12" in history
        
        calc.clear_history()
        assert len(calc.get_history()) == 0


def test_greet():
    """Test greet function."""
    assert greet() == "Hello, World!"
    assert greet("Alice") == "Hello, Alice!"
    assert greet("") == "Hello, !"


def test_fibonacci():
    """Test fibonacci function."""
    assert fibonacci(0) == 0
    assert fibonacci(1) == 1
    assert fibonacci(5) == 5
    assert fibonacci(10) == 55
    
    with pytest.raises(ValueError, match="n must be non-negative"):
        fibonacci(-1)