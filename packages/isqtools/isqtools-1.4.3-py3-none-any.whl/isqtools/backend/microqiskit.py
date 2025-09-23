import json
import random
from copy import deepcopy
from math import cos, pi, sin

r2 = 0.70710678118


class QuantumCircuit:
    def __init__(self, n, m=0):
        self.num_qubits = n
        self.num_clbits = m
        self.name = ""
        self.data = []

    def __add__(self, self2):
        self3 = QuantumCircuit(
            max(self.num_qubits, self2.num_qubits),
            max(self.num_clbits, self2.num_clbits),
        )
        self3.data = self.data + self2.data
        self3.name = self.name
        return self3

    def initialize(self, k):
        self.data[:] = []
        self.data.append(("init", [e for e in k]))

    def x(self, q):
        self.data.append(("x", q))

    def y(self, q):
        self.rz(pi, q)
        self.x(q)

    def z(self, q):
        self.rz(pi, q)

    def rx(self, theta, q):
        self.data.append(("rx", theta, q))

    def ry(self, theta, q):
        self.data.append(("ry", theta, q))

    def rz(self, theta, q):
        self.data.append(("rz", theta, q))

    def cx(self, s, t):
        self.data.append(("cx", s, t))

    def h(self, q):
        self.data.append(("h", q))

    # def crx(self, theta, s, t):
    #     self.data.append(("crx", theta, s, t))

    def dumps(self):
        data = deepcopy(self.data)
        data.insert(0, ("qubits", self.num_qubits, self.num_clbits))
        return json.dumps(data)

    def measure(self, q, b):
        assert b < self.num_clbits, "Index for output bit out of range."
        assert q < self.num_qubits, "Index for qubit out of range."
        self.data.append(("m", q, b))


def simulate(qc, shots=1024, get="counts", noise_model=[]):
    def superpose(x, y):
        return [r2 * (x[j] + y[j]) for j in range(2)], [
            r2 * (x[j] - y[j]) for j in range(2)
        ]

    def turn(x, y, theta):
        theta = float(theta)
        return [
            x[0] * cos(theta / 2) + y[1] * sin(theta / 2),
            x[1] * cos(theta / 2) - y[0] * sin(theta / 2),
        ], [
            y[0] * cos(theta / 2) + x[1] * sin(theta / 2),
            y[1] * cos(theta / 2) - x[0] * sin(theta / 2),
        ]

    def phaseturn(x, y, theta):
        theta = float(theta)
        return [
            [
                x[0] * cos(theta / 2) - x[1] * sin(-theta / 2),
                x[1] * cos(theta / 2) + x[0] * sin(-theta / 2),
            ],
            [
                y[0] * cos(theta / 2) - y[1] * sin(+theta / 2),
                y[1] * cos(theta / 2) + y[0] * sin(+theta / 2),
            ],
        ]

    k = [[0, 0] for _ in range(2**qc.num_qubits)]
    k[0] = [1.0, 0.0]
    if noise_model:
        if type(noise_model) is float:
            noise_model = [noise_model] * qc.num_qubits
    outputnum_clbitsap = {}
    for gate in qc.data:
        if gate[0] == "init":
            if type(gate[1][0]) is list:
                k = [e for e in gate[1]]
            else:
                k = [[e, 0] for e in gate[1]]
        elif gate[0] == "m":
            outputnum_clbitsap[gate[2]] = gate[1]
        elif gate[0] in ["x", "h", "rx", "rz"]:
            j = gate[-1]
            for i0 in range(2**j):
                for i1 in range(2 ** (qc.num_qubits - j - 1)):
                    b0 = i0 + 2 ** (j + 1) * i1
                    b1 = b0 + 2**j
                    if gate[0] == "x":
                        k[b0], k[b1] = k[b1], k[b0]
                    elif gate[0] == "h":
                        k[b0], k[b1] = superpose(k[b0], k[b1])
                    elif gate[0] == "rx":
                        theta = gate[1]
                        k[b0], k[b1] = turn(k[b0], k[b1], theta)
                    elif gate[0] == "rz":
                        theta = gate[1]
                        k[b0], k[b1] = phaseturn(k[b0], k[b1], theta)
        elif gate[0] in ["cx", "crx"]:
            if gate[0] == "cx":
                [s, t] = gate[1:]
            else:
                theta = gate[1]
                [s, t] = gate[2:]
            [l, h] = sorted([s, t])
            for i0 in range(2**l):
                for i1 in range(2 ** (h - l - 1)):
                    for i2 in range(2 ** (qc.num_qubits - h - 1)):
                        b0 = i0 + 2 ** (l + 1) * i1 + 2 ** (h + 1) * i2 + 2**s
                        b1 = b0 + 2**t
                        if gate[0] == "cx":
                            k[b0], k[b1] = k[b1], k[b0]
                        else:
                            k[b0], k[b1] = turn(k[b0], k[b1], theta)
    if get == "statevector":
        return k
    else:
        probs = [e[0] ** 2 + e[1] ** 2 for e in k]
        if noise_model:
            for j in range(qc.num_qubits):
                p_meas = noise_model[j]
                for i0 in range(2**j):
                    for i1 in range(2 ** (qc.num_qubits - j - 1)):
                        b0 = i0 + 2 ** (j + 1) * i1
                        b1 = b0 + 2**j
                        p0 = probs[b0]
                        p1 = probs[b1]
                        probs[b0] = (1 - p_meas) * p0 + p_meas * p1
                        probs[b1] = (1 - p_meas) * p1 + p_meas * p0
        if get == "probabilities_dict":
            return {
                ("{0:0" + str(qc.num_qubits) + "b}").format(j): p
                for j, p in enumerate(probs)
            }
        elif get in ["counts", "memory"]:
            m = [False for _ in range(qc.num_qubits)]
            for gate in qc.data:
                for j in range(qc.num_qubits):
                    assert not ((gate[-1] == j) and m[j]), (
                        "Incorrect or missing measure command."
                    )
                    m[j] = gate == ("m", j, j)
            m = []
            for _ in range(shots):
                cumu = 0
                un = True
                r = random.random()
                for j, p in enumerate(probs):
                    cumu += p
                    if r < cumu and un:
                        raw_out = ("{0:0" + str(qc.num_qubits) + "b}").format(j)
                        out_list = ["0"] * qc.num_clbits
                        for bit in outputnum_clbitsap:
                            out_list[qc.num_clbits - 1 - bit] = raw_out[
                                qc.num_qubits - 1 - outputnum_clbitsap[bit]
                            ]
                        out = "".join(out_list)
                        m.append(out)
                        un = False
            if get == "memory":
                return m
            else:
                counts = {}
                for out in m:
                    if out in counts:
                        counts[out] += 1
                    else:
                        counts[out] = 1
                return counts


{
    "results": [
        {
            "columns": [
                "task_id",
                "device",
                "source",
                "shots",
                "status",
                "user_id",
                "create_time",
                "update_time",
                "start_time",
                "finish_time",
            ],
            "types": [
                "integer",
                "text(50)",
                "text(10)",
                "integer(11)",
                "integer(1)",
                "integer",
                "datetime",
                "datetime",
                "datetime",
                "datetime",
            ],
            "values": [
                [
                    5,
                    None,
                    None,
                    100,
                    2,
                    1,
                    "2024-05-15T03:46:04Z",
                    "2024-05-15T03:46:04Z",
                    "2024-05-15T03:46:04Z",
                    "2024-05-15T03:46:04Z",
                ]
            ],
        }
    ]
}
