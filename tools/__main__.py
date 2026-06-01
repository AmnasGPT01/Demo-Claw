"""Public entry point: `python -m tools` lists available tools."""
from .finance import TOOL_REGISTRY


def main() -> None:
    print("Registered finance tools:")
    for name in sorted(TOOL_REGISTRY):
        fn = TOOL_REGISTRY[name]
        doc = (fn.__doc__ or "").strip().splitlines()[0]
        print(f"  - {name}: {doc}")


if __name__ == "__main__":
    main()
