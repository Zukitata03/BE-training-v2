"""Ví dụ: gọi hàm view của Smart Contract (SimpleStorage.get) bằng web3.py

Yêu cầu:
- Đã deploy SimpleStorage contract và có ABI file `SimpleStorage.abi` (JSON array) cùng với địa chỉ contract.
- Chạy node (ganache) trên WEB3_PROVIDER (mặc định http://localhost:8545).

Chạy:
$ python call_contract_read.py --abi path/to/SimpleStorage.abi --address 0x...

"""
import argparse
import json
import os

from web3_utils import get_web3, load_abi, get_contract, call_view_function


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--abi", required=True, help="Path to contract ABI JSON")
    parser.add_argument("--address", required=True, help="Contract address")
    parser.add_argument("--provider", default=os.getenv("WEB3_PROVIDER", "http://localhost:8545"))
    args = parser.parse_args()

    w3 = get_web3(args.provider)
    abi = load_abi(args.abi)
    contract = get_contract(w3, abi, args.address)

    val = call_view_function(contract, 'get')
    print("Contract get() returned:", val)


if __name__ == '__main__':
    main()
