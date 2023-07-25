"""Tools for making standardized figures with a command line interface.

Provides
--------
- A simple command line interface for displaying or saving figures produced
  using matplotlib.
- Functions to calculate 'good' figure sizes for use in LaTeX or other
  documents, and to make figures using these sizes.

How to use
----------
To use the command line interface, the basic procedure is as follows (see also
the example at the end of this docstring):
- For each figure you want to make, define a function that makes the figure and
  all of its contents, and returns the matplotlib.figure.Figure object. This
  function should have no required parameters, though optional parameters are no
  problem.
- To add a figure to the command line interface, annotate the function with the
  make function from this module.
- When you want to invoke the command line interface, e.g. in a script, call
  parse_args_make_figs().
- Command line usage:
  > script [-h|--help] [save|nosave] [figurename [anotherfigure [...]]]
  - If the first agument is 'save' or 'nosave', the default save/display
    behavior will be overridden.
  - If figure-making function names are listed on the command line, only those
    figures will be made, otherwise all figures will be made.

The other functionality in this module is mainly related to producing figures
with specific sizes intended to fit well into LaTeX, or other, documents. This
is done using the functions standard_figsize, standard_figure, and
standard_subplots, which take arguments (among others, see docstrings),
specifying figure sizes in convenient units, rather than just inches, as is the
case with matplotlib. The available units, their descriptions, and their lengths
in inches are stored in the UNITS dictionary. These include some common lengths
used in LaTeX documents, but any length can be specified. To find the width or
height of a text area in a LaTeX document, the following procedure is useful:
- In the relevant place in the LaTeX source code, write one of the following:
  - \\showthe\\linewidth
  - \\showthe\\textheight
- Compile the document with pdflatex. Some other programs that automate the
  document-compillation process may hide or mangle the relevant output, so it's
  probably best to run pdflatex directly.
- Compillation will stop when the \\showthe command is encountered, and the
  relevant length will be printed in units of pt.

A note on beamer usage: When making a multi-column slide, and setting column
widths using `\\column{XX\\textwidth}`, the resulting \\linewidth in the column
is XX times the full-page linewidth, so beamer_169_width can be used, with the
appropriate scaling factor.

Notable Functions and Variables
-------------------
- UNITS:
  Dictionary mapping various lenght units to floats representing inch
  measurements. These units can be used with standard_figsize and related
  functions.
- make:
  Decorator to use with a figure-making function to add it to the command line
  interface invoked with parse_args_make_figs.
- verbose:
  Decorator to provide text output indicating which function is running.
- standard_figsize:
  Calculate a figure size, e.g. for use with the figsize parameter of
  matplotlib.pyplot.figure, based on common/standard length scales and aspect
  ratios.
- standard_figure:
  Produce a matplotlib.figure.Figure using standard_figsize to decide the size.
- standard_subplots:
  Produce a figure with axes like matplotlib.pyplot.subplots, using
  standard_figsize to decide the size.
- parse_args_make_figs:
  Invoke a simple command line interface to display or save all or some figures
  decorated with make.

Example Script
--------------
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
"""

import sys
import os
import functools
import matplotlib as mpl
import matplotlib.pyplot as plt

FIGURES_REGISTRY = {}

GOLDEN = (5**0.5 + 1) / 2  # Golden ratio ('good' aspect ratio)

UNITS = {
    'pt': {
        'inches': 1 / 72.27,
        'description': 'LaTeX point. Not quite the same as a printer\'s point.'
    },
    'cm': {
        'inches': 1 / 2.54,
        'description': 'Centimeter'
    },
    'mm': {
        'inches': 1 / 25.4,
        'description': 'Millimeter'
    },
    'in': {
        'inches': 1.,
        'description': 'Inch'
    },
    'standard_text_width': {
        'inches': 6.5,
        'description': 'Reasonable width based on published scientific docs.'
    },
    'standard_text_height': {
        'inches': 6.5 / GOLDEN,
        'description': 'Reasonable height based on published scientific docs.'
    },
    'beamer_ar169_width': {
        'inches': 5.511811263318113,
        'description': '\\documentclass[aspectratio=169]{beamer} \\linewidth'
    },
    'beamer_ar169_height': {
        'inches': 3.3893697246436973,
        'description': '\\documentclass[aspectratio=169]{beamer} \\textheight'
    },
    'tex_letter_width': {
        'inches': 4.77376504773765,
        'description': '\\documentclass{article} \\linewidth, letter paper'
    },
    'tex_letter_height': {
        'inches': 7.610350076103501,
        'description': '\\documentclass{article} \\textheight, letter paper'
    },
    'tex_letter_twocol_width': {
        'inches':
            3.1755915317559156,
        'description':
            '\\documentclass[twocolumn]{article} \\linewidth, letter paper'
    },
    'tex_letter_twocol_height': {
        'inches':
            7.610350076103501,
        'description':
            '\\documentclass[twocolumn]{article} \\textheight, letter paper'
    },
}


def make(figfunc):
    """Decorator that registers a figure function for CLI use.

    Notes
    -----
    Decorating a function with this decorator will register it in a dictionary
    (FIGURES_REGISTRY) that is (by default) used with parse_args, make_figs, and
    parse_args_make_figs to implement a simple command line interface.

    See also
    --------
    parse_args:
        Parse command line arguments for use with make_figs
    make_figs:
        Make figures, optionally saving them or showing them.
    parse_args_make_figs:
        Parse command line arguments and make figures in the default way.
    """
    FIGURES_REGISTRY[figfunc.__name__] = figfunc
    return figfunc


def verbose(figfunc):
    """Decorator that prints info about the decorated function when it runs.

    The name of the function is printed, followed by the first line of the
    docstring if it exists. When the function exits, this is also indicated.
    """

    @functools.wraps(figfunc)
    def wrapper_verbose(*args, **kwargs):
        print(f'Processing: {figfunc.__name__}', end='')
        if figfunc.__doc__:
            shortdoc = figfunc.__doc__.split("\n", 1)[0]
        else:
            shortdoc = ''
        print(f' - {shortdoc}')
        fig = figfunc(*args, **kwargs)
        print('  Done')
        return fig

    return wrapper_verbose


def split_num_unit(string):
    """Split a string containing a number and a unit into a float and a string.

    Parameters
    ----------
    x : str
        A string containing an (optional) numeric part followed by a non-numeric
        part. The numeric part is considered to be any characters in the set
        '0123456789.-', and the string part is whatever is left over after
        removing the numeric part.

    Returns
    -------
    (num, unit) : (float, str)
        num is the numeric part of the string converted to a float. unit is the
        non-numeric suffix.
    """
    # WARN: This is probably not a very robust implementation, but it works in
    # the expected cases, and doesn't require any imports or verbose code.
    unit = string.translate(str.maketrans('', '', '0123456789.-'))
    try:
        num = float(string.removesuffix(unit))
    except ValueError:
        num = 1.
    return num, unit


def len2inch(string):
    """Convert a value+unit string to float inches.

    Parameters
    ----------
    string : str
        A string of the form NUMUNIT, where NUM is any collection of
        '0123456789.-' that can be converted to a float, and UNIT is any key of
        the dictionary UNITS.

    Returns
    -------
    x : float
        The length described by string, expressed in inches.

    Examples
    --------
    len2inch('2.54cm')  # 1.0
    len2inch('15pt')    # 0.2075...

    See also
    --------
    split_num_unit:
        Used for parsing the input into a float and a unit string.
    UNITS:
        Dictionary mapping unit strings to lengths in inches.
    """
    num, unit = split_num_unit(string)
    return num * UNITS[unit]['inches']


def standard_figsize(width=None, height=None, aspect=GOLDEN, nrows=1, ncols=1):
    """Calculate a 'good' figure size using convenient units and ratios.

    Parameters
    ----------
    width, height : optional, float or str
        Width and height of the figure. If given as a float, the units are
        assumed to be inches. If given as a string, it is converted to a float
        using len2inch. If neither are specified, width is set to
        matplotlib.rcParams['figure.figsize'][0], and height is determined from
        that using the values of aspect, nrows, and ncols. If width or height is
        specified without the other, the other is determined from the values of
        aspect, nrows, and ncols. If both are specified, they are used as the
        figure width and height, and the other arguments are ignored.
    aspect : optional, float
        The aspect ratio (width / height) of a single Axes in the figure. By
        default, this is the golden ratio (~ 1.62).
    nrows, ncols : optional, int
        Number of rows and columns of Axes expected to be used in the figure.
        These axes are not created, but the figure's aspect ratio is determined
        as 'aspect * ncols / nrows', so that the individual Axes have aspect
        ratios near the value of aspect (neglecting padding between axes).

    Returns
    -------
    (width_inches, height_inches) : (float, float)
        Figure width and height in inches.

    See also
    --------
    standard_figure:
        Wrapper on matplotlib.pyplot.figure using this function for the size.
    standard_subplots:
        Wrapper on matplotlib.pyplot.subplots using this function for the size
        and the number of rows and columns of Axes.
    """
    fig_aspect = aspect * ncols / nrows
    if not width and not height:
        width = mpl.rcParams['figure.figsize'][0]
        height = width / fig_aspect
    elif not height:
        if isinstance(width, str):
            width = len2inch(width)
        height = width / fig_aspect
    elif not width:
        if isinstance(height, str):
            height = len2inch(height)
        width = height * fig_aspect
    else:
        if isinstance(height, str):
            height = len2inch(height)
        if isinstance(width, str):
            width = len2inch(width)
    return width, height


def standard_figure(width=None,
                    height=None,
                    aspect=GOLDEN,
                    nrows=1,
                    ncols=1,
                    **kwargs):
    """Make a figure with a 'good' size using convenient units and ratios.

    Parameters
    ----------
    width, height : optional, float or str
        Width and height of the figure. If given as a float, the units are
        assumed to be inches. If given as a string, it is converted to a float
        using len2inch. See standard_figsize for more information.
    aspect : optional, float
        The aspect ratio (width / height) of a single Axes in the figure. By
        default, this is the golden ratio (~ 1.62).
    nrows, ncols : optional, int
        Number of rows and columns of Axes expected to be used in the figure.
        These axes are not created, but the figure's aspect ratio is determined
        as 'aspect * ncols / nrows', so that the individual Axes have aspect
        ratios near the value of aspect (neglecting padding between axes).
    **kwargs
        Other keyword arguments are passed to matplotlib.pyplot.figure 

    Returns
    -------
    fig : matplotlib.Figure.figure
        The created figure.

    See also
    --------
    standard_figsize:
        The function used for calculating the size of the figure.
    standard_subplots:
        Wrapper on matplotlib.pyplot.subplots using this function for the size
        and the number of rows and columns of Axes.
    """
    return plt.figure(figsize=standard_figsize(width, height, aspect, nrows,
                                               ncols),
                      **kwargs)


def standard_subplots(nrows=1,
                      ncols=1,
                      width=None,
                      height=None,
                      aspect=GOLDEN,
                      **kwargs):
    """Make a figure and some Axes with a 'good' size using convenient units.

    Parameters
    ----------
    width, height : optional, float or str
        Width and height of the figure. If given as a float, the units are
        assumed to be inches. If given as a string, it is converted to a float
        using len2inch. See standard_figsize for more information.
    aspect : optional, float
        The aspect ratio (width / height) of a single Axes in the figure. By
        default, this is the golden ratio (~ 1.62).
    nrows, ncols : optional, int
        Number of rows and columns of Axes expected to be used in the figure.
        These are passed to matplotlib.pyplot.subplots for creating the axes,
        and the figure's aspect ratio is determined as 'aspect * ncols / nrows',
        so that the individual Axes have aspect ratios near the value of aspect
        (neglecting padding between axes).
    **kwargs
        Other keyword arguments are passed to matplotlib.pyplot.figure 

    Returns
    -------
    fig : matplotlib.Figure.figure
        The created figure.
    ax : matplotlib.axes.Axes or array of Axes
        The created axes.

    See also
    --------
    standard_figsize:
        The function used for calculating the size of the figure.
    standard_subplots:
        Wrapper on matplotlib.pyplot.subplots using this function for the size
        and the number of rows and columns of Axes.
    Parameters
    ----------
    x : type
        Desc

    Returns
    -------
    x : type
        Desc

    See also
    --------
    standard_figsize:
        The function used for calculating the size of the figure.
    standard_figure:
        Wrapper on matplotlib.pyplot.figure using this function for the size.
    """
    return plt.subplots(nrows,
                        ncols,
                        figsize=standard_figsize(width, height, aspect, nrows,
                                                 ncols),
                        **kwargs)


def parse_args(args, save=False):
    """Parse command line arguments for use with make_figs.

    Parameters
    ----------
    args : list of str
        A list of string arguments, by convention sys.argv. The list controls
        output as follows:
            - The first element is ignored for sys.argv compatiblity.
            - If the next element is 'save', or 'nosave', the first return value
              will be True or False respectively.
            - If there are no further elements, second return value will be the
              full dictionary FIGURES_REGISTRY, containing all figures
              registered using the make decorator.
            - If there are further elements, they are considered to be the names
              of figures registered in the FIGURES_REGISTRY dictionary (i.e.
              dictionary keys. The second return value will consist of only
              those dictionary items for which the key matches the argument, in
              the order that the arguments are given.
    save : bool
        The default value of the first return value.

    Returns
    -------
    save : bool
        Intended to indicate whether the figures should be saved or shown.
    figures : dict mapping str -> func
        A set of figure names and figure-producing functions.

    See also
    --------
    make_figs:
        The function intended to consume the output of this function, used for
        making figures and either displaying them or saving them.
    parse_args_make_figs:
        A function that wraps the functionality of this function and make_figs
        for more convenient use.
    """
    prog = args[0]
    args = args[1:]
    if args == []:
        return save, FIGURES_REGISTRY
    if args[0] in ['help', '-h', '--help']:
        print('Usage: ')
        print(f'  {prog} [-h|--help] [save|nosave] [fig1 [fig2 ...]]')
        print('  - save/nosave overrides the default save/display behavior')
        print(f'    Default: save = {save}')
        print('  - Any figure names listed (after the optional save/nosave)')
        print('    will be processed. Default: process all figures.')
        sys.exit(0)
    if args[0] == 'save':
        save = True
        args = args[1:]
    elif args[0] == 'nosave':
        save = False
        args = args[1:]
    if len(args) == 0 or args[0] == 'all':
        return save, FIGURES_REGISTRY
    return save, {arg: FIGURES_REGISTRY[arg] for arg in args}


def make_figs(save, figures, save_dir='figures', save_type='pdf'):
    """Make a set of figures and save or show them.

    Parameters
    ----------
    save : bool
        Whether the figures should be saved or shown.
    figures : dict mapping str -> func
        A dictionary mapping figure names to figure-producing functions. The
        dictionary keys should be strings. and if save is True, these will be
        used as the output file names (with appropriate extension added). The
        functions should have no required arguments, and should return a
        matplotlib.figure.Figure that is ready to be saved or displayed.
    save_dir : str
        The name of the directory in which to save figures (if save is True).
        This is interpreted relative to the parent directory of the program
        being executed. Defaults to 'figures'.
    save_type : str
        The filetype (and backend) to use for saving figures. The implemented
        options are 'pdf' (default) and 'pgf'.

    Note
    ----
    - In the current implementation, the PGF matplotlib backend is used.
    - If save is True, each of the functions in figures.values() is executed,
      and the resulting figure is saved in save_dir, then closed.
    - If save is False, each of the functions in figures.values() is executed,
      then matplotlib.pyplot.show(block=True) is called to display all figures.

    See also
    --------
    parse_args:
        A function intended to parse sys.argv and produce inputs to this
        function.
    parse_args_make_figs:
        A function that wraps the functionality of this function and parse_args
        for more convenient use.
    """
    if save:
        if save_type == 'pdf':
            mpl.use('pdf')
            save_extension = 'pdf'
        elif save_type == 'pgf':
            mpl.use('pgf')
            save_extension = 'pgf'
        else:
            raise NotImplementedError("save_type should be 'pdf' or 'pgf'.")
        save_dir_path = os.path.join(os.path.dirname(sys.argv[0]), save_dir)
        os.makedirs(save_dir_path, exist_ok=True)
    for figname, figfunc in figures.items():
        fig = figfunc()
        if save:
            savename = os.path.join(save_dir_path,
                                    f'{figname}.{save_extension}')
            fig.savefig(savename)
            plt.close(fig)
    plt.show(block=True)


def parse_args_make_figs(save=False, savedir='figures', save_type='pdf'):
    """Parse command line arguments, make figures, then save or show them.

    Parameters
    ----------
    save : bool
        Whether the figures should be saved or shown. Default: False
    save_dir : str
        The name of the directory in which to save figures (if save is True).
        This is interpreted relative to the parent directory of the program
        being executed. Defaults to 'figures'.
    save_type : str
        The filetype (and backend) to use for saving figures. The implemented
        options are 'pdf' (default) and 'pgf'.

    Note
    ----
    This function is intended to implement a simple command line interface to
    make figures and either save or show them. See the module docstring for an
    example of how a script using this interface might be implemented.


    See also
    --------
    parse_args:
        The argument-parsing part of this function.
    make_figs:
        The figure-making part of this function.
    """

    make_figs(*parse_args(sys.argv, save), savedir, save_type)
