try:
    from braket.aws import AwsDevice, AwsQuantumTask
    from braket.circuits import Circuit
    from braket.devices import Devices, LocalSimulator
except ImportError:
    AwsDevice = AwsQuantumTask = Circuit = LocalSimulator = None

    class Devices:
        SIMULATOR = "simulator"


from .hardware_backend import HardwareBackend

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


class AwsBackendError(Exception):
    pass


class AwsBackend(HardwareBackend):
    def __init__(
        self,
        machine_name: str | Devices = "simulator",  # 默认是模拟器
        ignore=False,
    ) -> None:
        self._lab_id = None
        self._ignore = ignore
        self._position = None
        self._status = None
        self._circuit = None
        if machine_name == "simulator":
            self._device = LocalSimulator()
        else:
            self._device = AwsDevice(machine_name)
            if not self._ignore:
                print(
                    "this machine's task number in queue is: ",
                    self._device.queue_depth().quantum_tasks,
                )
        # self.max_wait_time = max_wait_time

    @property
    def task_id(self):
        return self._lab_id

    @property
    def position(self):
        return self._position

    @property
    def status(self):
        return self._status

    def get_ir(self):
        for instr in self._circuit.instructions:
            print(instr)

    def sample(self, qcis, shots=100) -> str | dict:
        """qcis: qcis command in string format connected by '\n'"""
        line_data = qcis.split("\n")
        qdic = self.check(line_data)
        qc = self.get_cq(line_data, qdic)

        if isinstance(self._device, LocalSimulator):
            task = self._device.run(qc, shots=shots)
            return dict(task.result().measurement_counts)
        else:
            task = self._device.run(qc, shots=shots)
            self._lab_id = task.id
            return self._lab_id

    def query_sample_result(self, task_id):
        task = AwsQuantumTask(arn=task_id)
        status = task.state()
        self._status = status
        self._position = task.queue_position().queue_position
        if self._status == "COMPLETED":
            results = task.result()
            counts = results.measurement_counts
            return dict(counts)
        elif self._status in ["FAILED", "CANCELLED"]:
            print(
                "Your quantum task is in terminal status by some reason maybe There is something wrong with the machine ."
            )
            return task
        else:
            print(
                "Sorry, your quantum task is still being processed and has not been finalized yet."
            )
            if not self._ignore:
                print(
                    "queue position you are now is: ",
                    task.queue_position().queue_position,
                )
            return task

    @staticmethod
    def check(line_data: list[str]) -> tuple[int, dict]:
        """检查qcis代码，获取qubit字符串表示和qubit索引的映射dict.
        line_data(list[str]): qcis command with str command of each line in the list.
        returns:
            qdic(dict): qubit mapping dictionary {"Q0": 0, "Q1": 1, ...}.
        """
        qdic = {}
        qnum = 0
        for idx, line in enumerate(line_data):
            line = line.strip()  # CZ Q1 Q0
            if not line:
                continue
            strArr = line.split(" ")
            if strArr[0] not in gate_list:
                raise AwsBackendError(f"error: in line {idx}, gate error")
            if len(strArr) < 2 or len(strArr) > 4:
                raise AwsBackendError(f"error: in line {idx}, qbit number error")
            if strArr[1][0] != "Q" or not strArr[1][1:].isdigit():
                raise AwsBackendError(f"error: in line {idx}, qbit syntax error")

            if strArr[1] not in qdic:
                qdic[strArr[1]] = qnum
                qnum += 1

            if strArr[0] in ["CZ", "CY", "CX", "CNOT"]:  # CZ Q1 Q0
                if len(strArr) != 3:
                    raise AwsBackendError(f"error: in line {idx}, qbit number error")

                if strArr[2][0] != "Q" or not strArr[2][1:].isdigit():
                    raise AwsBackendError(f"error: in line {idx}, qbit syntax error")

                if strArr[2] not in qdic:
                    qdic[strArr[2]] = qnum
                    qnum += 1
            if strArr[0] in ["RX", "RY", "RZ"]:  # RY Q3 0.39
                if len(strArr) != 3:
                    raise AwsBackendError(f"error: in line {idx}, qbit number error")
            if strArr[0] == "RXY":
                if len(strArr) != 4:
                    raise AwsBackendError(f"error: in line {idx}, qbit number error")

        return qdic

    def get_cq(
        self,
        line_data,
        qdic: dict,
    ) -> tuple:
        """
        Args:
            line_data(list[str]): qcis command with str command of each line in the list.
            qdic(dict): qubit mapping dictionary {"Q0": 0, "Q1": 1, ...}.
        """
        qc = Circuit()
        mq = []
        for line in line_data:
            line = line.strip()  # CZ Q1 Q0
            if not line:
                continue
            strArr = line.split(" ")
            q_idx1 = qdic[strArr[1]]
            if strArr[0] == "M":
                mq.append(q_idx1)
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
        qc.measure(mq)
        self._circuit = qc
        return qc
