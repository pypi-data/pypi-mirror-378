````markdown
# PyFileManager

**PyFileManager** is a lightweight Python 3 project that provides a unified interface for managing file operations through a simple, command-line-style programming model. It integrates functionality such as binary file handling, base64 encoding/decoding, cryptography (via Fernet), and lightweight socket-based file serving—all wrapped in a minimal, modular Python package.

---

## ✨ Features

- 📁 Stream reading/writing for files
- 📦 Binary file operations
- 🔐 Fernet-based encryption and decryption
- 🔤 Base64 encoding/decoding
- 🌐 Lightweight HTTP file server
- ⚡ Unified and efficient I/O interface
- ✅ Compatible with Python 2 and 3 (streamlined through IO abstraction)
- 🖥️ Designed for one-liner command-style operations

---

## 📦 Installation

```bash
pip install ostream-manager==2.0
````

---

## 🧰 Usage Overview

All features are accessed via modules within the `stream_manager` package.

### 📄 Stream File I/O

```python
import stream_manager.io as IO

# Write to a file
writer = IO.OpenWriter("example.txt", "Hello, World!")

# Read from a file
reader = IO.OpenReader("example.txt")
print(reader)  # Output: Hello, World!
```

### 💾 Binary File Handling

```python
import stream_manager.binary as BINARY

# Write binary data
binary_writer = BINARY.OpenBinaryWriter("example.bin", b"\x00\x01\x02")

# Read binary data
binary_reader = BINARY.OpenBinaryReader("example.bin")
print(binary_reader)
```

### 🔤 Base64 Encoding/Decoding

```python
import stream_manager.base64 as BASE64

# Encode and write Base64 content
b64_writer = BASE64.OpenBase64Writer("encoded.b64", "Some text to encode")

# Read and decode Base64 content
b64_reader = BASE64.OpenBase64Reader("encoded.b64")
print(b64_reader)
```

### 🔐 Cryptography with Fernet

```python
import stream_manager.cripto as CRIPTO

# Generate encryption key
key = CRIPTO.GenerateCriptoKey()

# Encrypt content
encrypted = CRIPTO.CriptographyContent("Secret Message", key)

# Decrypt content
decrypted = CRIPTO.Uncripto(encrypted, key)
print(decrypted)  # Output: Secret Message
```

### 🌍 File Server via HTTP

```python
import stream_manager.server as SERVER

# Serve a file on localhost
SERVER.OpenFileServer("localhost", 80, "example.txt")

# Access from browser or curl: http://localhost:80/example.txt
```

---

## 🗂 Examples

You can find practical usage examples inside the module:

```python
import stream_manager.examples
```

---

## 📚 Documentation & Manual Reference

The core functionality is structured as:

| Feature      | Module                  | Method                                                       |
| ------------ | ----------------------- | ------------------------------------------------------------ |
| File I/O     | `stream_manager.io`     | `OpenWriter()`, `OpenReader()`                               |
| Binary I/O   | `stream_manager.binary` | `OpenBinaryWriter()`, `OpenBinaryReader()`                   |
| Base64 I/O   | `stream_manager.base64` | `OpenBase64Writer()`, `OpenBase64Reader()`                   |
| Cryptography | `stream_manager.cripto` | `GenerateCriptoKey()`, `CriptographyContent()`, `Uncripto()` |
| File Server  | `stream_manager.server` | `OpenFileServer()`                                           |

---

## 👤 Author

Developed by **asytrick**
📧 Email: [eusmool@gmail.com](mailto:eusmool@gmail.com)

---

## 📖 License

CREATIVE COMMONS ZERO LICENSE

---

## 💡 Notes

* Optimized for use in command-line or bash environments.
* Encourages low-latency file operations with minimal setup.
* Built to streamline file management operations in a Pythonic way.

---

