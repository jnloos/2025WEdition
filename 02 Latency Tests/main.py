from pathlib import Path
from pylib.LatencyResult import LatencyResult
from pylib.LatencyTest import LatencyTest
import json


def __prompt_choice(prompt: str, options: list) -> int:
    print(f"\n{prompt}")
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
            print("\nInvalid input. Please enter a number.")

def __prompt_value(prompt: str, default, value_type=str):
    user_input = input(f"{prompt} [{default}]: ").strip()
    if not user_input:
        return default
    try:
        return value_type(user_input)
    except ValueError:
        print(f"Invalid input, using default: {default}")
        return default


def print_json(data: dict):
    json_str = json.dumps(data, indent=2)
    print(json_str)


# Find all .cpp files except helper files
def __scan_for_tests():
    cpp_dir = Path(__file__).parent / "cpp"
    if not cpp_dir.exists():
        return []

    cpp_files = sorted([f.stem for f in cpp_dir.glob("*.cpp")])
    cpp_files.remove("Stopwatch")
    return cpp_files


def __scan_for_results():
    """Scan results directory for available result files."""
    results_dir = Path(__file__).parent / "results"
    if not results_dir.exists():
        return []

    result_files = sorted(results_dir.glob("*.json"))
    return result_files


def load_results():
    result_files = __scan_for_results()
    if not result_files:
        print("\nNo existing results found.")
        return

    # Display available results
    options = [f.name for f in result_files]
    idx = __prompt_choice("Select a result file to load:", options)

    result_file = result_files[idx]
    result = LatencyResult.from_file(result_file)
    print(f"\nLoaded: {result_file.name}")
    print("\n" + "=" * 60)
    print_json(result.dict())
    print("=" * 60)

    show = input("\nDisplay interactive chart? (y/n) [y]: ").strip().lower()
    if show != 'n':
        result.show()


def run_tests():
    """Run a new latency test with user configuration."""
    print("\n=== Configure New Test ===")

    # Scan for available implementations
    implementations = __scan_for_tests()

    if not implementations:
        print("\nNo C++ implementations found in cpp directory.")
        return

    # Select implementation
    impl_idx = __prompt_choice("Select C++ implementation:", implementations)
    impl = implementations[impl_idx]

    # Configure test parameters
    title = __prompt_value("Test title", impl, str)
    reps = __prompt_value("Number of repetitions", 1000, int)
    conf = __prompt_value("Confidence level", 0.8, float)
    unit = __prompt_value("Time unit (s/ms/us/ns)", "us", str)

    # Load and configure test
    cpp_path = Path(__file__).parent / "cpp" / impl
    test = LatencyTest(str(cpp_path))

    test.set_title(title)
    test.set_conf(conf)
    test.set_unit(unit)

    # Execute measurement
    print(f"\nRunning test '{title}' with {reps} repetitions...")
    summary = test.exec(reps=reps)

    # Wrap in LatencyResult for visualization and persistence
    result = LatencyResult(test.title, summary)
    print("\n" + "=" * 60)
    print_json(result.dict())
    print("=" * 60)

    # Show results
    show = input("\nDisplay interactive chart? (y/n) [y]: ").strip().lower()
    if show != 'n':
        result.show()

    # Save results
    save = input("\nSave results? (y/n) [y]: ").strip().lower()
    if save != 'n':
        results_dir = Path(__file__).parent / "results"
        results_dir.mkdir(parents=True, exist_ok=True)

        default_name = f"{impl.lower()}.json"
        filename = __prompt_value("Output filename", default_name, str)
        if not filename.endswith('.json'):
            filename += '.json'

        output_path = results_dir / filename
        result.save(output_path)
        print(f"\nResults saved to: {output_path}")


def main():
    print("Latency Test Suite")
    mode_idx = __prompt_choice("What would you like to do?", ["Load existing results", "Run new test"])
    if mode_idx == 0:
        load_results()
    else:
        run_tests()


if __name__ == "__main__":
    main()