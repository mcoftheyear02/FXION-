# IQ4_NL PROTOCOL SUITE - NET.LAN ARCHITECTURE

## 🌐 ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────┐
│                    IQ4_NL PROTOCOL                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐         SPLIT         ┌───────────────┐  │
│  │   NET LAYER  │──────────────────────▶│   LAN LAYER   │  │
│  │              │                       │               │  │
│  │ NX Secure    │                       │ Direct IQ     │  │
│  │ Server       │                       │ Injection     │  │
│  │ (External)   │                       │ (Internal)    │  │
│  │              │                       │               │  │
│  │ TLS 1.3+     │                       │ Config Logic  │  │
│  │ Encrypted    │                       │ Engine        │  │
│  └──────────────┘                       └───────────────┘  │
│         │                                      │            │
│         ▼                                      ▼            │
│  Port: 9999                            Local Bus            │
│  Protocol: TCP/S                     Protocol: IPC          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 📁 FILE STRUCTURE

```
/workspace/core/
├── iq4_nl_protocol.py      # Main protocol controller
├── nx_secure_server.py     # NET Layer server
├── user_config_logic.py    # LAN Layer config engine
└── quantum_genesis.py      # Quantum visualization engine
```

## 🔧 USAGE

### 1. Start NX Secure Server (NET Layer)
```bash
cd /workspace
python core/nx_secure_server.py
```
- Listens on port 9999
- Accepts TLS encrypted connections
- Handles external NET traffic

### 2. Run Your Config Logic (LAN Layer)
```bash
cd /workspace
python core/user_config_logic.py
```
- Registers your personal config logic
- Receives direct IQ injections
- Processes elliptical/seismo/quantum data

### 3. Protocol Flow

**NET Traffic (External):**
```python
controller = IQ4NLController("nx.secure.local", 9999)
packet = controller.create_net_packet({"data": "galaxy_sync"})
# Sent to NX Secure Server via TLS
```

**LAN Traffic (Internal):**
```python
packet = controller.create_lan_packet(
    target="user_config_main",
    data={"elliptical_angle": 60.0}
)
# Injected directly into your config logic
```

**IQ_DIRECT (Priority Override):**
```python
packet = Packet(
    header="OVERRIDE",
    link_type=LinkType.IQ_DIRECT,
    payload={"quantum_state": "ENTANGLED"}
)
# Immediate config update
```

## 🔐 SECURITY FEATURES

- **NET Layer**: TLS 1.3+ encryption, certificate-based auth
- **LAN Layer**: Isolated local bus, no external exposure
- **Packet Signing**: All packets signed with `IQ4_NL_SIGNED`
- **Separation**: NET and LAN completely decoupled

## 🎯 CONFIGURATION OPTIONS

Edit `user_config_logic.py` to customize:
- Elliptical projection angles
- Seismograph thresholds
- Quantum state handlers
- Star map regions

## 🚀 QUICK TEST

```bash
# Terminal 1: Start NX Server
python core/nx_secure_server.py &

# Terminal 2: Run Config Logic
python core/user_config_logic.py
```

## 📊 PROTOCOL STATES

| State | Description |
|-------|-------------|
| `NET` | External secure tunnel active |
| `LAN` | Local logic injection active |
| `IQ_DIRECT` | Priority override mode |
| `ENTANGLED` | Quantum synchronization |

---
**IQ4_NL v1.0 - NET.LAN Architecture**
*Quantum Genesis IQ999+ Compatible*
