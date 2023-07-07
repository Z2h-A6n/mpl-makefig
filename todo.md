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
