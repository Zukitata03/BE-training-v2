"""Tiện ích kết nối và tương tác cơ bản với blockchain (web3.py).

Mô tả: cung cấp các hàm helper để:
- Khởi tạo Web3 provider (HTTP hoặc WebSocket)
- Nạp ABI từ file JSON
- Tạo đối tượng contract
- Đọc dữ liệu (call các hàm view / pure)
- Gửi giao dịch đã ký (sign & send raw tx)
- Chờ transaction receipt
- Lấy balance (ETH) và balance ERC20

Hướng dẫn nhanh sử dụng:
1. Khởi chạy local node (ví dụ ganache) hoặc kết nối tới testnet provider (Infura/Alchemy).
2. Thiết lập biến môi trường WEB3_PROVIDER (ví dụ http://localhost:8545).
3. Chuẩn bị ABI file và địa chỉ contract.
4. Import các hàm bên dưới và gọi.

Lưu ý bảo mật: không lưu private key trong repo; trong môi trường production phải dùng vault/secret manager.
"""
from web3 import Web3
import json
import os
import time
from typing import Any, Dict, Optional


def get_web3(provider_uri: Optional[str] = None) -> Web3:
    """Khởi tạo Web3 instance.

    Thử Websocket nếu URI bắt đầu bằng ws:// hoặc wss://
    """
    provider_uri = provider_uri or os.getenv("WEB3_PROVIDER", "http://localhost:8545")
    if provider_uri.startswith("ws"):
        provider = Web3.WebsocketProvider(provider_uri)
    else:
        provider = Web3.HTTPProvider(provider_uri)
    w3 = Web3(provider)
    # Nếu node là ganache hay geth --dev đôi khi không tự bật tính năng chainId; kiểm tra kết nối
    if not w3.isConnected():
        raise ConnectionError(f"Không thể kết nối đến provider: {provider_uri}")
    return w3


def load_abi(abi_path: str) -> Dict[str, Any]:
    """Nạp ABI từ file JSON (định dạng chuẩn của solidity compile output hoặc ABI array).

    abi_path: đường dẫn tới file .json hoặc .abi
    """
    with open(abi_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # file có thể chứa object compile (trong đó có key 'abi') hoặc chỉ mảng abi
    if isinstance(data, dict) and "abi" in data:
        return data["abi"]
    return data


def get_contract(w3: Web3, abi: Dict[str, Any], address: str):
    """Tạo instance contract từ ABI và địa chỉ.
    address: chuỗi hex address (0x...)
    """
    return w3.eth.contract(address=w3.toChecksumAddress(address), abi=abi)


def get_eth_balance(w3: Web3, address: str) -> float:
    """Trả về balance ETH của address (đơn vị ether, float)."""
    balance_wei = w3.eth.get_balance(w3.toChecksumAddress(address))
    return w3.fromWei(balance_wei, "ether")


def get_erc20_balance(contract, address: str) -> int:
    """Trả về balance token (raw integer theo decimals) bằng call balanceOf."""
    # ensure checksum address
    checksum_addr = Web3.toChecksumAddress(address)
    return contract.functions.balanceOf(checksum_addr).call()


def get_erc20_balance_human(contract, address: str) -> float:
    """Trả về balance token đã quy đổi theo decimals (float)."""
    checksum_addr = Web3.toChecksumAddress(address)
    raw = contract.functions.balanceOf(checksum_addr).call()
    # try to get decimals; default 18
    try:
        decimals = contract.functions.decimals().call()
    except Exception:
        decimals = 18
    return raw / (10 ** decimals)


def call_view_function(contract, fn_name: str, *args):
    """Gọi một hàm view/pure của contract và trả về kết quả.

    Ví dụ: call_view_function(contract, 'get', )
    """
    fn = getattr(contract.functions, fn_name)
    return fn(*args).call()


def estimate_gas_for_tx(contract_function_tx, tx_params: Dict[str, Any]) -> int:
    """Ước lượng gas cho một transaction tạo bởi method của contract.
    contract_function_tx: contract.functions.myMethod(...)
    tx_params: dict như {'from': from_addr}
    """
    return contract_function_tx.estimateGas(tx_params)


def sign_and_send_raw_transaction(w3: Web3, private_key: str, tx: Dict[str, Any], wait_for_receipt: bool = True, timeout: int = 120):
    """Ký transaction bằng private_key và gửi lên mạng.

    tx: phải chứa fields tối thiểu: to, value, gas, gasPrice (hoặc maxFeePerGas), nonce, chainId (nếu cần)
    Trả về receipt nếu wait_for_receipt True, ngược lại trả tx_hash.
    """
    account = w3.eth.account.from_key(private_key)
    # Nếu nonce không được cung cấp thì lấy current
    if "nonce" not in tx:
        tx["nonce"] = w3.eth.get_transaction_count(account.address)
    # Nếu chainId thiếu thì thử lấy từ node
    if "chainId" not in tx:
        try:
            tx["chainId"] = w3.eth.chain_id
        except Exception:
            pass
    signed = w3.eth.account.sign_transaction(tx, private_key)
    raw = signed.rawTransaction
    tx_hash = w3.eth.send_raw_transaction(raw)
    if not wait_for_receipt:
        return tx_hash.hex()
    receipt = wait_tx_receipt(w3, tx_hash, timeout=timeout)
    return receipt


def wait_tx_receipt(w3: Web3, tx_hash, timeout: int = 120, poll_interval: float = 2.0):
    """Chờ transaction receipt tới timeout (giây)."""
    start = time.time()
    while True:
        try:
            receipt = w3.eth.get_transaction_receipt(tx_hash)
            if receipt is not None:
                return receipt
        except Exception:
            pass
        if time.time() - start > timeout:
            raise TimeoutError(f"Timeout chờ receipt cho tx {tx_hash.hex() if hasattr(tx_hash, 'hex') else tx_hash}")
        time.sleep(poll_interval)


def get_contract_events(contract, event_name: str, from_block: int = 0, to_block: str = 'latest'):
    """Lấy tất cả events của contract theo tên sự kiện từ from_block -> to_block.

    Trả về list of event dicts.
    """
    if not hasattr(contract.events, event_name):
        raise ValueError(f"Contract has no event named {event_name}")
    event_cls = getattr(contract.events, event_name)
    # create filter and get entries (note: on some providers this requires archival node)
    event_filter = event_cls.createFilter(fromBlock=from_block, toBlock=to_block)
    return event_filter.get_all_entries()


def build_tx_for_contract_function(w3: Web3, contract_function, tx_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Build basic tx dict for a contract function call (to be signed).

    contract_function: contract.functions.myMethod(...)
    tx_params: optional dict overrides (from, gas, gasPrice, value, nonce)
    """
    tx_params = tx_params or {}
    # populate standard fields
    tx = contract_function.buildTransaction({
        'from': tx_params.get('from', w3.eth.accounts[0] if w3.eth.accounts else None),
        'value': tx_params.get('value', 0),
    })
    # merge overrides
    tx.update({k: v for k, v in tx_params.items() if v is not None})
    # ensure nonce
    if 'nonce' not in tx:
        if tx.get('from'):
            tx['nonce'] = w3.eth.get_transaction_count(Web3.toChecksumAddress(tx['from']))
    # set chainId if missing
    if 'chainId' not in tx:
        try:
            tx['chainId'] = w3.eth.chain_id
        except Exception:
            pass
    return tx


def w3_checksum(addr: str) -> str:
    """Trả về checksum address nếu có, hoặc raise nếu invalid"""
    try:
        return Web3.toChecksumAddress(addr)
    except Exception as e:
        raise ValueError(f"Invalid address: {addr}") from e
