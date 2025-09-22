# pyglow

![Python](https://img.shields.io/pypi/pyversions/pyglowx)
[![PyPI Version](https://img.shields.io/pypi/v/pyglowx)](https://pypi.org/project/pyglowx/)
[![PyPI Downloads](https://static.pepy.tech/badge/pyglowx)](https://pepy.tech/projects/pyglowx)

![GitHub Repo stars](https://img.shields.io/github/stars/BirukBelihu/pyglow)
![GitHub forks](https://img.shields.io/github/forks/BirukBelihu/pyglow)
![GitHub issues](https://img.shields.io/github/issues/BirukBelihu/pyglow)
![GitHub License](https://img.shields.io/github/license/birukbelihu/neovibe-vscode)

**pyglow** is a lightweight, feature rich, cross-platform, markdown-style console output formatter library for python.

---
GitHub: [pyglow](https://github.com/BirukBelihu/pyglow)
---

## ✨ Features

- 💻**Cross platform** (**Windows**, **Linux**, **macOS**)
- ✅ **Markdown-style tags**: `[red]`, `[green bold]`, `[italic underline]`
- 🎨 **Foreground & background colors** with support for custom rgb(235, 64, 52) & hexadecimal colors(#EB4034) along with some predefined ANSI colors
- 🪄 **Text styles**: `bold`, `dim`, `italic`, `underline`, `blink` & more
- 🏞️ **Views**: `Panel`, `Progressbar`, `Spinner` & `Table` & more
- 🔗 **Hyperlink support**
- 🔄 **Nested tag support**
- 🔡 Case insensitive tag names(Bold, bold, BOLD).
- 💡 Suggest the closest match of misspelt tag names(If available).

---

### Screenshots

|      ![pyglow sample 1](https://github.com/birukbelihu/pyglow/raw/master/samples/sample_1.png)      |   ![pyglow sample 2](https://github.com/birukbelihu/pyglow/raw/master/samples/sample_2.png)   |
|:---------------------------------------------------------------------------------------------------:|:---------------------------------------------------------------------------------------------:|
|                                                                                                     |                                                                                               |
|      ![pyglow sample 3](https://github.com/birukbelihu/pyglow/raw/master/samples/sample_3.png)      |   ![pyglow sample 4](https://github.com/birukbelihu/pyglow/raw/master/samples/sample_4.png)   |
|                                                                                                     |                                                                                               |
|      ![pyglow sample 5](https://github.com/birukbelihu/pyglow/raw/master/samples/sample_5.png)      |   ![pyglow sample 6](https://github.com/birukbelihu/pyglow/raw/master/samples/sample_6.png)   |
|                                                                                                     |                                                                                               |
|      ![pyglow sample 7](https://github.com/birukbelihu/pyglow/raw/master/samples/sample_7.png)      |   ![pyglow sample 8](https://github.com/birukbelihu/pyglow/raw/master/samples/sample_8.png)   |
|      ![pyglow sample 9](https://github.com/birukbelihu/pyglow/raw/master/samples/sample_9.png)      |  ![pyglow sample 10](https://github.com/birukbelihu/pyglow/raw/master/samples/sample_10.png)  |

## 📦 Installation

```
pip install pyglowx
```

You can also install pyglow from source code. source code may not be stable, but it will have the latest features and
bug fixes.

Clone the repository:

```
git clone https://github.com/birukbelihu/pyglow.git
```

Go inside the project directory:

```bash
cd pyglow
```

Install pyglow:

```
pip install -e .
```

---

> [!TIP]
> On PyPI, the package name is **`pyglowx`** because **`pyglow`** was already taken.  
> However, once installed you can simply import it as:
> ```python
> from pyglow.pyglow import Glow
> ```

## 🧠 Example Usage

```python
from pyglow.pyglow import Glow

Glow.print(
    "[cyan bold][link=https://github.com/birukbelihu/pyglow]pyglow[/][/] is a lightweight, [bold]markdown-style console subtitle formatter[/] library for Python. \nIt enables developers to output styled subtitle in the terminal using simple and readable tags like `[red bold]Error[/]`.")
```

### Output

![pyglow Output](https://github.com/birukbelihu/pyglow/raw/master/samples/sample_3.png)

### Running the examples

if you want to run the examples you can install pyglow stable or development version in your virtual environment & you can simply run them.

### Set up Python virtual environment(I recommend using [uv](https://github.com/astral-sh/uv) for lightning speed)

### With uv

```bash
uv venv .venv
```

### With Python

```bash
python -m venv .venv
```

# Activate virtual environment

```bash
.venv\Scripts\activate # On Windows
```

```bash
source .venv/bin/activate # On Linux, WSL & macOS
```

# Install pyglow

### With uv

```bash
uv pip install pyglowx
```

### With Python

```bash
pip install pyglowx
```

or install the dev version as described in this [section](#-installation) and run any example you want.

```bash
# Go inside the examples directory

cd examples
```

```bash
# Run any example you want

python hyperlink_example.py
python nested_tags_example.py
python panel_example.py
python progressbar_example.py
python spinner_example.py
python style_example.py
python table_example.py
python tags_example.py
python termpicker_example.py
```

---

## 📦 Library Overview

| Function                           | Description                                                                                                |
|------------------------------------|------------------------------------------------------------------------------------------------------------|
| `Glow.parse(str text)`             | Converts your markdown-style tags to ANSI-coded string                                                     |
| `Glow.print(str text)`             | Prints the text with the provided style                                                                    |
| `Glow.printc(str text)`            | Prints the text with the provided style with constants(Fore.BLUE, Back.GREEN, Style.BLINK) with auto reset |
| `Glow.prints(str text, str style)` | Prints the text with a provided style for the entire text                                                  |

---

## 📄 Demo & Documentation

Check out the [examples](https://github.com/birukbelihu/pyglow/raw/master/examples) for:

- ✅ Full usage examples
- ✅ Quickstart code snippets

---

## 🙌 Contribute

Want to improve `pyglow`? Contributions are welcome!

---

Shine bright in your terminal! 🚀

---

## 📄 License

This project is licensed under the **Apache License 2.0**. See
the [LICENSE](https://github.com/birukbelihu/pyglow/blob/master/LICENSE) file for details.