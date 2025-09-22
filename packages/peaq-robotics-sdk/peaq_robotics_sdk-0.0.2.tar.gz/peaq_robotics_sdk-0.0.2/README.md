# peaq Robotics SDK

## Highlights
- DID management (create/read), Protobuf-based storage, chainstate reads
- On-chain storage for telemetry/config (JSON-friendly)
- Keystore-backed wallets with optional encryption
- Confirmation modes and status callbacks
- Clean imports: `from peaq_robot import PeaqRobot`

## Install

From this repo (monorepo-style):
```bash
cd packages/python
pip install -r requirements.txt
pip install -e .
```

From TestPyPI (resolve deps from PyPI):
```bash
python -m venv .venv && source .venv/bin/activate
pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple --pre -U peaq-robotics-sdk
```
Note: Python 3.8–3.12 are supported. Python 3.13 is currently not supported due to upstream wheel availability.

## Wallets and Keystore
- Default keystore location: `~/.peaq_robot/wallet.json`
- Override path: `PEAQ_ROBOT_KEYSTORE=/custom/path.json`
- Optional encryption: set `PEAQ_ROBOT_KEY_PASSWORD` to encrypt the keystore with Fernet+PBKDF2

Create or load automatically:
```python
from peaq_robot import PeaqRobot
robot = PeaqRobot()            # loads from keystore or creates on first run
print(robot.address)
```

Generate a fresh wallet and persist to keystore:
```python
robot = PeaqRobot.create_wallet()
```

Use explicit keys (won’t be stored unless you call create_wallet):
```python
PeaqRobot(mnemonic="..."), PeaqRobot(private_key="0x...")
```

## Network selection
The SDK resolves a network URL for you:
- Default testnet (Agung): `wss://peaq-agung.api.onfinality.io/ws`
- Aliases: `"agung"|"test"|"testnet"` → Agung; `"peaq"|"main"|"mainnet"` → `wss://quicknode3.peaq.xyz`
- HTTPS QuickNode converts to WSS automatically

```python
from peaq_robot import PeaqRobot
robot = PeaqRobot(network="peaq")          # mainnet quicknode3
robot = PeaqRobot(network="wss://...")     # custom WSS
```

## Transactions: confirmation modes and callbacks
Types are in `peaq_robot.types`:
- `ConfirmationMode`: `FAST` | `FINAL`
- `TxOptions(mode=...)`
- `TransactionStatus`: `BROADCAST` | `IN_BLOCK` | `FINALIZED`
- `TransactionStatusCallback` (Pydantic model)

Write methods accept optional `tx_options` and `on_status`:
```python
from peaq_robot.types import TxOptions, ConfirmationMode

# FAST (default): returns tx-hash string
tx = robot.store.add_data("LOG", {"ok": True})

# FINAL: returns SubstrateSendResult with finalize awaitable; emits status callbacks
def on_status(s):
    print(s.model_dump())

res = robot.store.add_data(
    "LOG2", {"ok": True},
    tx_options=TxOptions(mode=ConfirmationMode.FINAL),
    on_status=on_status,
)
final_receipt = asyncio.run(res.finalize)
```

## DID (identity)
Create (idempotent friendly) and read:
```python
name = f"did:peaq:{robot.address}"
try:
    robot.id.create_identity(name=name)   # returns hash (FAST)
except Exception as e:
    # For duplicates, you might get AttributeAlreadyExist
    if "AttributeAlreadyExist" in str(e):
        pass

doc = robot.id.read_identity()
print(doc["decoded_data"])  # parsed protobuf
```

## Storage
```python
robot.store.add_data("TELEMETRY_001", {"battery": 87.3})
print(robot.store.read_data("TELEMETRY_001"))
```

## Access
Access management provides roles, permissions, and assignments.
```python
# Create role and permission, assign permission to role, grant role to user
role_tx = robot.access.create_role("ROBOT_OPERATOR", "Operator role")
perm_tx = robot.access.create_permission("ROBOT_CONTROL", "Control permission")
assign_tx = robot.access.assign_permission_to_role("ROBOT_CONTROL", "ROBOT_OPERATOR")
grant_tx = robot.access.grant_role("ROBOT_OPERATOR", "USER_123")

# Read role (best-effort)
role_info = robot.access.read_role("ROBOT_OPERATOR")
print(role_info)
```

## Demos and examples
- `examples/wallet_demo.py`: end-to-end flow
  - Set a local funder mnemonic in `examples/.env`:
    - `PEAQ_ROBOT_FUND_MNEMONIC="abandon ... about"`
  - Run: `python examples/wallet_demo.py`
- `examples/options_test.py`: exercises FAST/FINAL modes and callbacks

## Project layout
```
packages/
  python/
    peaq_robot/           # SDK implementation
    README.md             # package README for PyPI
    setup.py, requirements.txt, pytest.ini
examples/
  wallet_demo.py
  options_test.py
```

## Robotics wrappers
- `peaq_robot.robotics.IdentityService` – thin facade over `RobotIdentity`
- `peaq_robot.robotics.DataVault` – thin facade over `RobotStorage`

## Development
```bash
python3 -m venv .venv && source .venv/bin/activate
cd packages/python
pip install -r requirements.txt
pip install -e .
cd ../../
python examples/wallet_demo.py
```

## Contributing
1. Keep public APIs stable and backwards compatible
2. Add examples/tests for new options

## License
MIT

## Style
- Classes: PascalCase (e.g., `PeaqRobot`)
- Modules/packages: lowercase (e.g., `peaq_robot`)
- Methods/functions: snake_case