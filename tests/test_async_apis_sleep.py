import ast
from pathlib import Path
import unittest


APIS_PATH = Path(__file__).resolve().parents[1] / "operate" / "models" / "apis.py"


class AsyncAPISleepTests(unittest.TestCase):
    def test_async_functions_do_not_call_blocking_time_sleep(self):
        tree = ast.parse(APIS_PATH.read_text(encoding="utf-8"))
        blocking_calls = []
        async_sleep_funcs = []

        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef):
                for sub in ast.walk(node):
                    if (
                        isinstance(sub, ast.Call)
                        and isinstance(sub.func, ast.Attribute)
                        and sub.func.attr == "sleep"
                        and isinstance(sub.func.value, ast.Name)
                    ):
                        if sub.func.value.id == "time":
                            blocking_calls.append((node.name, sub.lineno))
                        elif sub.func.value.id == "asyncio":
                            async_sleep_funcs.append(node.name)

        self.assertEqual(
            blocking_calls,
            [],
            f"Found blocking time.sleep() inside async functions: {blocking_calls}",
        )
        self.assertIn("call_gpt_4o_with_ocr", async_sleep_funcs)


if __name__ == "__main__":
    unittest.main()
