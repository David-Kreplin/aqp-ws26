from typing import Union
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp
from qiskit_ibm_runtime import EstimatorV2
from qiskit_aer import Aer
from qiskit_ibm_runtime.fake_provider import FakeTorino
from qiskit.primitives import BackendEstimatorV2, StatevectorEstimator
from qiskit.compiler import transpile

from .statevector import sv_dict
from .sampling import (
    sample_from_circuit_backend,
    sample_from_circuit,
    measurements_to_probabilities,
)


def qiskit_expectation_value_hardware(
    quantum_circuit: QuantumCircuit,
    observable: SparsePauliOp,
    num_shots: Union[None, int] = None,
) -> dict:
    """Führt einen Quantenschaltkreis mit der angegebenen Anzahl von Messungen
    (Shots) aus und gibt die Messergebnisse als Dictionary zurück.
    
    Argumente:
        quantum_circuit (QuantumCircuit): Der auszuführende Quantenschaltkreis.
        num_shots (int): Die Anzahl der durchzuführenden Messungen (Shots).
    
    Rückgabe:
        dict: Ein Dictionary mit den Messergebnissen.
    """

    # Sampler mit 100 Messungen (Shots) initialisieren
    backend = FakeTorino()
    return qiskit_expectation_value_backend(
        quantum_circuit, observable, backend, num_shots
    )


def qiskit_expectation_value_backend(
    quantum_circuit: QuantumCircuit,
    observable: SparsePauliOp,
    backend,
    num_shots: Union[None, int] = None,
) -> dict:
    """Führt einen Quantenschaltkreis mit der angegebenen Anzahl von Messungen
    (Shots) aus und gibt die Messergebnisse als Dictionary zurück.
    
    Argumente:
        quantum_circuit (QuantumCircuit): Der auszuführende Quantenschaltkreis.
        num_shots (int): Die Anzahl der durchzuführenden Messungen (Shots).
    
    Rückgabe:
        dict: Ein Dictionary mit den Messergebnissen.
    """

    # Sampler mit 100 Messungen (Shots) initialisieren
    estimator = EstimatorV2(
        mode=backend, options={"default_precision": 1 / np.sqrt(num_shots)}
    )

    # Quantenschaltkreis mit Messungen ausführen
    result = estimator.run([(quantum_circuit, observable)]).result()

    return float(result[0].data.evs)


def qiskit_expectation_value(
    quantum_circuit: QuantumCircuit,
    observable: Union[SparsePauliOp, str],
    num_shots: Union[None, int] = None,
) -> dict:
    """Führt einen Quantenschaltkreis mit der angegebenen Anzahl von Messungen
    (Shots) aus und gibt die Messergebnisse als Dictionary zurück.
    
    Argumente:
        quantum_circuit (QuantumCircuit): Der auszuführende Quantenschaltkreis.
        num_shots (int): Die Anzahl der durchzuführenden Messungen (Shots).
    
    Rückgabe:
        dict: Ein Dictionary mit den Messergebnissen.
    """

    if isinstance(observable, str):
        observable = SparsePauliOp(observable[::-1])

    if num_shots == 0 or num_shots is None:
        # Sampler mit 100 Messungen (Shots) initialisieren
        estimator = StatevectorEstimator()
    else:
        # Sampler mit 100 Messungen (Shots) initialisieren
        backend = Aer.get_backend("aer_simulator")
        estimator = BackendEstimatorV2(
            backend=backend, options={"default_precision": 1 / np.sqrt(num_shots)}
        )

    # Quantenschaltkreis mit Messungen ausführen
    result = estimator.run([(quantum_circuit, observable)]).result()

    return result[0].data.evs


def Z_expectation(
    pauli_string: str,
    quantum_circuit: QuantumCircuit,
    shots: Union[None, int] = None,
    backend=None,
) -> float:
    """Berechnet den Erwartungswert eines aus I und Z zusammengesetzten Pauli-Operators
    auf mehreren Qubits anhand eines Quantenschaltkreises.
    
    Argumente:
        pauli_string (str): Eine Zeichenfolge aus "I" und "Z", die den Pauli-Operator darstellt.
        quantum_circuit (QuantumCircuit): Der auszuwertende Quantenschaltkreis.
        shots (int or None): Die Anzahl der Messungen. Bei None wird eine
            Zustandsvektorsimulation verwendet.
        backend: Das für die Ausführung verwendete Backend, wenn shots angegeben ist.
    
    Rückgabe:
        float: Der Erwartungswert des gegebenen Pauli-Z-Operators.
    """

    if shots is None:
        # Keine Messanzahl angegeben: exakte Wahrscheinlichkeiten per Zustandsvektorsimulation berechnen
        probabilities = sv_dict(quantum_circuit)
    else:
        # Messanzahl angegeben: Messungen durchführen
        measured_quantum_circuit = quantum_circuit.copy()
        measured_quantum_circuit.measure_all()

        if backend is None:
            # Kein Backend angegeben: lokal mit dem exakten Simulator messen
            measurements = sample_from_circuit(measured_quantum_circuit, shots)
        else:
            # Backend angegeben: mit diesem Backend messen (simulierte oder echte Hardware)
            measurements = sample_from_circuit_backend(
                measured_quantum_circuit, shots, backend
            )

        # Messhäufigkeiten in Wahrscheinlichkeiten umwandeln
        probabilities = measurements_to_probabilities(measurements)

    # Erwartungswert berechnen
    expectation_value = 0
    for m in probabilities.keys():
        fac = 1.0
        for i, s in enumerate(pauli_string):
            if s == "Z" and m[i] == "1":
                fac = fac * (-1.0)

        expectation_value += probabilities[m] * fac

    return expectation_value


def single_expectation_value(
    pauli_string: str,
    quantum_circuit: QuantumCircuit,
    shots: Union[None, int] = None,
    backend=None,
) -> float:
    """Berechnet den Erwartungswert eines einzelnen aus X, Y, Z und I zusammengesetzten
    Pauli-Operators anhand eines Quantenschaltkreises.
    
    Argumente:
        pauli_string (str): Eine Zeichenfolge aus "X", "Y", "Z" und "I", die den Pauli-Operator darstellt.
        quantum_circuit (QuantumCircuit): Der auszuwertende Quantenschaltkreis.
        shots (int or None): Die Anzahl der Messungen. Bei None wird eine
            Zustandsvektorsimulation verwendet.
        backend: Das für die Ausführung verwendete Backend, wenn shots angegeben ist.
    
    Rückgabe:
        float: Der Erwartungswert des gegebenen Pauli-Operators.
    """

    modified_quantum_circuit = quantum_circuit.copy()

    Z_string = ""
    for i, s in enumerate(pauli_string):
        if s == "X":
            modified_quantum_circuit.h(i)
            Z_string += "Z"
        elif s == "Y":
            modified_quantum_circuit.sdg(i)
            modified_quantum_circuit.h(i)
            Z_string += "Z"
        elif s == "Z":
            Z_string += "Z"
        elif s == "I":
            Z_string += "I"
        else:
            raise ValueError("Unbekanntes Pauli-Gatter:", s)

    return Z_expectation(Z_string, modified_quantum_circuit, shots, backend)


def expectation_value(
    observable: SparsePauliOp,
    quantum_circuit: QuantumCircuit,
    shots: Union[None, int] = None,
    backend=None,
) -> float:
    """Berechnet den Erwartungswert einer gegebenen SparsePauliOp-Observablen
    anhand eines Quantenschaltkreises.
    
    Argumente:
        observable (SparsePauliOp): Die auszuwertende Observable.
        quantum_circuit (QuantumCircuit): Der auszuwertende Quantenschaltkreis.
        shots (int or None): Die Anzahl der Messungen. Bei None wird eine
            Zustandsvektorsimulation verwendet.
        backend: Das für die Ausführung verwendete Backend, wenn shots angegeben ist.
    
    Rückgabe:
        float: Der Erwartungswert der gegebenen Observablen.
    """

    expectation_value = 0.0

    for o in observable:
        expectation_value += (
            single_expectation_value(str(o.paulis[0]), quantum_circuit, shots, backend)
            * o.coeffs[0]
        )

    return float(np.real_if_close(expectation_value))


def standard_deviation(
    observable: SparsePauliOp, quantum_circuit: QuantumCircuit, shots: int
):
    """Berechnet die Standardabweichung einer gegebenen SparsePauliOp-Observablen
    anhand eines Quantenschaltkreises.
    
    Argumente:
        observable (SparsePauliOp): Die auszuwertende Observable.
        quantum_circuit (QuantumCircuit): Der auszuwertende Quantenschaltkreis.
        shots (int): Die Anzahl der Messungen für die Berechnung der Standardabweichung.
    
    Rückgabe:
        float: Die Standardabweichung der gegebenen Observablen.
    """

    observable_squared = observable.power(2).simplify()
    exp_values_squared = expectation_value(
        observable_squared, quantum_circuit, shots=None
    )
    exp_values = expectation_value(observable, quantum_circuit, shots=None)

    std = np.sqrt((exp_values_squared - np.square(exp_values)) / shots)

    return std


def evaluate_expectation_value(
    circuit: QuantumCircuit,
    observable: SparsePauliOp,
    parameters: np.array = None,
    shots: Union[None, int] = None,
    backend=None,
) -> float:
    """Berechnet den Erwartungswert der gegebenen Observablen bezüglich des Zustands,
    der vom Schaltkreis mit den angegebenen Parametern präpariert wird.
    
    Argumente:
        circuit: Der parametrisierte Quantenschaltkreis.
        observable: Die zu messende Observable.
        parameters: Die an den Schaltkreis zu bindenden Parameter.
        shots: Die Anzahl der Messungen für die Ausführung. Bei None wird ein
            Zustandsvektorsimulator verwendet.
        backend: Das für die Ausführung verwendete Backend. Bei None wird ein
            ideales Backend verwendet.
    
    Rückgabe:
        float: Der Erwartungswert der Observablen.
    """
    if shots is None:
        estimator = StatevectorEstimator()
        circuit_run = circuit
        observable_run = observable
    elif backend is None:
        backend = Aer.get_backend("aer_simulator")
        estimator = EstimatorV2(
            mode=backend, options={"default_precision": 1 / np.sqrt(shots)}
        )
        circuit_run = circuit
        observable_run = observable

    else:

        circuit_run = transpile(circuit, backend=backend)
        observable_run = observable.apply_layout(circuit_run.layout)

        estimator = EstimatorV2(
            mode=backend, options={"default_precision": 1 / np.sqrt(shots)}
        )

    result = estimator.run([(circuit_run, observable_run, parameters)]).result()
    return float(result[0].data.evs)


def gradient_finite_differences(
    quantum_circuit: QuantumCircuit,
    observable: SparsePauliOp,
    parameters: np.ndarray,
    delta_h: float = 0.01,
    shots: Union[int, None] = None,
    backend=None,
) -> np.array:
    """Berechnet den Gradienten der Erwartungswertfunktion mit finiten Differenzen.
    
    Argumente:
        quantum_circuit (QuantumCircuit): Der parametrisierte Quantenschaltkreis.
        observable (SparsePauliOp): Die Observable, deren Erwartungswert berechnet wird.
        parameters (np.ndarray): Die aktuellen Parameter des Quantenschaltkreises.
        delta_h (float): Die kleine Änderung für die Berechnung der finiten Differenzen.
        shots (Union[int, None]): Die Anzahl der Messungen. Bei None wird eine
            Zustandsvektorsimulation verwendet.
        backend: Das für die Ausführung verwendete Backend. Bei None wird ein
            ideales Backend verwendet.
    
    Rückgabe:
        np.array: Der Gradientenvektor des Erwartungswerts bezüglich der Parameter.
    """

    gradient = []

    for p in range(len(parameters)):
        params_plus = parameters.copy()
        params_plus[p] += delta_h
        exp_plus = evaluate_expectation_value(
            quantum_circuit, observable, params_plus, backend=backend, shots=shots
        )

        params_minus = parameters.copy()
        params_minus[p] -= delta_h
        exp_minus = evaluate_expectation_value(
            quantum_circuit, observable, params_minus, backend=backend, shots=shots
        )

        gradient.append((exp_plus - exp_minus) / (2 * delta_h))

    return np.array(gradient)


def gradient_parameter_shift_rule(
    quantum_circuit: QuantumCircuit,
    observable: SparsePauliOp,
    parameters: np.ndarray,
    shots: Union[int, None] = None,
    backend=None,
) -> np.array:
    """Berechnet den Gradienten der Erwartungswertfunktion mit der Parameter-Shift-Regel.
    
    Argumente:
        quantum_circuit (QuantumCircuit): Der parametrisierte Quantenschaltkreis.
        observable (SparsePauliOp): Die Observable, deren Erwartungswert berechnet wird.
        parameters (np.ndarray): Die aktuellen Parameter des Quantenschaltkreises.
        shots (Union[int, None]): Die Anzahl der Messungen. Bei None wird eine
            Zustandsvektorsimulation verwendet.
        backend: Das für die Ausführung verwendete Backend. Bei None wird ein
            ideales Backend verwendet.
    
    Rückgabe:
        np.array: Der Gradientenvektor des Erwartungswerts bezüglich der Parameter.
    """

    gradient = []

    for p in range(len(parameters)):
        shift = np.pi / 2

        params_plus = parameters.copy()
        params_plus[p] += shift
        exp_plus = evaluate_expectation_value(
            quantum_circuit, observable, params_plus, backend=backend, shots=shots
        )

        params_minus = parameters.copy()
        params_minus[p] -= shift
        exp_minus = evaluate_expectation_value(
            quantum_circuit, observable, params_minus, backend=backend, shots=shots
        )

        gradient.append((exp_plus - exp_minus) / 2)

    return np.array(gradient)
