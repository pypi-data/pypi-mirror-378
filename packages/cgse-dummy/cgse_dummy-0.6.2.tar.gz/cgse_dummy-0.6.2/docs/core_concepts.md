# Core Concepts

This section introduces the fundamental concepts behind the CGSE-DUMMY project and its integration with the CGSE (Common-EGSE) framework. Understanding these concepts will help you effectively use, extend, and adapt the dummy device driver for your own projects.

## Device Driver Architecture in CGSE

The CGSE framework is designed to support modular, extensible device drivers that communicate with hardware or simulated devices. Each device driver typically consists of:

- **Control Server**: Manages communication between the CGSE core and the device driver. It receives commands, dispatches them to the device, and returns responses.
- **Device Driver**: Implements the logic for interacting with the device (real or simulated). It processes commands, manages device state, and handles data acquisition.
- **Simulator**: (Optional) Provides simulated device behavior for development and testing without real hardware.

The CGSE-DUMMY project provides both synchronous and asynchronous implementations of these components, allowing you to explore different concurrency models.

## Synchronous vs. Asynchronous Drivers

- **Synchronous Drivers**: Handle one command at a time, blocking until the operation completes. This model is simple and easy to reason about, but may not scale well for high-throughput or latency-sensitive applications.
- **Asynchronous Drivers**: Use Python's `asyncio` to handle multiple commands concurrently. In practice, commands that interact directly with hardware are usually executed one at a time to ensure device safety and integrity. However, many other operations—such as status queries, configuration changes, or simulated data acquisition—can be processed in parallel. This means the driver can remain responsive to new requests, even while a long-running operation is underway. Asynchronous drivers are more complex to implement, but they enable efficient, non-blocking I/O and allow the system to serve multiple clients or tasks simultaneously, making them well-suited for demanding or interactive environments.

In CGSE-DUMMY:

- `dummy_cs.py` and `dummy_dev.py` implement the synchronous control server and device driver.
- `dummy_acs.py` and `dummy_adev.py` provide experimental asynchronous versions.

## Control Server vs. Device Simulator

- **Control Server**: Acts as the entry point for external commands (e.g., from the CGSE core or user interface). It parses commands, manages sessions, and forwards requests to the device driver.
- **Device Simulator**: Mimics the behavior of a real device, generating simulated data and responses. Useful for development, testing, and demonstration without requiring physical hardware.

In CGSE-DUMMY:

- The control server and device simulator can be run independently or together, depending on your testing needs.

## SCPI Protocol Basics

The Standard Commands for Programmable Instruments (SCPI) protocol is a widely used text-based command language for controlling test and measurement devices. CGSE-DUMMY uses a simplified SCPI-like protocol for communication between the control server and device driver.

### How the Simplified SCPI-like Protocol Works

- **Command Structure:** Commands are sent as ASCII strings, typically in the form `COMMAND[:SUBSYSTEM][?]` (e.g., `MEAS:VOLT?` to query voltage, `CONF:CURR 1.0` to set current).
- **Queries and Settings:** Commands ending with `?` are queries; others are settings or actions. The protocol supports both types.
- **Parsing and Decoding:** The implementation uses Python functions to decode and encode command arguments and responses (e.g., for on/off states, numeric arrays, or device identification strings). This makes it easy to handle different data types and formats.
- **Extensibility:** Each command can have associated translation functions for getting or setting values, allowing flexible and modular command handling.
- **Differences from Full SCPI:** The protocol is intentionally simpler than the full SCPI standard. It may not support all SCPI features, such as deeply nested command trees, all standard commands, or a full error/event queue. Instead, it focuses on the most common use cases for device simulation and testing.

#### Example Commands

- Query device identification: `*IDN?` → `ACME,MODEL123,123456,1.0`
- Set output state: `OUTP ON` → `ON`
- Query measurement: `MEAS:VOLT?` → `3.1415`

### Suggestions for Improvement

- **Increase SCPI Compliance:** Add support for more hierarchical commands, standard error/event queues, and flexible query syntax.
- **Robust Parsing:** Use more advanced parsing techniques to handle complex commands and argument validation.
- **Extensibility:** Provide a registry or decorator-based system for adding new commands and handlers.
- **Documentation:** Auto-generate command documentation and provide a `HELP` command for discoverability.
- **Testing:** Expand unit tests for command parsing, dispatch, and error handling.

By iteratively improving these aspects, you can make the protocol more robust, extensible, and user-friendly, while still keeping it lightweight for simulation and development purposes.

---

Next: [Usage Examples](./usage_examples.md)
