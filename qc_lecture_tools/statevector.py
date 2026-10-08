import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
import ipywidgets
from ipywidgets import interact, interactive
from IPython.display import display, Math
import sympy
from sympy import sqrt, sin, cos, pi, E, N


def format_complex(v: float):
    """
    Gibt einen Wert als LaTeX-Ausdruck zurück.

    Parameter:
        v (float): Zahl, die in LaTeX umgewandelt wird.

    Rückgabe:
        LaTeX-Ausdruck
    """

    # Mit sympy vereinfachen und Wurzeln sowie rationale Ausdrücke erkennen

    constants = [sqrt(2), sqrt(3), sqrt(5), pi, E]
    trig_constants = [
        sin(pi / 6),
        cos(pi / 6),  # 1/2, sqrt(3)/2
        sin(pi / 4),
        cos(pi / 4),  # sqrt(2)/2
        sin(pi / 3),
        cos(pi / 3),  # sqrt(3)/2, 1/2
    ]

    constants += trig_constants
    expr = N(v, 15, chop=1e-10)
    expr = sympy.nsimplify(expr, constants=constants, tolerance=1e-15)

    # Wurzelausdrücke nach Möglichkeit weiter vereinfachen
    expr = sympy.simplify(expr)

    # Sehr große Nenner bei rationalen Zahlen vermeiden
    if any(
        isinstance(r, sympy.Rational) and r.q > 50 for r in expr.atoms(sympy.Rational)
    ):
        expr = expr.evalf()  # Als Gleitkommazahl darstellen

    if isinstance(expr, sympy.core.numbers.Float):
        expr = round(expr, 15)

    # Wenn expr eine sympy-Zahl ist, als LaTeX formatieren
    if isinstance(expr, sympy.Basic):
        latex = sympy.latex(expr)
    else:
        # Andernfalls als Gleitkommazahl formatieren
        latex = f"{v.real:.2f}"
        if not np.isclose(v.imag, 0):
            sign = "+" if v.imag > 0 else ""
            latex += f"{sign}{v.imag:.2f}i"
    return latex


def matrix_to_latex(matrix, label=None):
    """Wandelt eine Matrix in LaTeX um und stellt typische Zahlen einschließlich Wurzeln als analytische Ausdrücke dar."""

    latex_str = "\\begin{pmatrix}"
    rows = []
    for row in matrix:
        row_str = " & ".join([format_complex(v) for v in row])
        rows.append(row_str)
    latex_str += " \\\\ ".join(rows)
    latex_str += "\\end{pmatrix}"
    if label is None:
        display(Math(f"{latex_str}"))
    else:
        display(Math(f"\\text{{ {label} }}{latex_str}"))


def sv_compute(quantum_circuit: QuantumCircuit) -> Statevector:
    """Berechnet den Zustandsvektor eines Quantenschaltkreises.

    Parameter:
        quantum_circuit (QuantumCircuit): Der zu simulierende Quantenschaltkreis.

    Rückgabe:
        Statevector: Der Zustandsvektor des Quantenschaltkreises.
    """

    statevector = Statevector.from_instruction(quantum_circuit.reverse_bits())
    return statevector


def sv_array(quantum_circuit: QuantumCircuit) -> np.ndarray:
    """Berechnet den Zustandsvektor eines Quantenschaltkreises und gibt ihn als Liste zurück.

    Parameter:
        quantum_circuit (QuantumCircuit): Der zu simulierende Quantenschaltkreis.
    Rückgabe:
        np.ndarray: Der Zustandsvektor des Quantenschaltkreises als Liste.
    """
    statevector = sv_compute(quantum_circuit)
    return statevector.data


def sv_vector(quantum_circuit: QuantumCircuit, label: str = None):
    """Gibt den Zustandsvektor als LaTeX-Vektor aus.

    Parameter:
        quantum_circuit (QuantumCircuit): Der zu simulierende Quantenschaltkreis.
        name (str): Optionaler Name, der der Ausgabe hinzugefügt wird.
    """
    statevector = sv_compute(quantum_circuit)
    latex_str = "\\begin{pmatrix}"
    rows = []
    for value in statevector:
        latex_str += format_complex(value)
        latex_str += "\\\\"
    latex_str += "\\end{pmatrix}"
    if label is None:
        return Math(latex_str)
    else:
        return Math(f"\\text{{ {label} }}{latex_str}")


def sv_dict(quantum_circuit: QuantumCircuit) -> dict:
    array = np.square(np.abs(sv_array(quantum_circuit)))

    prob_dict = {}
    num_qubits = quantum_circuit.num_qubits

    for i, v in enumerate(array):
        if np.abs(v) > 1e-10:
            bitstr = format(i, f"0{num_qubits}b")
            prob_dict[bitstr] = float(v)

    return prob_dict


def sv_state(quantum_circuit: QuantumCircuit, label: str = None):
    """Gibt den Zustandsvektor eines Quantenschaltkreises aus.

    Parameter:
        quantum_circuit (QuantumCircuit): Der zu simulierende Quantenschaltkreis.
        name (str): Optionaler Name, der der Ausgabe hinzugefügt wird.
    """
    statevector = sv_compute(quantum_circuit)
    if label is None:
        return Math(statevector.draw("latex_source"))
    else:
        return Math(f"\\text{{ {label} }}{statevector.draw('latex_source')}")


def sv_probs(quantum_circuit: QuantumCircuit, label: str = None):
    """Berechnet die Messwahrscheinlichkeiten der Basiszustände des gegebenen Quantenschaltkreises und gibt sie aus."""
    vector = sv_compute(quantum_circuit)
    probs = np.square(np.abs(vector))

    if label is not None:
        latex_str = f"\\text{{ {label} }}" + "\\begin{array}{rcl}"
    else:
        latex_str = r"\begin{array}{rcl}"

    for i, p in enumerate(probs):
        latex_str += f"p_{{{i:0{quantum_circuit.num_qubits}b}}}" + r" & = & "
        latex_str += format_complex(p) + " \\\\[1mm]"
    latex_str += "\\end{array}"
    return Math(latex_str)


def sv_latex(quantum_circuit: QuantumCircuit):
    """Gibt den Zustandsvektor eines Quantenschaltkreises aus.

    Parameter:
        quantum_circuit (QuantumCircuit): Der zu simulierende Quantenschaltkreis.
    """
    return sv_state(quantum_circuit)


def sv_blochsphere(quantum_circuit: QuantumCircuit):
    """Zeichnet den Zustandsvektor eines Quantenschaltkreises.

    Parameter:
        quantum_circuit (QuantumCircuit): Der zu simulierende Quantenschaltkreis.
    """

    if quantum_circuit.num_qubits != 1:
        raise ValueError(
            "Die Darstellung des Zustandsvektors in der Bloch-Kugel wird nur für Schaltkreise mit einem einzelnen Qubit unterstützt."
        )

    statevector = sv_compute(quantum_circuit)
    return statevector.draw("bloch")


def sv_tensor(quantum_circuit_1: QuantumCircuit, quantum_circuit_2: QuantumCircuit):
    """Berechnet das äußere Produkt der Zustandsvektoren zweier Quantenschaltkreise.

    Parameter:
        quantum_circuit_1 (QuantumCircuit): Der erste zu simulierende Quantenschaltkreis.
        quantum_circuit_2 (QuantumCircuit): Der zweite zu simulierende Quantenschaltkreis.

    Rückgabe:
        np.ndarray: Das äußere Produkt der Zustandsvektoren der beiden Quantenschaltkreise.
    """

    statevector_1 = sv_compute(quantum_circuit_1)
    statevector_2 = sv_compute(quantum_circuit_2)

    output_latex = (
        r"\Bigg["
        + statevector_1.draw("latex_source")
        + r"\Bigg] \otimes \Bigg["
        + statevector_2.draw("latex_source")
        + r"\Bigg] = "
        + (statevector_1.tensor(statevector_2)).draw("latex_source")
    )

    return Math(output_latex)


def sv_interactive_blochsphere(quantum_circuit: QuantumCircuit):
    """Zeichnet den Zustandsvektor eines Quantenschaltkreises interaktiv.

    Parameter:
        quantum_circuit (QuantumCircuit): Der zu simulierende Quantenschaltkreis.
    """

    if quantum_circuit.num_qubits != 1:
        raise ValueError(
            "Die Darstellung des Zustandsvektors in der Bloch-Kugel wird nur für Schaltkreise mit einem einzelnen Qubit unterstützt."
        )

    if quantum_circuit.num_parameters == 0:
        return sv_blochsphere(quantum_circuit)

    sliders = {}
    value_labels = {}
    rows = []
    for param in quantum_circuit.parameters:
        sliders[param.name] = ipywidgets.FloatSlider(
            value=0,
            min=-2,
            max=2,
            step=0.1,
            description=param.name,
            continuous_update=True,
            readout=False,
        )

        value_labels[param.name] = ipywidgets.HTMLMath(
            value=f"{sliders[param.name].value:.1f}π = {sliders[param.name].value * np.pi:.2f}"
        )
        update_value = lambda change, pn=param.name: setattr(
            value_labels[pn],
            "value",
            f"{change['new']:.1f}π = {change['new'] * np.pi:.2f}",
        )

        sliders[param.name].observe(update_value, names="value")

        rows.append(
            ipywidgets.HBox(
                [sliders[param.name], value_labels[param.name]],
                layout=ipywidgets.Layout(align_items="center"),
            )
        )

    controls = ipywidgets.VBox(rows)

    def plot_ry(**parameter_values):
        param_dict = {
            param: parameter_values[param.name] * np.pi
            for param in quantum_circuit.parameters
        }
        qc_param = quantum_circuit.assign_parameters(param_dict, inplace=False)
        return display(sv_blochsphere(qc_param))

    out = ipywidgets.interactive_output(plot_ry, sliders)

    ui = ipywidgets.VBox([controls, out])
    return ui
