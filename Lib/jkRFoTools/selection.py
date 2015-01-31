from robofab.world import CurrentGlyph

def getSelectedOrCurrentGlyphNamesList(f):
    """
    Return a list of glyph names:
        If the Font Window is active, return selected glyph names
        If a Glyph Windows is active, return current glyph name
    """
    if f.selection:
        glyph_list = f.selection
    else:
        glyph_list = [CurrentGlyph().name]
    return glyph_list