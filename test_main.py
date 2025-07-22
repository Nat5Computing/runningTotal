import unittest
import ast

class TestFlexibleFruitStand(unittest.TestCase):

    def setUp(self):
        with open("main.py", "r") as f:
            self.tree = ast.parse(f.read())

    def test_has_input_call(self):
        input_found = any(
            isinstance(node, ast.Call) and getattr(node.func, 'id', '') == 'input'
            for node in ast.walk(self.tree)
        )
        self.assertTrue(input_found, "Expected at least one call to input()")

    def test_has_loop(self):
        loop_found = any(isinstance(node, ast.For) for node in ast.walk(self.tree))
        self.assertTrue(loop_found, "Expected a for loop")

    def test_has_running_total(self):
        found = False
        for node in ast.walk(self.tree):
            if isinstance(node, ast.For):
                for inner in ast.walk(node):
                    # Check for total += price (AugAssign)
                    if isinstance(inner, ast.AugAssign) and isinstance(inner.op, ast.Add):
                        found = True
                    # Check for total = total + price (Assign)
                    if isinstance(inner, ast.Assign):
                        if (isinstance(inner.value, ast.BinOp) and isinstance(inner.value.op, ast.Add)):
                            targets = [t.id for t in inner.targets if isinstance(t, ast.Name)]
                            if isinstance(inner.value.left, ast.Name) and inner.value.left.id in targets:
                                found = True
        self.assertTrue(found, "Expected a running total using += or = total + ... inside a loop")

    import re

    def test_final_concatenated_sentence(self):
        with open("main.py", "r", encoding="utf-8", errors="ignore") as file:
            code = file.read().lower()
    
        code = code.replace("â", "")  # filter out weird characters
    
        self.assertIn("your total is £", code, "Missing 'Your total is £'")
        self.assertIn("str(", code, "Missing use of str() for concatenation")
        self.assertIn("+", code, "Missing string concatenation using '+'")


if __name__ == "__main__":
    unittest.main()
