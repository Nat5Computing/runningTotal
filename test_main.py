import unittest
import ast

class TestFruitStandCode(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open("main.py", "r") as f:
            cls.code = f.read()
            cls.tree = ast.parse(cls.code)

    def test_welcome_message_present(self):
        # Check if the word 'welcome' appears (case-insensitive)
        self.assertIn("welcome", self.code.lower(), "Missing welcome message.")

    def test_input_variable_saved(self):
        # Check that input() is used and stored in a variable
        inputs = [node for node in ast.walk(self.tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "input"]
        assigned = [node for node in ast.walk(self.tree) if isinstance(node, ast.Assign)]
        found = False
        for assign in assigned:
            if isinstance(assign.value, ast.Call) and isinstance(assign.value.func, ast.Name) and assign.value.func.id == "input":
                found = True
        self.assertTrue(found, "Input is not stored in a variable.")

    def test_total_price_initialised_to_zero(self):
        # Check total_price = 0 is present
        assigned = [node for node in ast.walk(self.tree) if isinstance(node, ast.Assign)]
        match = any(
            isinstance(a.targets[0], ast.Name) and a.targets[0].id == "total_price"
            and isinstance(a.value, ast.Constant) and a.value.value == 0
            for a in assigned
        )
        self.assertTrue(match, "total_price is not initially set to 0.")

    def test_for_loop_uses_input_variable(self):
        # Check there's a for loop using range with input variable
        for_loops = [node for node in ast.walk(self.tree) if isinstance(node, ast.For)]
        found = False
        for loop in for_loops:
            if isinstance(loop.iter, ast.Call) and isinstance(loop.iter.func, ast.Name) and loop.iter.func.id == "range":
                if isinstance(loop.iter.args[0], ast.Name):
                    found = True
        self.assertTrue(found, "For loop does not use input variable to control iteration.")

    def test_running_total_inside_loop(self):
        # Look for total_price += price or similar
        aug_assigns = [node for node in ast.walk(self.tree) if isinstance(node, ast.AugAssign)]
        found = False
        for node in aug_assigns:
            if isinstance(node.target, ast.Name) and node.target.id == "total_price":
                if isinstance(node.op, ast.Add):
                    found = True
        self.assertTrue(found, "Running total not correctly used in loop.")

    def test_final_concatenated_sentence(self):
        # Look for a print that contains "Your total is £"
        self.assertIn("Your total is £", self.code, "Missing final concatenated sentence.")

if __name__ == '__main__':
    unittest.main()
