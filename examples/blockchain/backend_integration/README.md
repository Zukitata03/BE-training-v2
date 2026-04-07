# Blockchain integration examples (TrainingAPI)

Hướng dẫn nhanh để gọi dữ liệu từ blockchain và gửi giao dịch bằng Python (web3.py).

Yêu cầu
- Python 3.9+
- Chạy local node (Ganache) hoặc cung cấp `WEB3_PROVIDER` tới testnet (Infura/Alchemy)
- Cài dependencies: `pip install -r requirements.txt`

File chính
- `web3_utils.py`: helpers để kết nối, nạp ABI, tạo contract, đọc balance, gửi giao dịch đã ký.
- `call_contract_read.py`: script mẫu để gọi hàm view (get) của SimpleStorage.
- `send_tx_example.py`: script mẫu để xây dựng, ký và gửi transaction (ví dụ gọi set(uint256) của SimpleStorage).

Chạy nhanh (local Ganache)
1. Chạy ganache:

```bash
# nếu cài ganache CLI
ganache -p 8545
# hoặc docker
docker run -p 8545:8545 trufflesuite/ganache-cli:latest -h 0.0.0.0 -p 8545
```

2. Chuẩn bị ABI và địa chỉ contract (deploy contract trước bằng một script deploy hoặc công cụ như Remix/Brownie)

3. Gọi read:

```bash
python call_contract_read.py --abi ./path/to/SimpleStorage.abi --address 0xYourContractAddress
```

4. Gửi tx (ví dụ):

```bash
python send_tx_example.py --abi ./path/to/SimpleStorage.abi --address 0xYourContractAddress --private-key 0xYourPrivateKey --value 123
```

Lưu ý bảo mật: KHÔNG lưu private key trong repo. Dùng biến môi trường hoặc secret manager cho môi trường không an toàn.
