weightclassForStyle = {
    "Thin":       (250, 3),
    "Light":      (300, 4),
    "Regular":    (400, 5),
    "Book":       (450, 5),
    "Medium":     (500, 6),
    "Demi Bold":  (600, 7),
    "Bold":       (700, 8),
    "Extra Bold": (800, 9),
    "Black":      (900, 10),
}

def getPanoseAndWeightForStyle(style):
    style_no_italic = style.strip(" Italic")
    if style_no_italic in weightclassForStyle:
        return weightclassForStyle[style_no_italic]
    else:
        return (400, 0)