"""Submodule of XML specific utilities."""

from collections.abc import Iterable

from lxml import etree

PARSER = etree.XMLParser(recover=True)


def yield_recursive_findall(
    element: etree._Element,
    tag: str | Iterable[str],
) -> Iterable[etree._Element]:
    """
    Yield all occurrences of a given XML tag at any depth in an XML tree.

    Yields
    ------
    etree._Element
        The next XML element with the requested tag.

    """
    if isinstance(tag, str):
        tag = {tag}
    if not isinstance(tag, set):
        tag = set(tag)
    if element.tag in tag:
        yield element
    for child in element:
        yield from yield_recursive_findall(child, tag)
