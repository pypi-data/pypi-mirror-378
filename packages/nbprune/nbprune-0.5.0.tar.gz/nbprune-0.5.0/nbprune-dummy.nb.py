# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: all,-hidden,-heading_collapsed,-run_control,-trusted
#     formats: py:percent
#     notebook_metadata_filter: all, -jupytext.text_representation.jupytext_version,
#       -jupytext.text_representation.format_version, -language_info.version, -language_info.codemirror_mode.version,
#       -language_info.codemirror_mode, -language_info.file_extension, -language_info.mimetype,
#       -toc
#     text_representation:
#       extension: .py
#       format_name: percent
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
#   language_info:
#     name: python
#     nbconvert_exporter: python
#     pygments_lexer: ipython3
# ---

# %% [markdown]
# # test page for nbprune.py

# %% [markdown]
# typical use case is, a teacher writes a notebook, with solution(s) to a problem that students must solve
#
# so this means 2 versions, one for the teacher(s) with the solutions, and one for the students
#
# this tool is about defining annotations that the teacher can use to remove parts of the contents

# %% [markdown]
# ## tags

# %% [markdown]
# here are the recognized keywords
#
# | tag | meaning |
# |-|-|
# | `prune-line` (*) | remove just that one line from the output |
# | `prune-cell` | remove this cell from the output |
# | `prune-begin` | remove this cell and the ones below from the output |
# | `prune-end` | remove this cell, but resume insertion on the next cell |
# | `prune-begin-next` (**) | keep this cell from the output, and start pruning at the next one |
# | `prune-end-previous` (**) | stop pruning, and insert the current cell |

# %% [markdown]
# **NOTE** 
# * (*) `prune-line` of course is not relevant, and ignored, if set in the cell's metadata tags
# * (**) because `prune-begin-next` and `prune-end-previous` appear in a cell that is visible, the whole line containing the tag is removed from the output, so it is probably best to keep these tags on a separate line

# %% [markdown]
# ## format

# %% [markdown]
# the tool will consider a tag is present in a cell if any line in the cell contains one of the above tags, with the beginning of the line containing only `#` and spaces or tabs
#
# so for exemple
#
# | line | match |
# |:-|-|
# | prune-cell | yes |
# | # prune-cell | yes |
# | # # prune-cell | yes | 
# | some code prune-cell | no |

# %% [markdown]
# ## cell metadata

# %% [markdown]
# the tags can also be set in the cell's metadata as well (except for `prune-line`) ; something like this
#
# ```json
# {
#   "tags": [
#     "prune-cell"
#   ]
# }
# ```

# %% [markdown]
# ## examples

# %% [markdown]
# so that these 2 scenarios are equivalent

# %% [markdown] cell_style="split"
# | cell | tag | preserved |
# |-|-|-|
# | 1 | | y |
# | 2 | `prune-cell` | n |
# | 3 | | y |
# | 4 | | y |
# | 5 | `prune-begin-next` | y |
# | 6 | | n |
# | 7 | | n |
# | 8 | | n |
# | 9 | `prune-end-previous` | y |
# | 10 | | y |

# %% [markdown] cell_style="split"
# | cell | tag | preserved |
# |-|-|-|
# | 1 | | y |
# | 2 | `prune-cell` | n |
# | 3 | | y |
# | 4 | | y |
# | 5 | | y |
# | 6 | `prune-begin` | n |
# | 7 | | n |
# | 8 | `prune-end` | n |
# | 9 | | y |
# | 10 | | y |

# %%
# kept as-is
students_see_this = []

# %%
# preserved again
visible_stuff = True

# %%
visible_again = True

# %%
regular_output = True

# %%
# preserved again
visible_stuff = True

# %%
visible_again = True
