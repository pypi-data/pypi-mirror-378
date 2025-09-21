# � CTFUtils
> *Tu arsenal definitivo para dominar CTFs*

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Tests](https://img.shields.io/badge/Tests-21%2F21%20%E2%9C%85-brightgreen)](tests/)
[![CTF Ready](https://img.shields.io/badge/CTF-Ready-red.svg)](#)

*¿Cansado de googlear herramientas CTF? ¡CTFUtils tiene todo lo que necesitas!*

[🚀 Instalación](#-instalación-rápida) • 
[⚡ Inicio Rápido](#-inicio-rápido) • 
[🎯 Ejemplos](#-ejemplos) • 
[� Documentación](#-documentación)

</div>

---

## 🎯 ¿Por qué CTFUtils?

**Antes:** "¿Dónde está mi script de Caesar cipher? ¿Cómo se hace LSB steganography otra vez?"

**Después:** 
```python
from ctfutils import *
CaesarCipher().brute_force("WKLV LV HQFUBSWHG")  # ¡Boom! 💥
```

✅ **4 módulos completos** - Crypto, Forensics, Stego, Misc  
✅ **21 tests pasando** - Código confiable  
✅ **Ejemplos reales** - Casos de CTFs auténticos  
✅ **POO moderno** - Fácil de usar y extender

## 🚀 Instalación Rápida

```bash
# Clona el repo
git clone https://github.com/Oxidizerhack/ctfutils.git
cd ctfutils

# Instala y listo
pip install -e .
```

## ⚡ Inicio Rápido

```python
# Crypto: Rompe Caesar en una línea
from ctfutils.crypto.classical import CaesarCipher
cipher = CaesarCipher()
cipher.brute_force("KHOOR ZRUOG")  # Encuentra "HELLO WORLD"

# Stego: Oculta mensajes como un ninja
from ctfutils.stego.text import ZeroWidthSteganography
stego = ZeroWidthSteganography()
hidden = stego.encode("public text", "FLAG{hidden}")

# Forensics: Analiza archivos sospechosos
from ctfutils.forensics.files import FileAnalyzer  
analyzer = FileAnalyzer()
analyzer.get_file_signature(binary_data)  # "PNG Image"

# Misc: Convierte todo a todo
from ctfutils.misc.converters import NumberConverter
conv = NumberConverter()
conv.decimal_to_binary(1337)  # "10100111001"
```
## �️ Arsenal Completo

| 🔐 **Crypto** | 🔍 **Forensics** | 🖼️ **Stego** | 🔧 **Misc** |
|---------------|------------------|---------------|--------------|
| Caesar Cipher | File Analysis | Text Hiding | Base Conversion |
| Vigenère Cipher | Memory Dumps | Image LSB | String Manipulation |
| Hash Cracking | Network Logs | Zero-Width | Encoding/Decoding |
| Modern Crypto | Binary Analysis | Audio Stego | Math Utils |

<details>
<summary>🎯 <strong>Ver todos los módulos</strong></summary>

### 🔐 Crypto (`ctfutils.crypto`)
- **classical.py**: `CaesarCipher`, `VigenereCipher`
- **modern.py**: Base64, XOR, algoritmos modernos
- **hashing.py**: `HashAnalyzer` para MD5, SHA, etc.

### 🔍 Forensics (`ctfutils.forensics`) 
- **files.py**: `FileAnalyzer` para análisis binario
- **memory.py**: `MemoryAnalyzer` para dumps
- **network.py**: `NetworkAnalyzer` para logs

### 🖼️ Stego (`ctfutils.stego`)
- **text.py**: `ZeroWidthSteganography`, espacios ocultos
- **image.py**: `ImageSteganography` LSB 
- **audio.py**: Análisis de audio

### 🔧 Misc (`ctfutils.misc`)
- **converters.py**: `NumberConverter`, `TextConverter`
- **utils.py**: `StringManipulator`
</details>

## 🎯 Ejemplos

### � Caesar Cipher Brute Force
```python
from ctfutils.crypto.classical import CaesarCipher

# Mensaje interceptado en CTF
encrypted = "WKLV LV D VHFUHW PHVVDJH"

# Rompe el cipher automáticamente 
cipher = CaesarCipher()
solutions = cipher.brute_force(encrypted)

# Encuentra "THIS IS A SECRET MESSAGE"
print(solutions[3])  # ¡Boom! 💥
```

### 🕵️ Análisis Forense Express
```python
from ctfutils.forensics.files import FileAnalyzer

# Archivo sospechoso
mystery_file = b"\x89PNG\r\n\x1a\n...hidden_flag..."

analyzer = FileAnalyzer()
file_type = analyzer.get_file_signature(mystery_file)  # "PNG Image"
strings = analyzer.extract_strings(mystery_file)       # ["hidden_flag"]
```

### 🥷 Esteganografía Ninja
```python
from ctfutils.stego.text import ZeroWidthSteganography

# Oculta un flag en texto visible
stego = ZeroWidthSteganography() 
hidden_text = stego.encode("Normal text", "FLAG{invisible}")

# Nadie sospecha nada... 😏
print(hidden_text)  # "Normal text" (pero con el flag oculto)

# Extrae el flag
flag = stego.decode(hidden_text)  # "FLAG{invisible}"
```

## 🧪 Testing

Código confiable con **21 tests pasando**:

```bash
# Corre todos los tests
python -m pytest tests/ -v

# Ver cobertura
python -m pytest tests/ --cov=ctfutils
```

<details>
<summary>📊 <strong>Ver results de tests</strong></summary>

```
tests/test_crypto.py::test_caesar_cipher ✓
tests/test_crypto.py::test_vigenere_cipher ✓  
tests/test_crypto.py::test_hash_functions ✓
tests/test_misc.py::test_number_conversions ✓
tests/test_misc.py::test_text_manipulations ✓
... (16 tests más) ✓

======================== 21 passed in 0.13s ========================
```

</details>

## 📚 Documentación

- **[Ejemplos Prácticos](docs/examples/)** - Casos reales de CTF
- **[API Reference](ctfutils/)** - Documentación completa
- **[Guías de Uso](docs/)** - Tutoriales paso a paso

## 🤝 Contribuir

¿Encontraste un bug? ¿Tienes una idea genial?

```bash
# Fork, clone, código, commit, push, PR
git clone https://github.com/Oxidizerhack/Pgr2_Practica7.git
cd ctfutils
# Haz tu magia ✨
git commit -m "feat: nueva herramienta épica"
```


<div align="center">

**Construido con ❤️ para la comunidad CTF**

[📧 Contacto](gmail:jhonnyantoquispe@gmail.com) • 
[🐛 Issues](https://github.com/Oxidizerhack/ctfutils/issues) • 
[💡 Features](https://github.com/Oxidizerhack/ctfutils/discussions)

*Licencia MIT - Úsalo, modifícalo, compártelo*

</div>