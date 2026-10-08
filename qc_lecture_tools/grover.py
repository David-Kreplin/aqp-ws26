import numpy as np
from qiskit import QuantumCircuit

from .statevector import sv_array


def print_grover_states(quantum_circuit, num_data_qubits, cutoff=None):
    """
    Gibt alle Basiszustände des Zustandsvektors eines Quantenschaltkreises aus, deren Amplituden über einem vorgegebenen Schwellenwert liegen.

    Parameter:
        quantum_circuit (QuantumCircuit): Der Quantenschaltkreis, dessen Zustandsvektor analysiert wird.
        num_data_qubits (int): Die Anzahl der Datenqubits ohne Hilfsqubits.
        cutoff (float, optional): Der minimale Amplitudenbetrag, ab dem ein Zustand ausgegeben wird.
            Ohne Angabe wird 1e-10 verwendet.

    Rückgabe:
        None
    """
    num_qubits = quantum_circuit.num_qubits
    statevector = sv_array(quantum_circuit)
    if cutoff is None:
        print("Gefundene Basiszustände mit Amplituden ungleich Null:")
        cutoff = 1e-10
    else:
        print(f"Gefundene Basiszustände mit Amplituden größer als {cutoff}:")
    for i, amplitude in enumerate(statevector):
        if np.abs(amplitude) > cutoff:
            bitstr = format(i, f"0{num_qubits}b")
            if num_qubits != num_data_qubits:
                print(
                    f"{bitstr[:num_data_qubits]} {bitstr[num_data_qubits:]}: {np.real(amplitude):5.2f}  Wahrscheinlichkeit: {np.square(np.real(amplitude)):5.2f}"
                )
            else:
                print(
                    f"{bitstr}: {np.real(amplitude):5.2f}  Wahrscheinlichkeit: {np.square(np.real(amplitude)):5.2f}"
                )


def initial_state(num_data_qubits, num_ancilla_qubits):
    """
    Erzeugt den Anfangszustand für den Grover-Algorithmus, indem Hadamard-Gatter
    auf alle Datenqubits angewendet werden, um eine gleichmäßige Superposition zu erzeugen.

    Parameter:
        num_data_qubits (int): Anzahl der Datenqubits, die in Superposition gebracht werden.
        num_ancilla_qubits (int): Anzahl der Hilfsqubits, die dem Schaltkreis hinzugefügt werden.

    Rückgabe:
        QuantumCircuit: Ein Quantenschaltkreis, der den initialisierten Zustand darstellt.
    """
    list_of_qubits = list(range(num_data_qubits))
    qc_initial_state = QuantumCircuit(num_data_qubits + num_ancilla_qubits)
    qc_initial_state.h(list_of_qubits)
    return qc_initial_state


def amplitude_amplification(num_data_qubits, num_ancilla_qubits):
    """
    Erstellt den Schaltkreis zur Amplitudenverstärkung für den Grover-Algorithmus.
    Dieser Schaltkreis wendet eine Folge von Hadamard-, X- und mehrfach kontrollierten X-Gattern an,
    um die Wahrscheinlichkeit markierter Zustände zu verstärken.

    Parameter:
        num_data_qubits (int): Anzahl der Qubits, die den Suchraum darstellen.
        num_ancilla_qubits (int): Anzahl der für die Berechnung verwendeten Hilfsqubits.

    Rückgabe:
        QuantumCircuit: Der Schaltkreis zur Amplitudenverstärkung.
    """
    qc_amplification = QuantumCircuit(num_data_qubits + num_ancilla_qubits)
    list_of_qubits = list(range(num_data_qubits))
    qc_amplification.h(list_of_qubits)
    qc_amplification.x(list_of_qubits)
    qc_amplification.h(num_data_qubits - 1)
    qc_amplification.mcx(list_of_qubits[:-1], num_data_qubits - 1)
    qc_amplification.h(num_data_qubits - 1)
    qc_amplification.x(list_of_qubits)
    qc_amplification.h(list_of_qubits)

    qc_amplification.rz(2 * np.pi, 0)

    return qc_amplification


def oracle_sudoku():
    """
    Erstellt den Orakelschaltkreis für ein vereinfachtes 2x2-Sudoku-Problem.
    Das Orakel bildet die Sudoku-Regeln mithilfe mehrfach kontrollierter Toffoli-Gatter ab
    und kehrt die Phase des Lösungszustands um.

    Qubit-Anordnung:
        - Qubits 0–3: Variablen der Sudoku-Zellen
        - Qubits 4–10: Hilfsqubits für logische Zwischenprüfungen
        - Qubit 11: Ausgabequbit des Orakels

    Geprüfte Bedingungen:
        - q0q1 == 01
        - q2q3 == 01
        - q0q1 == 11
        - q2q3 == 11
        - q0 == q2
        - q1 == q3
        - Alle Bedingungen müssen erfüllt sein, um die Orakelausgabe umzukehren

    Parameter:
        None

    Rückgabe:
        QuantumCircuit: Der erstellte Orakelschaltkreis für das Sudoku-Problem.
    """
    qc_compute = QuantumCircuit(12)

    # Hilfsqubit 1 (Qubit 4) überprüft q0q1 == 01
    qc_compute.x(0)
    qc_compute.ccx(0, 1, 4)
    qc_compute.x(0)

    # Hilfsqubit 2 (Qubit 5) überprüft Qubit q2q3 == 01
    qc_compute.x(2)
    qc_compute.ccx(2, 3, 5)
    qc_compute.x(2)

    # Hilfsqubit 3 (Qubit 6) überprüft Qubit q0q1 == 11
    qc_compute.ccx(0, 1, 6)

    # Hilfsqubit 4 (Qubit 7) überprüft Qubit q2q3 == 11
    qc_compute.ccx(2, 3, 7)

    # Hilfsqubit 5 (Qubit 8) überprüft q0 == q2
    qc_compute.cx(0, 8)
    qc_compute.cx(2, 8)
    qc_compute.x(8)

    # Hilfsqubit 6 (Qubit 9) überprüft q1 == q3
    qc_compute.cx(1, 9)
    qc_compute.cx(3, 9)
    qc_compute.x(9)

    # Prüfen, ob beide Gleichheitsprüfungen (Hilfsqubits 5 und 6) erfüllt sind
    qc_compute.ccx(8, 9, 10)

    # Alle Abfragen invertieren -> Richtige Lösung wenn alle 1
    qc_compute.x([4, 5, 6, 7, 10])

    # mehrfach kontrolliertes CNOT mit dem Orakelqubit als Ziel
    qc_compute.mcx([4, 5, 6, 7, 10], 11)

    qc_oracle = QuantumCircuit(12)
    qc_oracle.compose(qc_compute, inplace=True)
    qc_oracle.z(11)
    qc_oracle.compose(qc_compute.inverse(), inplace=True)

    return qc_oracle


def grover_ones(num_data_qubits: int, num_steps: int) -> QuantumCircuit:
    """Implementiert den Grover-Algorithmus zum Finden des Zustands |1...11>.

    Parameter:
        num_data_qubits (int): Anzahl der Datenqubits.
        num_steps (int): Anzahl der Grover-Schritte.

    Rückgabe:
        Quantenschaltkreis des Orakels.
    """

    # Einen Quantenschaltkreis mit der angegebenen Anzahl von Datenqubits erstellen
    quantum_circuit = QuantumCircuit(num_data_qubits)

    # Die anfängliche gleichmäßige Superposition vorbereiten (üblicherweise Zustand |s⟩)
    quantum_circuit.compose(initial_state(num_data_qubits, 0), inplace=True)

    # Die Kontrollqubits festlegen (alle außer dem letzten Qubit, das als Ziel dient)
    control_qubits = list(range(num_data_qubits - 1))

    # Die Grover-Iteration wiederholen (Orakel + Amplitudenverstärkung)
    for i in range(num_steps):

        # --- Orakelschritt ---
        # Das Orakel markiert den Lösungszustand durch Umkehrung seiner Phase.
        # Hier durch ein kontrolliertes X-Gatter (Inversion) auf mehreren Qubits dargestellt.
        quantum_circuit.h(num_data_qubits - 1)
        quantum_circuit.mcx(control_qubits, num_data_qubits - 1)
        quantum_circuit.h(num_data_qubits - 1)

        # --- Diffusionsschritt (Amplitudenverstärkung) ---
        # Spiegelt den Zustandsvektor an der mittleren Amplitude.
        quantum_circuit.compose(
            amplitude_amplification(num_data_qubits, 0), inplace=True
        )

    # Den erstellten Grover-Schaltkreis zurückgeben
    return quantum_circuit


def grover_ones_ancilla(num_data_qubits, num_steps):
    """Implementiert den Grover-Algorithmus zum Finden des Zustands |1...11> mithilfe eines Hilfsqubits.

    Parameter:
        num_data_qubits (int): Anzahl der Datenqubits.
        num_steps (int): Anzahl der Grover-Schritte.

    Rückgabe:
        Quantenschaltkreis des Orakels.
    """

    # Einen Quantenschaltkreis mit einem zusätzlichen Hilfsqubit erstellen
    quantum_circuit = QuantumCircuit(num_data_qubits + 1)

    # Den Anfangszustand vorbereiten, z. B. eine gleichmäßige Superposition aller Datenqubits
    # und das auf |1⟩ initialisierte Hilfsqubit (das kontrollierte Orakel benötigt ein Hilfsqubit)
    quantum_circuit.compose(initial_state(num_data_qubits, 1), inplace=True)

    # Die Kontrollqubits festlegen (alle Datenqubits)
    control_qubits = list(range(num_data_qubits))

    # Die angegebene Anzahl von Grover-Iterationen ausführen
    for i in range(num_steps):

        # --- Orakelschritt ---
        # Die Phase des Zustands |11...1> mithilfe des Hilfsqubits umkehren.
        # Die Folge mcx -> z -> mcx implementiert eine bedingte Phasenumkehrung.
        quantum_circuit.mcx(control_qubits, num_data_qubits)  # Kontrolliertes X auf dem Hilfsqubit
        quantum_circuit.z(num_data_qubits)  # Phasenumkehrung auf dem Hilfsqubit
        quantum_circuit.mcx(control_qubits, num_data_qubits)  # Das kontrollierte X rückgängig machen

        # --- Diffusionsschritt (Amplitudenverstärkung) ---
        # Spiegelt den Zustand an der mittleren Amplitude, um den markierten Zustand zu verstärken.
        quantum_circuit.compose(
            amplitude_amplification(num_data_qubits, 1), inplace=True
        )

    # Den erstellten Grover-Schaltkreis mit Hilfsqubit zurückgeben
    return quantum_circuit
