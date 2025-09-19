from __future__ import annotations

try:
    from quafu import QuantumCircuit, User
except Exception:
    User = None
    QuantumCircuit = None

from ..hardware_backend import HardwareBackend
from .qua_task import Task

gate_list: list[str] = [
    "H",
    "X",
    "Y",
    "Z",
    "S",
    "T",
    "RZ",
    "RX",
    "RY",
    "SD",
    "TD",
    "X2M",
    "X2P",
    "Y2M",
    "Y2P",
    "CZ",
    "CY",
    "CX",
    "CNOT",
    "M",
    "RXY",
]


class QuafuBackendError(Exception):
    """Quafu backend error"""


class QuafuBackend(HardwareBackend):
    """the backend of quafu quantum hardware"""

    def __init__(
        self,
        machine_name: str = "Baihua",
        token: str = None,
    ) -> None:
        self._token = token
        self._machine_name = machine_name
        self._task = Task()
        if token:
            self._user = User(self._token)
            self._user.save_apitoken()
        else:
            self._user = User()

    @property
    def available_backends(self):
        """get available backends in quadu"""
        self._user.get_available_backends()

    def get_ir(self):
        """String for the name of the operator."""
        return self._circuit.instructions

    def sample(self, qcis, shots=100) -> str:
        """qcis: qcis command in string format connected by '\n'"""
        line_data = qcis.split("\n")
        qdic, qnum = self.check(line_data)
        qc = self.get_cq(line_data, qdic, qnum)
        self._task.config(backend=self._machine_name, shots=shots, compile=True)
        _, task_id = self._task.send(qc)
        return task_id

    def query_sample_result(self, task_id) -> dict[str, int]:
        result = self._task.retrieve(task_id)
        return dict(result.counts)

    @staticmethod
    def check(line_data: list[str]) -> tuple[int, dict]:
        """检查qcis代码，获取qubit字符串表示同qubit索引的映射dict.
        line_data(list[str]): qcis command with str command of each line in the list.
        returns:
            qdic(dict): qubit mapping dictionary {"Q0": 0, "Q1": 1, ...}.
            qnum(int): qubit number
        """
        qdic = {}
        qnum = 0
        for idx, line in enumerate(line_data):
            line = line.strip()  # CZ Q1 Q0
            if not line:
                continue
            strArr = line.split(" ")
            if strArr[0] not in gate_list:
                raise QuafuBackendError(f"error: in line {idx}, gate error")
            if len(strArr) < 2 or len(strArr) > 4:
                raise QuafuBackendError(f"error: in line {idx}, qbit number error")
            if strArr[1][0] != "Q" or not strArr[1][1:].isdigit():
                raise QuafuBackendError(f"error: in line {idx}, qbit syntax error")

            if strArr[1] not in qdic:
                qdic[strArr[1]] = qnum
                qnum += 1

            if strArr[0] in ["CZ", "CY", "CX", "CNOT"]:  # CZ Q1 Q0
                if len(strArr) != 3:
                    raise QuafuBackendError(f"error: in line {idx}, qbit number error")

                if strArr[2][0] != "Q" or not strArr[2][1:].isdigit():
                    raise QuafuBackendError(f"error: in line {idx}, qbit syntax error")

                if strArr[2] not in qdic:
                    qdic[strArr[2]] = qnum
                    qnum += 1
            if strArr[0] in ["RX", "RY", "RZ"]:  # RY Q3 0.39
                if len(strArr) != 3:
                    raise QuafuBackendError(f"error: in line {idx}, qbit number error")
            if strArr[0] == "RXY":
                if len(strArr) != 4:
                    raise QuafuBackendError(f"error: in line {idx}, qbit number error")

        return qdic, qnum

    def get_cq(self, line_data, qdic: dict, qnum: int) -> QuantumCircuit:
        """
        Args:
            line_data(list[str]): qcis command with str command of each line in the list.
            qdic(dict): qubit mapping dictionary {"Q0": 0, "Q1": 1, ...}.
        """
        mq = []
        for line in line_data:
            line = line.strip()  # CZ Q1 Q0
            if not line:
                continue
            strArr = line.split(" ")
            q_idx1 = qdic[strArr[1]]
            if strArr[0] == "M":  # M Q0
                mq.append(q_idx1)

        qc = QuantumCircuit(qnum, len(mq))
        for line in line_data:
            line = line.strip()  # CZ Q1 Q0
            if not line:
                continue
            strArr = line.split(" ")
            q_idx1 = qdic[strArr[1]]
            if strArr[0] == "M":  # M Q0
                pass
            else:
                if strArr[0] in ["CZ", "CY", "CX", "CNOT"]:
                    q_idx2 = qdic[strArr[2]]
                    getattr(qc, strArr[0].lower())(q_idx1, q_idx2)
                elif strArr[0] in ["RX", "RY", "RZ"]:  # RY Q3 0.39 RXY
                    theta = []
                    theta.append(eval(strArr[2]))
                    getattr(qc, strArr[0].lower())(q_idx1, theta)
                else:
                    getattr(qc, strArr[0].lower())(q_idx1)
        qc.measure(mq, list(range(len(mq))))
        self._circuit = qc
        return qc
