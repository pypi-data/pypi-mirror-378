# 🌟 ModXPy — The Python Module Universe at Your Fingertips 🌟

Welcome to **ModXPy**, the ultimate playground for Python’s modules.  
With ModXPy you can instantly import, explore, and experiment with the entire Python standard library — plus any installed third-party modules — all from one simple interface.

---

## 🚀 Installation

Install directly from PyPI:

```bash
pip install modxpy

In Python, import as import modx (not modxpy)


Functions: 


import_all()

Imports about every standard library module at once.

🔹 import_random(n)

Imports n random modules from the standard library.

🔹 import_letter(letter)

Imports all standard library modules whose names start with the given letter.

🔹 import_external()

Attempts to import every third-party module you currently have installed.

🔹 import_screen()

Imports every module that uses a screen/GUI (like pygame or turtle).

🔹 list_importall()

Returns a list of modules that would be imported by import_all().

🔹 modules_loaded()

Shows how many modules you currently have downloaded on your device.

🔹 imported()

Lists the modules imported since ModX loaded (user + ModX), including dependencies.

🔹 modximported()

Lists the modules that were ONLY imported by ModX, NOT including user imports
and dependencies.


Example Code:


>>> import modx
>>> modx.imported()
Modules imported after ModX load (user + ModX):
Total modules imported after ModX load: 0

>>> modx.import_random(5)
['csv', 'wave', 'tarfile', 'turtle', 'contextlib']

>>> modx.imported()
Modules imported after ModX load (user + ModX):
- csv
- wave
- tarfile
- turtle
- contextlib

Total modules imported after ModX load: 5



💡 Why Use ModX?



Explore the Python standard library in seconds

Stress-test your environment by bulk importing modules

See hidden dependencies that load behind the scenes

Experiment with random imports for fun or testing

Discover new modules you didn’t know existed


ModXPy turns Python’s module system into a playground — 
perfect for learning, testing, or just satisfying your curiosity.
Install it today with pip install modxpy, import it with import modx,
and start discovering how many modules Python already has waiting for you!
