import os

from pennylane.devices import Device
from pennylane.measurements import CountsMP, ExpectationMP
from qcaas_client.client import OQCClient, QPUTask, TaskStatus
from qcaas_client.compiler_config import (
    CompilerConfig,
    QuantumResultsFormat,
    Tket,
    TketOptimizations,
)
import numpy as np
from os import path
from typing import List
from time import sleep


class qcaas(Device):
    name = "OQC QCaaS PennyLane Plugin"
    short_name = "oqc_qcaas"
    config_filepath = path.join(path.dirname(__file__), "config.toml")

    def __init__(self, wires, **kwargs):
        self._check_envvar()
        self._num_shots = int(kwargs.get("shots", str(1000)))
        super().__init__(wires=wires)
        self.backend = kwargs.get("backend", "default_backend")
        self._client = OQCClient(url=self._url, authentication_token=self._auth_token)
        self.batch_limit = kwargs.get("batch_limit", 10)

    @property 
    def shots(self):
        return self._num_shots
    
    @property
    def num_wires(self):
        return len(self._wires)
    
    def _check_envvar(self):
        self._url = os.getenv("OQC_URL")
        self._auth_token = os.getenv("OQC_AUTH_TOKEN")
        self._device = os.getenv("OQC_DEVICE")
        if not all((self._url, self._auth_token, self._device)):
            raise ValueError("OQC_URL, OQC_AUTH_TOKEN and OQC_DEVICE must be set as environment variables.")

    @staticmethod
    def _expval_from_counts(observable, counts, wires, shots):
        """ 
        Returns <observable> from raw shot counts.
        """
        exp_val = 0.0
        wire_indices = [wires.index(i) for i in observable.wires]
        for bits, count in counts.items():
            exp_val += np.prod([(-1) ** int(bits[i]) for i in wire_indices]) * count / shots
        return exp_val

    def _batch_execute_qasm_programs(self, qasms: List[str], shot_list: List[int]):
        res_format = QuantumResultsFormat().binary_count()
        optimisations = Tket()
        optimisations.tket_optimizations = TketOptimizations.Two
        tasks = []
        for qasm, shots in zip(qasms, shot_list):
            config = CompilerConfig(repeats=shots,
                                    results_format=res_format,
                                    optimizations=optimisations)
            tasks.append(QPUTask(program=qasm, config=config, qpu_id=self._device))

        tasks = self._client.schedule_tasks(tasks, qpu_id=self._device)
        task_ids = [task.task_id for task in tasks]

        results = []
        for task_id in task_ids:
            attempts = 0
            while True:
                task_status = self._client.get_task_status(task_id, qpu_id=self._device)
                if task_status == TaskStatus.COMPLETED.value:
                    schedule_result = self._client.get_task_results(task_id, qpu_id=self._device)
                    results.append(schedule_result.result['c'])
                    break
                elif task_status == TaskStatus.FAILED.value:
                    raise RuntimeError("QPU execution failed.")
                elif task_status == TaskStatus.CANCELLED.value:
                    raise RuntimeError("QPU execution canceled.")
                elif task_status == TaskStatus.UNKNOWN.value:
                    raise RuntimeError("QPU returns UNKNOWN status. Quit.")
                elif task_status == TaskStatus.EXPIRED.value:
                    raise RuntimeError("QPU returns EXPIRED status. Too old job.")
                elif task_status == TaskStatus.CREATED.value:
                    raise RuntimeError("QPU returns CREATED status. This should not happen at this point. Quit")
                elif task_status == TaskStatus.SUBMITTED.value:
                    # Submitted but not running. Just goes to the next round
                    pass
                elif task_status == TaskStatus.RUNNING.value:
                    # Running. Let's wait for the completion!
                    pass
                else:
                    raise RuntimeError("QCaaS client returned something wrong. Quit")
                if attempts < 5:
                    attempts += 1
                else:
                    sleep(0.2)
        return results

    @staticmethod
    def batcher(items, batch_length):
        for i in range(0, len(items), batch_length):
            yield items[i:i+batch_length]

    def execute(self, operations, execution_config=None):
        results = []
        for circuit_batch in self.batcher(operations, self.batch_limit):
            qasms = []
            shots_list = []
            for circuit in circuit_batch:
                shots = circuit.shots.total_shots
                openqasm_code = circuit.to_openqasm()
                qasms.append(openqasm_code)
                shots_list.append(shots)
            results.extend(self._batch_execute_qasm_programs(qasms, shots_list))

        postprocessed_results = []
        for circuit, result in zip(operations, results):
            if isinstance(circuit.measurements[0], CountsMP):
                postprocessed_results.append(result)
            elif isinstance(circuit.measurements[0], ExpectationMP):
                postprocessed_result = []
                for measurement in circuit.measurements:
                    obs = measurement.obs
                    exp_val = self._expval_from_counts(obs, result, circuit.wires, circuit.shots.total_shots)
                    postprocessed_result.append(exp_val)
                if len(postprocessed_result) == 1:
                    postprocessed_result = postprocessed_result[0]
                postprocessed_results.append(postprocessed_result)
        return np.array(postprocessed_results)
