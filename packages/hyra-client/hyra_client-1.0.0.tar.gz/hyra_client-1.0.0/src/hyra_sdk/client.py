import json
from pathlib import Path
import random
from web3 import Web3
import os
from dotenv import load_dotenv
import zkp_rust_client
from typing import Optional, Dict, List, Union, Tuple
from web3.contract import Contract

# Load environment variables from .env file
load_dotenv()

# Contract addresses for the Hyra task pool system
TASK__POOL_FACTORY_ADDRESS = "0x19afd9f3c69e98A08D50c665D3A543eb2B187e68"
TASK_POOL_ROUTER_ADDRESS = "0x615C7F453D491b48B158Fcd806f16EB8D25c2584"
POOL_VIEWER_ADDRESS = "0x7c7bF46d2747559Ed6754ACAF9eF880F07ea3CE6"
MODEL_REGISTRY_ADDRESS = "0xE1Fe675381F03358CcB06225A6BBf5dc13D3b426"

# Load ABI files for smart contract interaction
# Get the directory where this file is located
_current_dir = Path(__file__).parent
factory_abi_path = _current_dir / "abis" / "pool-factory.json"
task_pool_abi_path = _current_dir / "abis" / "task-pool.json"
pool_viewer_abi_path = _current_dir / "abis" / "pool-viewer.json"
task_pool_router_abi_path = _current_dir / "abis" / "pool-router.json"
model_registry_abi_path = _current_dir / "abis" / "model-registry.json"

factory_contract_abi = json.loads(factory_abi_path.read_text("utf-8"))
task_pool_contract_abi = json.loads(task_pool_abi_path.read_text("utf-8"))
pool_viewer_contract_abi = json.loads(pool_viewer_abi_path.read_text("utf-8"))
task_pool_router_contract_abi = json.loads(task_pool_router_abi_path.read_text("utf-8"))
model_registry_contract_abi = json.loads(model_registry_abi_path.read_text("utf-8"))


class HyraClient:
    """
    HyraClient - Main client for interacting with the Hyra task pool system.

    This client provides a simple interface to claim tasks, submit results,
    and interact with the Hyra decentralized task marketplace.

    Features:
    - Task claiming and submission
    - ZKP proof generation and verification
    - Pool statistics and monitoring
    - Model registry access
    - Global system statistics
    """

    def __init__(
        self, private_key: Optional[str] = None, rpc_url: Optional[str] = None
    ) -> None:
        """
        Initialize HyraClient with private key and RPC URL.

        Args:
            private_key: Private key for wallet operations. Can be provided via:
                        - Constructor parameter
                        - PRIVATE_KEY environment variable
                        - WALLET_PRIVATE_KEY environment variable
                        - HYRA_PRIVATE_KEY environment variable
                        - .env file
            rpc_url: RPC URL for blockchain connection. Defaults to Hyra testnet.

        Raises:
            ValueError: If no private key is provided through any method
        """
        # Try to get private key from environment variables first
        if private_key is None:
            private_key = os.getenv("PRIVATE_KEY")

        # If still None, try other common environment variable names
        if private_key is None:
            private_key = os.getenv("WALLET_PRIVATE_KEY")

        if private_key is None:
            private_key = os.getenv("HYRA_PRIVATE_KEY")

        # If no private key found, raise error
        if private_key is None:
            raise ValueError(
                "No private key provided. Please set one of the following:\n"
                "1. Pass private_key parameter to constructor\n"
                "2. Set PRIVATE_KEY environment variable\n"
                "3. Set WALLET_PRIVATE_KEY environment variable\n"
                "4. Set HYRA_PRIVATE_KEY environment variable\n"
                "5. Add PRIVATE_KEY to .env file"
            )

        self.private_key = private_key
        if rpc_url is None:
            rpc_url = "https://rpc-testnet.hyra.network"
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.account = self.w3.eth.account.from_key(self.private_key)
        self.task_pool_factory = self.w3.eth.contract(
            address=TASK__POOL_FACTORY_ADDRESS, abi=factory_contract_abi
        )
        self.task_pool_router = self.w3.eth.contract(
            address=TASK_POOL_ROUTER_ADDRESS, abi=task_pool_router_contract_abi
        )
        self.pool_viewer = self.w3.eth.contract(
            address=POOL_VIEWER_ADDRESS, abi=pool_viewer_contract_abi
        )
        self.model_registry = self.w3.eth.contract(
            address=MODEL_REGISTRY_ADDRESS, abi=model_registry_contract_abi
        )
        self.rpc_url = rpc_url
        self.private_key = private_key

    def claim_task(self) -> Dict[str, Union[int, str, bool, None]]:
        """
        Claim a task from the task pool system.

        If user already has an active task, returns that task.
        Otherwise, claims a new task from the best available pool.

        Returns:
            Dict containing task information:
            - task_id (int): Unique task identifier
            - reward (int): Reward amount in wei for completing the task
            - deadline (int): Unix timestamp when task expires
            - assigned_to (str): Address of the user assigned to this task
            - request_id (int): ID of the user's inference request
            - model_name (str): Name of the AI model to use
            - input_data (str): Input data/prompt for the task
            - pool_address (str): Address of the task pool contract
            - tx_hash (str): Transaction hash of the claim transaction

        Raises:
            Exception: If no tasks available or blockchain transaction fails
        """
        active_task = self.task_pool_router.functions.getUserStatus(
            self.account.address
        ).call()
        has_active_task = active_task[4]
        print("🔥 has_active_task:", has_active_task)
        if has_active_task:
            pool_address = active_task[0]
            task_id = active_task[1]
            task_pool_contract = self.w3.eth.contract(
                address=pool_address, abi=task_pool_contract_abi
            )
            task_detail = task_pool_contract.functions.tasks(task_id).call()

            model_id = task_detail[8]
            model_detail = self.model_registry.functions.getModel(model_id).call()
            model_name = model_detail[0]
            return {
                "task_id": task_id,
                "reward": task_detail[0],
                "deadline": task_detail[1],
                "assigned_to": task_detail[2],
                "request_id": task_detail[7],
                "model_name": model_name,
                "input_data": task_detail[9],
                "pool_address": pool_address,
                "tx_hash": None,
            }

        # call claimBestTask() from task_pool_router
        transaction = self.task_pool_router.functions.claimBestTask().build_transaction(
            {
                "from": self.account.address,
                "nonce": self.w3.eth.get_transaction_count(self.account.address),
            }
        )
        signed_tx = self.account.sign_transaction(transaction)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        # Extract pool address and task ID from receipt logs (similar to JavaScript approach)
        logs = receipt["logs"]
        if not logs:
            raise Exception("No logs found in transaction receipt")

        # Get pool address from the first log
        pool_address = logs[0]["address"]

        # Get task ID from the third topic (index 2)
        topics = logs[0]["topics"]
        if not topics or len(topics) < 3:
            raise Exception("No task id found in transaction logs")

        task_id_hex = topics[2].hex()
        task_id = int(task_id_hex, 16)
        print("🔥 task_id:", task_id)
        print("🔥 pool_address:", pool_address)

        # Get task details from pool viewer
        pool_contract = self.w3.eth.contract(
            address=pool_address, abi=task_pool_contract_abi
        )
        task_detail = pool_contract.functions.tasks(task_id).call()
        model_id = task_detail[8]
        model_detail = self.model_registry.functions.getModel(model_id).call()
        model_name = model_detail[0]
        print("🔥 model_name:", model_name)

        return {
            "task_id": task_id,
            "reward": task_detail[0],
            "deadline": task_detail[1],
            "assigned_to": task_detail[2],
            "request_id": task_detail[7],
            "model_name": model_name,
            "input_data": task_detail[9],
            "pool_address": pool_address,
            "tx_hash": None,
        }

    def submit_task(self, task_id: int, result: str, pool_address: str) -> str:
        """
        Submit a completed task with ZKP proof for verification.

        Args:
            task_id (int): ID of the task to submit
            result (str): The task result/output
            pool_address (str): Address of the task pool contract

        Returns:
            str: Transaction hash of the submission transaction

        Raises:
            Exception: If submission fails or ZKP proof generation fails
        """

        ## generate a proof
        prover = zkp_rust_client.PyZKProver()
        start = random.randint(1, 1000000)
        increments = random.randint(1, 1000000)
        expected_result = start + increments
        proof_result = prover.generate_proof_only(start, increments)

        # Convert proof data to bytes
        proof_bytes = bytes(proof_result.proof_data())

        transaction = self.task_pool_router.functions.submitTask(
            pool_address, task_id, proof_bytes, start, expected_result, result
        ).build_transaction(
            {
                "from": self.account.address,
                "nonce": self.w3.eth.get_transaction_count(self.account.address),
            }
        )
        # Sign transaction
        signed_tx = self.account.sign_transaction(transaction)
        # Send transaction
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        # Wait for confirmation
        self.w3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_hash.hex()

    def get_all_task_pools(self) -> List[str]:
        """
        Get all task pool addresses from the factory contract.

        Returns:
            List[str]: List of task pool contract addresses
        """
        return self.task_pool_factory.functions.getAllPools().call()

    def get_supported_models(self) -> List[Dict[str, Union[str, int, bool]]]:
        """
        Get all supported AI models from the model registry.

        Returns:
            List[Dict]: List of model information dictionaries containing:
            - modelId (int): Unique model identifier
            - modelName (str): Human-readable model name
            - modelDescription (str): Model description
            - modelPricingType (str): "fixed" or "dynamic" pricing
            - modelIsActive (bool): Whether model is currently active
            - modelCreatedAt (int): Unix timestamp of model creation
            - modelTokenPrice (int): Price per token in wei
        """
        modelIds = self.model_registry.functions.getActiveModels().call()
        models = []
        for modelId in modelIds:
            model = self.model_registry.functions.getModel(modelId).call()
            models.append(
                {
                    "modelId": modelId,
                    "modelName": model[0],
                    "modelDescription": model[1],
                    "modelPricingType": "fixed" if model[2] == 0 else "dynamic",
                    "modelIsActive": model[3],
                    "modelCreatedAt": model[4],
                    "modelTokenPrice": model[5],
                }
            )
        return models

    def get_task_status(self) -> Dict[str, Union[int, str, bool]]:
        """
        Get the current status of the user's active task.

        Returns:
            Dict containing task status:
            - active_pool (str): Address of the active task pool
            - active_task_id (int): ID of the active task
            - deadline (int): Unix timestamp when task expires
            - reward (int): Reward amount in wei
            - has_active_task (bool): Whether user has an active task
        """
        data = self.task_pool_router.functions.getUserStatus(
            self.account.address
        ).call()
        return {
            "active_pool": data[0],
            "active_task_id": data[1],
            "deadline": data[2],
            "reward": data[3],
            "has_active_task": data[4],
        }

    def get_global_stats(self) -> Dict[str, Union[int, str, bool]]:
        """
        Get global statistics about the entire task pool system.

        Returns:
            Dict containing global statistics:
            - total_pools (int): Total number of task pools
            - total_active_pools (int): Number of pools with available tasks
            - total_available_tasks (int): Total tasks available across all pools
            - total_active_tasks (int): Total tasks currently being worked on
            - total_pending_tasks (int): Total tasks pending submission
            - total_processed_tasks (int): Total tasks completed
            - total_rewards_distributed (int): Total rewards paid out in wei
        """
        data = self.task_pool_router.functions.getGlobalStats().call()
        return {
            "total_pools": data[0],
            "total_active_pools": data[1],
            "total_available_tasks": data[2],
            "total_active_tasks": data[3],
            "total_pending_tasks": data[4],
            "total_processed_tasks": data[5],
            "total_rewards_distributed": data[6],
        }
