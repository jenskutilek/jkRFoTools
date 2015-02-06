from robofab.world import CurrentGlyph

def getSelectedOrCurrentGlyphNamesList(f):
    """
    Return a list of glyph names:
        If the Font Window is active, return selected glyph names
        If a Glyph Windows is active, return current glyph name
    """
    if CurrentGlyph() is not None:
        return [CurrentGlyph().name]
    if f.selection:
        return f.selection
    return []