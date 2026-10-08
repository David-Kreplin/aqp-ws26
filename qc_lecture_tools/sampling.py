import numpy as np
from IPython.display import display, Math

from qiskit import QuantumCircuit
from qiskit_ibm_runtime import SamplerV2
from qiskit_aer import Aer
from qiskit_ibm_runtime.fake_provider import FakeTorino
from qiskit.primitives import BackendSamplerV2
from qiskit.compiler import transpile

from qiskit.quantum_info import Statevector

def sample_from_circuit_hardware(
    quantum_circuit: QuantumCircuit, num_shots: int
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
    return sample_from_circuit_backend(quantum_circuit, num_shots, backend)


def sample_from_circuit_backend(
    quantum_circuit: QuantumCircuit, num_shots: int, backend
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
    statevector_sampler = SamplerV2(mode=backend, options={"default_shots": num_shots})
    
    # Apply the course bit order before mapping logical qubits to the backend.
    # Reversing a transpiled circuit would invalidate its physical layout.
    quantum_circuit_trans = transpile(
        quantum_circuit.reverse_bits(),
        backend=backend,
    )

    # Quantenschaltkreis mit Messungen ausführen
    result = statevector_sampler.run([quantum_circuit_trans]).result()

    # Messergebnisse ausgeben
    if hasattr(result[0].data, "c"):
        shots_dict = result[0].data.c.get_counts()
    elif hasattr(result[0].data, "meas"):
        shots_dict = result[0].data.meas.get_counts()
    else:
        raise ValueError("Es werden nur die Standardregisternamen unterstützt.")
    return shots_dict


def sample_from_circuit(quantum_circuit: QuantumCircuit, num_shots: int) -> dict:
    """Führt einen Quantenschaltkreis mit der angegebenen Anzahl von Messungen
    (Shots) aus und gibt die Messergebnisse als Dictionary zurück.
    
    Argumente:
        quantum_circuit (QuantumCircuit): Der auszuführende Quantenschaltkreis.
        num_shots (int): Die Anzahl der durchzuführenden Messungen (Shots).
    
    Rückgabe:
        dict: Ein Dictionary mit den Messergebnissen.
    """

    # Sampler mit 100 Messungen (Shots) initialisieren
    backend = Aer.get_backend("aer_simulator")
    statevector_sampler = BackendSamplerV2(
        backend=backend, options={"default_shots": num_shots}
    )

    # Quantenschaltkreis mit Messungen ausführen
    result = statevector_sampler.run([quantum_circuit.reverse_bits()]).result()

    # Messergebnisse ausgeben
    if hasattr(result[0].data, "c"):
        shots_dict = result[0].data.c.get_counts()
    elif hasattr(result[0].data, "meas"):
        shots_dict = result[0].data.meas.get_counts()
    else:
        raise ValueError("Es werden nur die Standardregisternamen unterstützt.")
    return shots_dict

def measure_quantum_circuit(quantum_circuit: QuantumCircuit, latex: bool = True):
    """Misst einen Quantenschaltkreis einmal und zeigt den resultierenden Zustand im LaTeX-Format an.
    
    Argumente:
        quantum_circuit (QuantumCircuit): Der zu messende Quantenschaltkreis.
        latex (bool): Gibt an, ob das Ergebnis im LaTeX-Format angezeigt wird;
            der Standardwert ist True. Andernfalls wird es als Bitstring zurückgegeben.
    """
    result_dict = sample_from_circuit(quantum_circuit.measure_all(inplace=False), num_shots=1)
    bitstring = list(result_dict.keys())[0]
    
    if latex:
        latex_str = "\\ket{" + bitstring + "}"
        return display(Math(f"{latex_str}"))
    else:
        return bitstring


def measure_to_probability(measurements: dict) -> dict:
    """Wandelt die Messhäufigkeiten eines Dictionarys in Wahrscheinlichkeiten um.
    
    Argumente:
        measurements (dict): Dictionary mit Zuständen als Schlüsseln und
            Messhäufigkeiten als Werten.
    
    Rückgabe:
        Ein Dictionary mit den gemessenen Wahrscheinlichkeiten.
    """
    if not isinstance(measurements, dict):
        raise ValueError("Die übergebenen Messungen müssen ein Dictionary sein!")
    probs = {}
    total_counts = sum(measurements.values())
    for state in measurements.keys():
        probs[state] = measurements[state] / total_counts
    return probs


def sort_dict(shots_dict: dict):
    """Sortiert ein Dictionary nach seinen Schlüsseln.
    
    Argumente:
        shots_dict (dict): Das zu sortierende Dictionary.
    
    Rückgabe:
        dict: Das sortierte Dictionary.
    """

    return dict(sorted(shots_dict.items()))


def get_quasi_probs(quantum_circuit: QuantumCircuit, num_shots: int) -> np.ndarray:
    """Führt einen Quantenschaltkreis mit der angegebenen Anzahl von Messungen
    (Shots) aus und gibt die Quasiwahrscheinlichkeiten als Array zurück.
    
    Argumente:
        quantum_circuit (QuantumCircuit): Der auszuführende Quantenschaltkreis.
        num_shots (int): Die Anzahl der durchzuführenden Messungen (Shots).
    
    Rückgabe:
        np.ndarray: Ein Array mit den Quasiwahrscheinlichkeiten.
    """

    shots_dict = sample_from_circuit(quantum_circuit, num_shots)
    probs_array = convert_to_probs(shots_dict, quantum_circuit.num_qubits)
    return probs_array

def get_probs(quantum_circuit: QuantumCircuit) -> dict:
    """Berechnet die Messwahrscheinlichkeiten der Basiszustände für den gegebenen Quantenschaltkreis.
    
    Argumente:
        quantum_circuit (QuantumCircuit): Der auszuführende Quantenschaltkreis.
    
    Rückgabe:
        dict: Ein Dictionary mit der Wahrscheinlichkeit für jeden Basiszustand.
    """

    statevector = Statevector.from_instruction(quantum_circuit.reverse_bits())
    probs = np.square(np.abs(statevector))
    probs_dict = {}
    for i, p in enumerate(probs):
        bitstring = f"{i:0{quantum_circuit.num_qubits}b}"
        probs_dict[bitstring] = float(p)

    return sort_dict(probs_dict)

def convert_to_probs(shots_dict: dict, num_qubits: int) -> np.ndarray:
    """Wandelt ein Dictionary mit Messergebnissen in ein Array mit Wahrscheinlichkeiten um.
    
    Argumente:
        shots_dict (dict): Ein Dictionary mit den Messergebnissen.
        num_qubits (int): Die Anzahl der Qubits im Quantenschaltkreis.
    
    Rückgabe:
        np.ndarray: Ein Array mit den Wahrscheinlichkeiten.
    """

    num_states = 2**num_qubits
    probs_array = [0.0] * num_states

    for bitstring, count in shots_dict.items():
        index = int(bitstring, 2)
        probs_array[index] = count

    total_counts = sum(shots_dict.values())
    if total_counts > 0:
        probs_array = [count / total_counts for count in probs_array]

    return np.array(probs_array)


def measurements_to_probabilities(measurements: dict) -> dict:
    """Wandelt Messhäufigkeiten in Wahrscheinlichkeiten um; beide werden als Dictionary gespeichert.
    
    Argumente:
        measurements (dict): Ein Dictionary mit Messergebnissen als Schlüsseln
            und ihren Häufigkeiten als Werten.
    
    Rückgabe:
        dict: Ein Dictionary mit Messergebnissen als Schlüsseln und ihren
            Wahrscheinlichkeiten als Werten.
    """
    probabilities = {}

    # Gesamtzahl der Messungen berechnen
    total_shots = 0
    for m in measurements.keys():
        total_shots += measurements[m]

    # Wahrscheinlichkeit für jeden gefundenen Basiszustand berechnen
    for m in measurements.keys():
        probabilities[m] = measurements[m] / total_shots

    return probabilities
