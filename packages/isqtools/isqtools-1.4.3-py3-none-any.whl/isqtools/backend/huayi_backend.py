from __future__ import annotations

import json
import os
import sys

try:
    from requests_toolbelt import sessions
except:
    pass

from .hardware_backend import HardwareBackend
from .microqiskit import QuantumCircuit

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


class HuayiBackendError(Exception):
    pass


class HuayiBackend(HardwareBackend):
    def __init__(
        self,
        token: str | None = None,
        max_wait_time: int = 5,
        machine_name: str = None,  # 默认是模拟器
        lab_id: int | None = None,
        url: str = "https://q-coding.hyqubit.com/",
        ignore=False,
    ) -> None:
        self._token = token
        self._lab_id = lab_id
        self._machine_name = machine_name
        self._max_wait_time = max_wait_time
        self._url = url
        self._ignore = ignore
        self._token_dir = os.path.join(self.get_homedir(), ".huayi")
        self._status = None
        self._circuit = None

        if token is None:
            self._token = self._load_account()
        else:
            self._token = token
            self._save_apitoken(self._token)

    @property
    def task_id(self):
        return self._lab_id

    @property
    def status(self):
        return self._status

    def get_ir(self):
        print(self._circuit.dumps())

    def _config_account(self):
        base = sessions.BaseUrlSession(base_url=self._url)
        base.headers = {"Authorization": self._token}
        return base

    def sample(self, qcis, shots=100) -> str:
        """qcis: qcis command in string format connected by '\n'"""
        line_data = qcis.split("\n")
        qdic, qnum = self.check(line_data)
        qc = self.get_cq(line_data, qdic, qnum)
        #
        base = self._config_account()
        self._lab_id = base.post(f"db/task?cols=shots&vals={shots}").json()["results"][
            0
        ]["last_insert_id"]
        res = base.put(f"file/task/{self._lab_id}/circuit", qc.dumps()).text
        if not self._ignore:
            print(f"Upload task {self._lab_id}: {res}")
        return self._lab_id

    def query_sample_result(self, task_id) -> dict[str, int]:
        base = self._config_account()
        res = base.get(f"db/task?cols=*&cond=task_id={task_id}").json()["results"][0][
            "values"
        ][0][4]
        if res == 0:
            print(f"Status of task {task_id} is uncompleted")
        elif res == 1:
            print(f"Status of task {task_id} is completed")
            counts = base.get(f"file/task/{task_id}/result").text
            return counts
        else:
            print(f"Status of task {task_id} is exception or completed")
            counts = base.get(f"file/task/{task_id}/result").text
            print(f"output of task {task_id} is: {counts}")
            return counts

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
                raise HuayiBackendError(f"error: in line {idx}, gate error")
            if len(strArr) < 2 or len(strArr) > 4:
                raise HuayiBackendError(f"error: in line {idx}, qbit number error")
            if strArr[1][0] != "Q" or not strArr[1][1:].isdigit():
                raise HuayiBackendError(f"error: in line {idx}, qbit syntax error")

            if strArr[1] not in qdic:
                qdic[strArr[1]] = qnum
                qnum += 1

            if strArr[0] in ["CZ", "CY", "CX", "CNOT"]:  # CZ Q1 Q0
                if len(strArr) != 3:
                    raise HuayiBackendError(f"error: in line {idx}, qbit number error")

                if strArr[2][0] != "Q" or not strArr[2][1:].isdigit():
                    raise HuayiBackendError(f"error: in line {idx}, qbit syntax error")

                if strArr[2] not in qdic:
                    qdic[strArr[2]] = qnum
                    qnum += 1
            if strArr[0] in ["RX", "RY", "RZ"]:  # RY Q3 0.39
                if len(strArr) != 3:
                    raise HuayiBackendError(f"error: in line {idx}, qbit number error")
            if strArr[0] == "RXY":
                if len(strArr) != 4:
                    raise HuayiBackendError(f"error: in line {idx}, qbit number error")

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
                    if strArr[0] == "CNOT":
                        strArr[0] = "CX"
                    q_idx2 = qdic[strArr[2]]
                    getattr(qc, strArr[0].lower())(q_idx1, q_idx2)
                elif strArr[0] in ["RX", "RY", "RZ"]:  # RY Q3 0.39 RXY
                    theta = []
                    theta.append(eval(strArr[2]))
                    getattr(qc, strArr[0].lower())(q_idx1, theta)
                else:
                    getattr(qc, strArr[0].lower())(q_idx1)
        for i, q in enumerate(mq):
            qc.measure(q, i)
        self._circuit = qc
        return qc

    def _load_account(self):
        file_dir = os.path.join(self._token_dir, "api")
        try:
            with open(file_dir, "r") as f:  # pylint: disable=unspecified-encoding
                data = json.load(f)  # 返回api文件中存储的数据为dict
                token = data["token"]
        except FileNotFoundError as exc:
            raise HuayiBackendError("Please provide the token.") from exc
        return token

    def _save_apitoken(self, token):
        data = {"token": token}
        file_path = os.path.join(self._token_dir, "api")
        if not os.path.exists(self._token_dir):
            os.mkdir(self._token_dir)  # 创建目录即使中间目录不存在
        with open(file_path, "w") as f:  # noqa:SCS109 # pylint: disable=unspecified-encoding
            json.dump(data, f)  # 将字典保存到文件f中

    @staticmethod
    def get_homedir():
        if sys.platform == "win32":
            return os.environ["USERPROFILE"]
        if sys.platform in ["darwin", "linux"]:
            return os.environ["HOME"]
        raise ValueError(
            f"unsupported platform:{sys.platform}. "
            f"You may raise a request issue on github."
        )
