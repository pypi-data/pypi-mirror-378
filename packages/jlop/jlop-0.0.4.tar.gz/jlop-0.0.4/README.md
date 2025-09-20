# JLoP

<p align="center">
<img src="logo/jlop_logo_final.png" alt="GraviPy Logo" width="60%">
</p>

**J**ust **LO**vely  **P**lots is a Python package that offers a a quick and easy way of making publication quality plots.

## Instalation

The package can be installed directly from pip

```bash
pip install jlop
```

## Usage

To use the packagage, just import it and load your desired style.

```python
import jlop
jlop.set_style('modern')
```

The current avaliable styles are

- `modern` (default)
- `classic`
- `retro`
- `futuristic`
- `handwritten`

## Known Issues

In some machines, for the Latex rendering to work, the following packages might need to be installed:

- `texlive` 
- `texlive-latex-extra` 
- `dvipng`
- `cm-super`
