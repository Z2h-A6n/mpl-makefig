Some things that may be worth doing:

- Add more length scales to the `UNITS` dictionary:
    - Paper sizes: `letter_width`, `letter_height`, `A0`, `A1`, `A2`, ...
    - Text area width/height in MS Word with standard margin settings.
- The implementation of `split_num_unit` is a bit dodgy and could be improved.
- Make some things more configurable:
    - E.g. choose the savefig backend?
    - Should be done in a way that doesn't add much complexity to makefig, or to
      projects using makefig.
      - Maybe a good option is to pass it as optional kwargs to
        `parse_args_make_figs`, so that all the configuration is basically
        done in the `__main__` block.
- Consider adding some code to allow saving the current matplotlib.rcParams
  to a file, to allow for (more) reproducible figure production.
    - Presumably it would be best to use a file format that is either:
        - suitable for use with `matplotlib.rc_file()`, i.e. an equivalent
          format to matplotlibrc
        - easy to load into a python `dict`. This may be useful in case the user
          wants to load the file, delete some items (so that the values from
          matplotlibrc are used), and use the modified dict.
    - It would (probably) be nice if the rcParams are saved the same way figures
      are saved in the usual CLI, i.e. using `parse_args_make_figs()`.
      Presumably this would involve one of:
        - Adding an item to the `FIGURES_REGISTRY`, then checking the type of
          the items in `FIGURES_REGISTRY` to decide how to save each object.
        - Adding special rcParams saving code to `parse_args_make_figs`, or one
          of the functions it calls, in order to specifically save the rcParams.
