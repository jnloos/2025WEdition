from pathlib import Path
from pylib.LatencyResult import LatencyResult
from pylib.LatencyTest import LatencyTest


def main():
    # Load and configure test
    cpp_path = Path(__file__).parent / "cpp" / "PipelineMsg"
    test = LatencyTest(str(cpp_path))

    test.set_title("Pipeline Message")
    test.set_conf(0.8)
    test.set_unit("us")

    # Execute measurement and collect statistics
    summary = test.exec(reps=1000)

    # Wrap in LatencyResult for visualization and persistence
    result = LatencyResult(test.title, summary)
    result.show()
    result.save(Path(__file__).parent / "results" / "pipeline_msg.json")
    print(result.dict())


if __name__ == "__main__":
    main()
