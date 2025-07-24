import unittest
import ast
import io
import sys
import runpy

class TestFlexibleFruitStand(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Capture print output from main.py
        cls.captured_output = io.StringIO()
        sys.stdout = cls.captured_output

        # Simulated user input values
        test_input_values = ["5", "3", "2", "3", "4", "3"]
        input_iter = iter(test_input_values)
        input_count = {"count": 0}

        def mock_input(prompt=""):
            input_count["count"] += 1
            value = next(input_iter)

            # First prompt (e.g. "How many fruits:")
            if input_count["count"] == 1:
                print(f"{prompt}{value}")
            else:
                # Numbered prompt for each fruit price
                numbered_prompt = f"Enter price {input_count['count'] - 1}: "
                print(f"{numbered_prompt}{value}")
            return value

        # Patch built-in input
        original_input = __builtins__.input
        __builtins__.input = mock_input

        try:
            runpy.run_path("main.py", run_name="__main__")
        except Exception as e:
            print(f"\n[⚠️ Error running main.py: {e}]")
        finally:
            __builtins__.input = original_input
            sys.stdout = sys.__stdout__

        cls.output_text = cls.captured_output.getvalue()
        print("------ main.py OUTPUT ------")
        print(cls.output_text)
        print("------ END OUTPUT ------\n")

        # AST for static code checks
        with open("main.py", "r") as f:
            cls.tree = ast.parse(f.read())

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
                    if isinstance(inner, ast.AugAssign) and isinstance(inner.op, ast.Add):
                        found = True
                    if isinstance(inner, ast.Assign):
                        if (isinstance(inner.value, ast.BinOp) and isinstance(inner.value.op, ast.Add)):
                            targets = [t.id for t in inner.targets if isinstance(t, ast.Name)]
                            if isinstance(inner.value.left, ast.Name) and inner.value.left.id in targets:
                                found = True
        self.assertTrue(found, "Expected a running total using += or = total + ... inside a loop")

    def test_final_concatenated_sentence(self):
        code = self.output_text.lower().replace("â", "")
        self.assertIn("your total is £", code, "Missing 'Your total is £'")
        self.assertIn("thanks", code, "Missing 'Thanks' in the final message")

if __name__ == "__main__":
    unittest.main()
