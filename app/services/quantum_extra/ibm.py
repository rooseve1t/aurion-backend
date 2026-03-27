"""
IBM Quantum client for Aurion OS
"""
import logging
from typing import Dict, Any, Optional

try:
    from qiskit import QuantumCircuit, transpile
    from qiskit_ibm_provider import IBMProvider
    QISKIT_IBM_AVAILABLE = True
except ImportError:
    QISKIT_IBM_AVAILABLE = False
    QuantumCircuit = None
    IBMProvider = None

logger = logging.getLogger(__name__)

class IBMClient:
    """Client for interacting with IBM Quantum services."""

    def __init__(self, token: str):
        if not QISKIT_IBM_AVAILABLE:
            raise RuntimeError("qiskit-ibm-provider is not installed")
        self.token = token
        self.provider = None

    def connect(self):
        """Connect to IBM Quantum.
        
        Raises:
            Exception: If connection fails.
        """
        try:
            self.provider = IBMProvider(token=self.token)
            logger.info("Successfully connected to IBM Quantum.")
        except Exception as e:
            logger.error(f"Failed to connect to IBM Quantum: {e}")
            raise

    def get_backend(self, backend_name: str = "ibmq_qasm_simulator"):
        """Get a quantum backend.

        Args:
            backend_name (str, optional): The name of the backend. Defaults to "ibmq_qasm_simulator".

        Returns:
            Any: The backend object.
        """
        if not self.provider:
            self.connect()
        
        return self.provider.get_backend(backend_name)

    def run_circuit(self, circuit, backend_name: str = "ibmq_qasm_simulator", shots: int = 1024) -> Dict[str, Any]:
        """Run a quantum circuit on an IBM Quantum backend.

        Args:
            circuit: The quantum circuit to run.
            backend_name (str, optional): The name of the backend. Defaults to "ibmq_qasm_simulator".
            shots (int, optional): The number of shots. Defaults to 1024.

        Returns:
            Dict[str, Any]: The results of the job.
        """
        backend = self.get_backend(backend_name)
        transpiled_circuit = transpile(circuit, backend)
        job = backend.run(transpiled_circuit, shots=shots)
        result = job.result()
        counts = result.get_counts(transpiled_circuit)
        
        return {
            "counts": counts,
            "job_id": job.job_id()
        }
