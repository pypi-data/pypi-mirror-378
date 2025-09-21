import json
import os
from mscp.lib import get_data_types, parse_method_to_function
from eth_abi import encode, decode
from web3 import Web3


class ERC7654Connector:
    def __init__(self, rpc, address, account, name="erc7654"):
        self.rpc = rpc
        self.address = address
        self.web3 = Web3(Web3.HTTPProvider(rpc))
        self.account = account
        self.name = name
        # Get the directory of this module and construct the ABI file path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        abi_path = os.path.join(current_dir, "abis", "erc7654.json")
        with open(abi_path, "r") as f:
            abi = json.load(f)
        self.contract = self.web3.eth.contract(address=self.address, abi=abi)
        self.methods = self.get_methods()

    def call_function(self, function):

        method_data_values = list(json.loads(function.arguments).values())
        method = [item for item in self.methods if item["name"] == function.name][0]
        method_type = method["type"]
        methdo_name = method["name"]

        method_params = "0x" + encode(method["req"], method_data_values).hex()

        if method_type == "get":
            method_response = self.contract.functions.get(
                methdo_name, method_params
            ).call()

            decoded = decode(method["res"], method_response)
            result = ",".join(map(str, decoded))

            return result
        else:

            post_put_func = getattr(self.contract.functions, method_type)
            build_args = {
                "from": self.account.address,
                "nonce": self.web3.eth.get_transaction_count(self.account.address),
                "value": 0,
            }

            estimated_txn = post_put_func(methdo_name, method_params).build_transaction(
                build_args
            )
            estimated_gas = self.web3.eth.estimate_gas(estimated_txn)
            gasPrice = self.web3.eth.gas_price
            txn_args = {
                "from": self.account.address,
                "nonce": self.web3.eth.get_transaction_count(self.account.address),
                "gasPrice": gasPrice,
                "gas": estimated_gas,
                "value": 0,
            }
            txn = post_put_func(methdo_name, method_params).build_transaction(txn_args)
            signed_txn = self.account.sign_transaction(txn)
            txn_hash = self.web3.eth.send_raw_transaction(
                signed_txn.raw_transaction
            ).hex()
            receipt = self.web3.eth.wait_for_transaction_receipt(txn_hash)

            if len(method["res"]) > 0:
                post_event = self.contract.events.Response().process_receipt(receipt)[0]
                decoded = decode(method["res"], post_event["args"]["_response"])
                result = ",".join(map(str, decoded))
                return result
            else:
                return receipt["transactionHash"].hex()

    def get_methods(self):
        options = self.contract.functions.options().call()
        options_str = ["get", "post", "put"]
        methods_response = []
        for option in options:
            methods = self.contract.functions.getMethods(option).call()
            for method in methods:
                req, res = self.contract.functions.getMethodReqAndRes(method).call()
                instruction = self.contract.functions.getMethodInstruction(
                    method
                ).call()
                methods_response.append(
                    {
                        "name": method,
                        "type": options_str[option],
                        "req": [get_data_types(x) for x in req],
                        "res": [get_data_types(x) for x in res],
                        "rpc": self.rpc,
                        "address": self.address,
                        "instruction": instruction,
                    }
                )
        return methods_response

    def get_functions(self):
        funtions = parse_method_to_function(self.methods)
        return funtions
