# mpl-makefig
Tools for making standardized figures with a command line interface.

## Provides
- A simple command line interface for displaying or saving figures produced
  using matplotlib.
- Functions to calculate 'good' figure sizes for use in LaTeX or other
  documents, and to make figures using these sizes.

## How to use
To use the command line interface, the basic procedure is as follows (see also
the example at the end of this docstring):

- For each figure you want to make, define a function that makes the figure and
  all of its contents, and returns the `matplotlib.figure.Figure` object. This
  function should have no required parameters, though optional parameters are no
  problem.
- To add a figure to the command line interface, annotate the function with the
  make function from this module.
- When you want to invoke the command line interface, e.g. in a script, call
  `parse_args_make_figs()`.
- Command line usage:

  `script [-h|--help] [save|nosave] [figurename [anotherfigure [...]]]`
  - If the first agument is `save` or `nosave`, the default save/display
    behavior will be overridden.
  - If figure-making function names are listed on the command line, only those
    figures will be made, otherwise all figures will be made.

The other functionality in this module is mainly related to producing figures
with specific sizes intended to fit well into LaTeX, or other, documents. This
is done using the functions standard_figsize, standard_figure, and
standard_subplots, which take arguments (among others, see docstrings),
specifying figure sizes in convenient units, rather than just inches, as is the
case with matplotlib. The available units, their descriptions, and their lengths
in inches are stored in the `UNITS` dictionary. These include some common lengths
used in LaTeX documents, but any length can be specified. To find the width or
height of a text area in a LaTeX document, the following procedure is useful:

- In the relevant place in the LaTeX source code, write one of the following:
  - `\showthe\linewidth` 
  - `\showthe\textheight`
- Compile the document with `pdflatex`. Some other programs that automate the
  document-compillation process may hide or mangle the relevant output, so it's
  probably best to run pdflatex directly.
- Compillation will stop when the `\showthe` command is encountered, and the
  relevant length will be printed in units of `pt`.

A note on beamer usage: When making a multi-column slide, and setting column
widths using `\column{XX\textwidth}`, the resulting `\linewidth` in the column
is `XX` times the full-page linewidth, so `beamer_169_width` can be used, with the
appropriate scaling factor.

## Notable Functions and Variables 
- `UNITS`: 
  - Dictionary mapping various lenght units to floats representing inch
  measurements. These units can be used with `standard_figsize` and related
  functions.
- `make`:
  - Decorator to use with a figure-making function to add it to the command line
  interface invoked with `parse_args_make_figs`.
- `verbose`:
  - Decorator to provide text output indicating which function is running.
- `standard_figsize`:
  - Calculate a figure size, e.g. for use with the figsize parameter of
  `matplotlib.pyplot.figure`, based on common/standard length scales and aspect
  ratios.
- `standard_figure`:
  - Produce a `matplotlib.figure.Figure` using `standard_figsize` to decide the size.
- `standard_subplots`:
  - Produce a figure with axes like `matplotlib.pyplot.subplots`, using
  `standard_figsize` to decide the size.
- `parse_args_make_figs`:
  - Invoke a simple command line interface to display or save all or some figures
  decorated with `make`.

## Example Script 
```python 
import makefig

def some_function():
    # this function will not be added to FIGURES_REGISTRY
    ...

@makefig.make      # Adds this function to FIGURES_REGISTRY
def figure_name():
    # Do whatever is necessary to produce a figure, e.g.:
    fig, ax = makefig.standard_subplots()
    ax.plot([0, 1, 2], [2, 4, 8])
    return fig

if __name__ == '__main__':
    makefig.parse_args_make_figs()
```
