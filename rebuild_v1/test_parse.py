"""Minimal parser validation for JSON cleaning."""
from engine_llm import parse_action_text


def run_case(name: str, text: str) -> None:
    result = parse_action_text(text)
    status = "PASS" if result is not None else "FAIL"
    print(f"{name}: {status} -> {result}")


def main() -> None:
    wrapped = """
```json
{"type": "wait", "seconds": 1}
```
"""
    noisy = "Some intro {\n  \"type\": \"done\", \"reason\": \"ok\"\n}\n trailing"
    run_case("Wrapped JSON", wrapped)
    run_case("Noisy text", noisy)


if __name__ == "__main__":
    main()
