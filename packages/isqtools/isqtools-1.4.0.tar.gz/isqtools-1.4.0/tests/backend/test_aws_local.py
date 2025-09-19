import tempfile
from pathlib import Path

import pytest

from isqtools import IsqCircuit
from isqtools.backend import AwsBackend

TEST_FILE_CONTENT = """
import std;
unit main() {
    qbit q[2];
    H(q[1]);
    X(q[0]);
    M(q[0]);
    M(q[1]);
}
"""


def test_aws_locol(request):
    if not request.config.getoption("--run-aws-local"):
        pytest.skip("Skipping AwsBackend test since --run-aws-local is not set")
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        temp_file_path = temp_dir_path / "temp_file.isq"
        with open(temp_file_path, "w") as temp_file:
            temp_file.write(TEST_FILE_CONTENT)

        backend = AwsBackend()  # local

        qc = IsqCircuit(
            file=str(temp_file_path),
            sample=True,
            shots=100,
            backend=backend,
        )
        result = qc.measure()
        print(result)
