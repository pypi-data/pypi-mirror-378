"""Packaged AST with Run/Noise model nodes added."""
from dataclasses import dataclass
from enum import Enum


class NodeType(Enum):
    NUMBER = "NUMBER"
    STRING = "STRING"
    IDENTIFIER = "IDENTIFIER"
    UNCERTAIN = "UNCERTAIN"
    BINARY_OP = "BINARY_OP"
    UNARY_OP = "UNARY_OP"
    ASSIGNMENT = "ASSIGNMENT"
    FUNCTION_CALL = "FUNCTION_CALL"
    LIST = "LIST"
    MATRIX = "MATRIX"
    TENSOR = "TENSOR"
    HYPOTHESIS = "HYPOTHESIS"
    EXPERIMENT = "EXPERIMENT"
    PARALLEL = "PARALLEL"
    BRANCH = "BRANCH"
    STREAM = "STREAM"
    REASON_CHAIN = "REASON_CHAIN"
    PREMISE = "PREMISE"
    DERIVE = "DERIVE"
    CONCLUDE = "CONCLUDE"
    PIPELINE = "PIPELINE"
    STAGE = "STAGE"
    EXPLORE = "EXPLORE"
    TRY = "TRY"
    FALLBACK = "FALLBACK"
    PROPAGATE = "PROPAGATE"
    PROVE = "PROVE"
    QUANTUM_CIRCUIT = "QUANTUM_CIRCUIT"
    QUANTUM_GATE = "QUANTUM_GATE"
    QUANTUM_MEASURE = "QUANTUM_MEASURE"
    QUANTUM_BACKEND = "QUANTUM_BACKEND"
    QUANTUM_ALGORITHM = "QUANTUM_ALGORITHM"
    QUANTUM_ANSATZ = "QUANTUM_ANSATZ"
    QUANTUM_RUN = "QUANTUM_RUN"
    RUN = "RUN"
    BLOCK = "BLOCK"
    PROGRAM = "PROGRAM"


@dataclass
class ASTNode:
    node_type: NodeType
    line: int
    column: int


@dataclass
class NumberNode(ASTNode):
    value: float
    def __init__(self, value: float, line: int, column: int):
        super().__init__(NodeType.NUMBER, line, column)
        self.value = value


@dataclass
class StringNode(ASTNode):
    value: str
    def __init__(self, value: str, line: int, column: int):
        super().__init__(NodeType.STRING, line, column)
        self.value = value


@dataclass
class IdentifierNode(ASTNode):
    name: str
    def __init__(self, name: str, line: int, column: int):
        super().__init__(NodeType.IDENTIFIER, line, column)
        self.name = name


@dataclass
class UncertainNode(ASTNode):
    value: float
    uncertainty: float
    def __init__(self, value: float, uncertainty: float, line: int, column: int):
        super().__init__(NodeType.UNCERTAIN, line, column)
        self.value = value
        self.uncertainty = uncertainty


@dataclass
class ListNode(ASTNode):
    elements: list[ASTNode]
    def __init__(self, elements: list[ASTNode], line: int, column: int):
        super().__init__(NodeType.LIST, line, column)
        self.elements = elements


@dataclass
class MatrixNode(ASTNode):
    rows: list[list[ASTNode]]
    def __init__(self, rows: list[list[ASTNode]], line: int, column: int):
        super().__init__(NodeType.MATRIX, line, column)
        self.rows = rows


@dataclass
class TensorNode(ASTNode):
    dimensions: list[int]
    values: list[ASTNode]
    def __init__(self, dimensions: list[int], values: list[ASTNode], line: int, column: int):
        super().__init__(NodeType.TENSOR, line, column)
        self.dimensions = dimensions
        self.values = values


@dataclass
class QuantumCircuitNode(ASTNode):
    name: str
    qubits: int
    gates: list["QuantumGateNode"]
    measurements: list["QuantumMeasureNode"]
    def __init__(self, name: str, qubits: int, gates: list["QuantumGateNode"], measurements: list["QuantumMeasureNode"], line: int, column: int):
        super().__init__(NodeType.QUANTUM_CIRCUIT, line, column)
        self.name = name
        self.qubits = qubits
        self.gates = gates
        self.measurements = measurements


@dataclass
class QuantumGateNode(ASTNode):
    gate_type: str
    qubits: list[ASTNode]
    parameters: list[ASTNode]
    def __init__(self, gate_type: str, qubits: list[ASTNode], parameters: list[ASTNode], line: int, column: int):
        super().__init__(NodeType.QUANTUM_GATE, line, column)
        self.gate_type = gate_type
        self.qubits = qubits
        self.parameters = parameters


@dataclass
class QuantumMeasureNode(ASTNode):
    qubits: list[ASTNode]
    classical_bits: list[ASTNode]
    def __init__(self, qubits: list[ASTNode], classical_bits: list[ASTNode], line: int, column: int):
        super().__init__(NodeType.QUANTUM_MEASURE, line, column)
        self.qubits = qubits
        self.classical_bits = classical_bits


@dataclass
class QuantumBackendNode(ASTNode):
    name: str
    config: dict[str, ASTNode]
    def __init__(self, name: str, config: dict[str, ASTNode], line: int, column: int):
        super().__init__(NodeType.QUANTUM_BACKEND, line, column)
        self.name = name
        self.config = config


@dataclass
class QuantumAlgorithmNode(ASTNode):
    name: str
    parameters: list[ASTNode]
    ansatz: "QuantumAnsatzNode"
    cost_function: ASTNode
    optimizer: ASTNode
    def __init__(self, name: str, parameters: list[ASTNode], ansatz: "QuantumAnsatzNode", cost_function: ASTNode, optimizer: ASTNode, line: int, column: int):
        super().__init__(NodeType.QUANTUM_ALGORITHM, line, column)
        self.name = name
        self.parameters = parameters
        self.ansatz = ansatz
        self.cost_function = cost_function
        self.optimizer = optimizer


@dataclass
class QuantumAnsatzNode(ASTNode):
    name: str
    layers: list[ASTNode]
    def __init__(self, name: str, layers: list[ASTNode], line: int, column: int):
        super().__init__(NodeType.QUANTUM_ANSATZ, line, column)
        self.name = name
        self.layers = layers

@dataclass
class QuantumRunNode(ASTNode):
    """Quantum circuit execution (run) configuration.
    Represents: run <circuit> [with backend <backend>] { shots: N, noise_model: depolarizing, p1q: 0.001, ... }
    """
    circuit_name: str
    backend_name: str | None
    config: dict[str, ASTNode]

    def __init__(self, circuit_name: str, backend_name: str | None, config: dict[str, ASTNode], line: int, column: int):
        super().__init__(NodeType.QUANTUM_RUN, line, column)
        self.circuit_name = circuit_name
        self.backend_name = backend_name
        self.config = config

# Backward compatibility alias used by packaged parser earlier naming (RunNode)
RunNode = QuantumRunNode


@dataclass
class BinaryOpNode(ASTNode):
    operator: str
    left: ASTNode
    right: ASTNode
    def __init__(self, operator: str, left: ASTNode, right: ASTNode, line: int, column: int):
        super().__init__(NodeType.BINARY_OP, line, column)
        self.operator = operator
        self.left = left
        self.right = right


@dataclass
class UnaryOpNode(ASTNode):
    operator: str
    operand: ASTNode
    def __init__(self, operator: str, operand: ASTNode, line: int, column: int):
        super().__init__(NodeType.UNARY_OP, line, column)
        self.operator = operator
        self.operand = operand


@dataclass
class AssignmentNode(ASTNode):
    target: IdentifierNode
    value: ASTNode
    is_uncertain: bool = False
    is_constrained: bool = False
    is_evolving: bool = False
    def __init__(self, target: IdentifierNode, value: ASTNode, line: int, column: int, is_uncertain: bool = False, is_constrained: bool = False, is_evolving: bool = False):
        super().__init__(NodeType.ASSIGNMENT, line, column)
        self.target = target
        self.value = value
        self.is_uncertain = is_uncertain
        self.is_constrained = is_constrained
        self.is_evolving = is_evolving


@dataclass
class FunctionCallNode(ASTNode):
    function: IdentifierNode
    arguments: list[ASTNode]
    def __init__(self, function: IdentifierNode, arguments: list[ASTNode], line: int, column: int):
        super().__init__(NodeType.FUNCTION_CALL, line, column)
        self.function = function
        self.arguments = arguments


@dataclass
class ParallelNode(ASTNode):
    branches: list["BranchNode"]
    num_workers: int | None
    def __init__(self, branches: list["BranchNode"], line: int, column: int, num_workers: int | None = None):
        super().__init__(NodeType.PARALLEL, line, column)
        self.branches = branches
        self.num_workers = num_workers


@dataclass
class BranchNode(ASTNode):
    name: str
    body: ASTNode
    def __init__(self, name: str, body: ASTNode, line: int, column: int):
        super().__init__(NodeType.BRANCH, line, column)
        self.name = name
        self.body = body


@dataclass
class StreamNode(ASTNode):
    name: str
    body: "BlockNode"
    def __init__(self, name: str, body: "BlockNode", line: int, column: int):
        super().__init__(NodeType.STREAM, line, column)
        self.name = name
        self.body = body


@dataclass
class HypothesisNode(ASTNode):
    name: str
    assumptions: list[ASTNode]
    predictions: list[ASTNode]
    validations: list[ASTNode]
    def __init__(self, name: str, assumptions: list[ASTNode], predictions: list[ASTNode], validations: list[ASTNode], line: int, column: int):
        super().__init__(NodeType.HYPOTHESIS, line, column)
        self.name = name
        self.assumptions = assumptions
        self.predictions = predictions
        self.validations = validations


@dataclass
class ExperimentNode(ASTNode):
    name: str
    setup: ASTNode | None
    procedure: ASTNode
    analysis: ASTNode | None
    def __init__(self, name: str, procedure: ASTNode, line: int, column: int, setup: ASTNode | None = None, analysis: ASTNode | None = None):
        super().__init__(NodeType.EXPERIMENT, line, column)
        self.name = name
        self.setup = setup
        self.procedure = procedure
        self.analysis = analysis


@dataclass
class ReasonChainNode(ASTNode):
    name: str
    premises: list["PremiseNode"]
    derivations: list["DeriveNode"]
    conclusion: "ConcludeNode"
    def __init__(self, name: str, premises: list["PremiseNode"], derivations: list["DeriveNode"], conclusion: "ConcludeNode", line: int, column: int):
        super().__init__(NodeType.REASON_CHAIN, line, column)
        self.name = name
        self.premises = premises
        self.derivations = derivations
        self.conclusion = conclusion


@dataclass
class PremiseNode(ASTNode):
    name: str
    statement: ASTNode
    def __init__(self, name: str, statement: ASTNode, line: int, column: int):
        super().__init__(NodeType.PREMISE, line, column)
        self.name = name
        self.statement = statement


@dataclass
class DeriveNode(ASTNode):
    name: str
    from_premise: str
    statement: ASTNode
    def __init__(self, name: str, from_premise: str, statement: ASTNode, line: int, column: int):
        super().__init__(NodeType.DERIVE, line, column)
        self.name = name
        self.from_premise = from_premise
        self.statement = statement


@dataclass
class ConcludeNode(ASTNode):
    condition: ASTNode
    result: ASTNode
    def __init__(self, condition: ASTNode, result: ASTNode, line: int, column: int):
        super().__init__(NodeType.CONCLUDE, line, column)
        self.condition = condition
        self.result = result


@dataclass
class PipelineNode(ASTNode):
    name: str
    stages: list["StageNode"]
    def __init__(self, name: str, stages: list["StageNode"], line: int, column: int):
        super().__init__(NodeType.PIPELINE, line, column)
        self.name = name
        self.stages = stages


@dataclass
class StageNode(ASTNode):
    name: str
    body: ASTNode
    parallel_count: int | None
    def __init__(self, name: str, body: ASTNode, line: int, column: int, parallel_count: int | None = None):
        super().__init__(NodeType.STAGE, line, column)
        self.name = name
        self.body = body
        self.parallel_count = parallel_count


@dataclass
class ExploreNode(ASTNode):
    name: str
    tries: list["TryNode"]
    fallbacks: list["FallbackNode"]
    accept_condition: ASTNode | None
    reject_condition: ASTNode | None
    def __init__(self, name: str, tries: list["TryNode"], fallbacks: list["FallbackNode"], line: int, column: int, accept_condition: ASTNode | None = None, reject_condition: ASTNode | None = None):
        super().__init__(NodeType.EXPLORE, line, column)
        self.name = name
        self.tries = tries
        self.fallbacks = fallbacks
        self.accept_condition = accept_condition
        self.reject_condition = reject_condition


@dataclass
class TryNode(ASTNode):
    name: str
    body: ASTNode
    def __init__(self, name: str, body: ASTNode, line: int, column: int):
        super().__init__(NodeType.TRY, line, column)
        self.name = name
        self.body = body


@dataclass
class FallbackNode(ASTNode):
    name: str
    body: ASTNode
    def __init__(self, name: str, body: ASTNode, line: int, column: int):
        super().__init__(NodeType.FALLBACK, line, column)
        self.name = name
        self.body = body


@dataclass
class PropagateNode(ASTNode):
    uncertainty_var: str
    through_body: ASTNode
    def __init__(self, uncertainty_var: str, through_body: ASTNode, line: int, column: int):
        super().__init__(NodeType.PROPAGATE, line, column)
        self.uncertainty_var = uncertainty_var
        self.through_body = through_body


@dataclass
class ProveNode(ASTNode):
    statement: ASTNode
    method: ASTNode | None
    def __init__(self, statement: ASTNode, method: ASTNode | None, line: int, column: int):
        super().__init__(NodeType.PROVE, line, column)
        self.statement = statement
        self.method = method


@dataclass
class RunNode(ASTNode):
    circuit_name: str
    backend_name: str | None
    options: dict[str, ASTNode]
    def __init__(self, circuit_name: str, backend_name: str | None, options: dict[str, ASTNode], line: int, column: int):
        super().__init__(NodeType.RUN, line, column)
        self.circuit_name = circuit_name
        self.backend_name = backend_name
        self.options = options


@dataclass
class BlockNode(ASTNode):
    statements: list[ASTNode]
    def __init__(self, statements: list[ASTNode], line: int, column: int):
        super().__init__(NodeType.BLOCK, line, column)
        self.statements = statements


@dataclass
class ProgramNode(ASTNode):
    body: list[ASTNode]
    def __init__(self, body: list[ASTNode]):
        super().__init__(NodeType.PROGRAM, 0, 0)
        self.body = body


def walk(node: ASTNode):  # simple utility for debugging
    yield node
    for attr in vars(node).values():
        if isinstance(attr, ASTNode):
            yield from walk(attr)
        elif isinstance(attr, list):
            for v in attr:
                if isinstance(v, ASTNode):
                    yield from walk(v)
