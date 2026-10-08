"""Bereitgestellte Hilfsfunktionen für die Übung zum Shor-Algorithmus."""

import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit import QuantumCircuit
from .statevector import sv_dict


def print_basis_state_mapping(
    circuit: QuantumCircuit,
    input_states: list[int],
) -> list[tuple[int, int]]:
    """Gib die Basiszustandsabbildung eines zu prüfenden Schaltkreises aus.

    Derselbe Schaltkreis wird unabhängig auf jeden Eingabezustand angewendet.
    """
    if circuit.num_qubits != 4:
        raise ValueError(
            "Die Übungshilfsfunktion erwartet genau 4 Qubits für ganzzahlige Zustände."
        )

    width = circuit.num_qubits
    mappings = []

    for input_integer in input_states:
        # Bereite den Eingabebasiszustand |input_integer> vor
        input_bitstring = f"{input_integer:0{width}b}"
        test_circuit = QuantumCircuit(width)

        for qubit, bit in enumerate(reversed(input_bitstring)):
            if bit == "1":
                test_circuit.x(qubit)

        # Wende den zu prüfenden Schaltkreis an
        test_circuit.compose(circuit, inplace=True)

        # Lies den resultierenden Basiszustand mit der Kurshilfsfunktion aus
        probabilities = sv_dict(test_circuit.reverse_bits())

        if len(probabilities) != 1:
            raise ValueError(
                "Der Schaltkreis bildet den Eingabebasiszustand nicht "
                "deterministisch auf einen einzelnen Ausgabebasiszustand ab."
            )

        output_bitstring = next(iter(probabilities))
        output_integer = int(output_bitstring, 2)

        mappings.append((input_integer, output_integer))

        print(f"|{input_bitstring}> -> |{output_bitstring}>")

    return mappings


def _inverse_qft(num_qubits: int):
    """Gib das inverse QFT-Gatter der bereitgestellten QPE-Blackbox zurück."""
    circuit = QuantumCircuit(num_qubits, name="QFT†")

    for qubit in range(num_qubits // 2):
        circuit.swap(qubit, num_qubits - qubit - 1)

    for target in range(num_qubits):
        for control in range(target):
            angle = -np.pi / (2 ** (target - control))
            circuit.cp(angle, control, target)
        circuit.h(target)

    return circuit.to_gate(label="QFT†")


def create_qpe_circuit(
    controlled_modular_function,
    num_ancilla_qubits: int,
    num_target_qubits: int = 4,
) -> QuantumCircuit:
    """Erstelle QPE aus einer von Studierenden gelieferten kontrollierten modularen Potenzfunktion.

    controlled_modular_function(power) muss ein Gatter, eine Anweisung oder
    einen Schaltkreis zurückgeben, der auf ein Kontrollqubit und anschließend
    num_target_qubits Zielqubits wirkt. Die Funktion wird mit den Potenzen
    1, 2, 4, ... aufgerufen.
    """
    if num_ancilla_qubits < 1:
        raise ValueError("num_ancilla_qubits muss mindestens 1 sein")

    counting = QuantumRegister(num_ancilla_qubits, "ancilla")
    target = QuantumRegister(num_target_qubits, "target")
    measured_phase = ClassicalRegister(num_ancilla_qubits, "c")
    circuit = QuantumCircuit(counting, target, measured_phase)

    circuit.h(counting)
    circuit.x(target[0])

    expected_block_qubits = 1 + num_target_qubits
    for ancilla_index in range(num_ancilla_qubits):
        power = 2**ancilla_index
        controlled_block = controlled_modular_function(power)

        if controlled_block.num_qubits != expected_block_qubits:
            raise ValueError(
                "Die kontrollierte modulare Funktion muss eine Operation auf "
                f"{expected_block_qubits} Qubits zurückgeben: ein Kontrollqubit, gefolgt von "
                f"{num_target_qubits} Zielqubits."
            )

        if isinstance(controlled_block, QuantumCircuit):
            controlled_block = controlled_block.to_gate(
                label=controlled_block.name
            )

        circuit.append(
            controlled_block,
            [counting[ancilla_index], *target],
        )

    circuit.append(_inverse_qft(num_ancilla_qubits), counting)
    for i in range(num_ancilla_qubits):
        circuit.measure(num_ancilla_qubits-1-i, i)
    return circuit
