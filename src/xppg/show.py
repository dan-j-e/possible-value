"""Tables with a title, for notebooks."""

CAPTION_CSS = [{"selector": "caption",
                "props": "caption-side: top; text-align: left; font-weight: bold; font-size: 1.1em; padding-bottom: 6px;"}]


def table(df, title, precision=1):
    """Return the DataFrame styled with a title above it.

    A plain 0, 1, 2, ... row index means nothing to a reader, so it is hidden.
    """
    styled = (df.style.set_caption(title).set_table_styles(CAPTION_CSS)
                .format(precision=precision, thousands=","))
    if df.index.name is None and df.index.equals(__import__("pandas").RangeIndex(len(df))):
        styled = styled.hide(axis="index")
    return styled
