from pathlib import Path
from pylib.LatencyTest import LatencyTest
from pylib.LatencyResult import LatencyResult
import json
from pylib.Importer import Importer


def results_dialog():
    result_files = __search_results()
    if not result_files:
        print("\nNothing found.")
        return

    options = [f.name for f in result_files]
    idx = __prompt_choice("\nSelect a result:", options)
    print("")

    result_file = result_files[idx]
    result = LatencyResult.from_file(result_file)
    print_json(result.dict())

    show = input("\nDisplay diagram? (y/n) [y]: ").strip().lower()
    if show != "n":
        result.show()


def test_dialog():
    impls = __search_tests()
    if not impls:
        print("\nNothing found.")
        return

    impl_idx = __prompt_choice("\nSelect a test:", impls)
    impl = impls[impl_idx]

    title = __prompt_value("\nTitle", impl, str)
    reps = __prompt_value("Repetitions", 10000, int)
    conf = __prompt_value("Confidence level", 0.95, float)

    units = ["s", "ms", "us", "ns"]
    unit_idx = __prompt_choice("\nTime unit:", units)
    unit = units[unit_idx]

    cpp_path = Path(__file__).parent / "cpp" / impl
    test = LatencyTest(str(cpp_path))
    test.set_title(title)
    test.set_conf(conf)
    test.set_unit(unit)

    print(f"\nRunning ...")
    result = test.exec(reps=reps)
    print("\n")
    print_json(result.dict())

    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    default_name = f"{impl.lower()}.json"
    filename = __prompt_value("\nStore as", default_name, str)
    if not filename.endswith(".json"):
        filename += ".json"

    output_path = results_dir / filename
    result.save(output_path)
    print("Saved.")


def __prompt_choice(prompt: str, options: list) -> int:
    print(f"{prompt}")
    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")

    while True:
        try:
            choice = input(f"Enter choice (1-{len(options)}): ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return idx
            print(f"Please enter a number between 1 and {len(options)}")
        except (ValueError, KeyboardInterrupt):
            print("Invalid input.")


def __prompt_value(prompt: str, default, value_type=str):
    user_input = input(f"{prompt} [{default}]: ").strip()
    if not user_input:
        return default
    try:
        return value_type(user_input)
    except ValueError:
        print(f"Invalid input, using default: {default}")
        return default


def __search_tests():
    cpp_dir = Path(__file__).parent / "cpp"
    if not cpp_dir.exists():
        return []
    cpp_files = sorted([f.stem for f in cpp_dir.glob("*.cpp")])
    if "Stopwatch" in cpp_files:
        cpp_files.remove("Stopwatch")
    return cpp_files


def __search_results():
    results_dir = Path(__file__).parent / "results"
    if not results_dir.exists():
        return []
    return sorted(results_dir.glob("*.json"))


def print_json(data: dict):
    print(json.dumps(data, indent=2))


def main():
    # Import stopwatch module
    imp = Importer()
    imp.cpp('cpp/Stopwatch')

    print("Latency Test Suite")
    while True:
        choice = __prompt_choice(
            "\nSelect mode:",
            ["Load results", "Execute test", "Exit"]
        )

        if choice == 0:
            results_dialog()
        elif choice == 1:
            test_dialog()
        elif choice == 2:
            print("\nBye.")
            break


if __name__ == "__main__":
    main()