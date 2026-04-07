"""Ví dụ: build, sign và gửi transaction gọi hàm set(uint256) trên SimpleStorage contract.

Sử dụng:
python send_tx_example.py --abi path/to/SimpleStorage.abi --address 0x... --private-key 0x...
"""
import argparse
import os
from web3 import Web3

from web3_utils import get_web3, load_abi, get_contract, build_tx_for_contract_function, sign_and_send_raw_transaction


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--abi', required=True)
    parser.add_argument('--address', required=True)
    parser.add_argument('--private-key', required=True)
    parser.add_argument('--value', required=True, type=int)
    parser.add_argument('--provider', default=os.getenv('WEB3_PROVIDER', 'http://localhost:8545'))
    args = parser.parse_args()

    w3 = get_web3(args.provider)
    abi = load_abi(args.abi)
    contract = get_contract(w3, abi, args.address)

    # build contract function tx
    contract_fn = contract.functions.set(args.value)
    tx = build_tx_for_contract_function(w3, contract_fn, tx_params={'from': w3.eth.accounts[0], 'gas': 100000})

    receipt = sign_and_send_raw_transaction(w3, args.private_key, tx, wait_for_receipt=True)
    print('Receipt:', receipt)


if __name__ == '__main__':
    main()
