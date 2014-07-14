import vanilla
from defconAppKit.windows.baseWindow import BaseWindowController
from defconAppKit.windows.progressWindow import ProgressWindow
from robofab.world import AllFonts

class ProcessFonts(BaseWindowController):
    def __init__(self, message="Choose Fonts", function=None, show_results=True, width=400, height=300):
        """Open a window containing a list of all open fonts, to select some fonts and process them with a supplied function.
            
            message:      The title to display in the title bar, e. g. the name of your script
            function:     A function that will be called for each selected font with the RFont as its argument
            show_results: Boolean to indicate if your function returns a result which should be displayed in the result list
            width:        The initial width of the window (optional)
            height:       The initial height of the window (optional)
            
            Select and double-click rows in the result list to copy them to the pasteboard."""
        self.w = vanilla.Window(
            (width, height),
            message,
            (400, 300),
        )
        
        self.function = function
        
        column_descriptions = [
            {
                "title": "Font",
                "typingSensitive": True,
                "editable": False,
            },
        ]
        
        result_column_descriptions = [
            {
                "title": "Font",
                "typingSensitive": True,
                "editable": False,
            },
            {
                "title": "Result",
            },
        ]
        
        self.w.message = vanilla.TextBox(
            (10, 10, -10, 30),
            "Select fonts to process:",
        )
        
        self.w.font_list = vanilla.List(
            (10, 40, -10, 100),
            [],
            columnDescriptions = column_descriptions,
            drawFocusRing = True,
            allowsMultipleSelection = True,
        )
        
        self.w.result_list = vanilla.List(
            (10, 150, -10, -42),
            [],
            columnDescriptions = result_column_descriptions,
            drawFocusRing = True,
            allowsMultipleSelection = True,
            doubleClickCallback = self.copy_result,
        )
        
        self.w.cancel_button = vanilla.Button(
            (-170, -32, -90, -10),
            "Cancel",
            callback = self.cancel,
        )
        
        self.w.ok_button = vanilla.Button(
            (-80, -32, -10, -10),
            "Process",
            callback = self.ok,
        )
        
        self.setUpBaseWindowBehavior()
        self.update_font_list()
        self.w.open()
    
    def cancel(self, sender=None):
        self.w.close()
    
    def ok(self, sender=None):
        fonts = self.w.font_list.getSelection()
        
        progress = ProgressWindow(
            "",
            tickCount = len(fonts),
            parentWindow = self.w,
        )
        
        results = []
        for i in fonts:
            font = AllFonts()[i]
            progress.update("Processing %s %s ..." % (font.info.familyName, font.info.styleName))
            result = self.function(font)
            results.append(
                {
                    "Font": "%s %s" % (font.info.familyName, font.info.styleName),
                    "Result": result,
                }
            )
        progress.close()
        self.w.result_list.set(results)
    
    def copy_result(self, sender):
        from string import strip
        from AppKit import NSPasteboard, NSArray
        
        s = u""
        
        results = self.w.result_list.getSelection()
        
        for i in results:
            s += self.w.result_list.get()[i]["Font"] + "\n\n"
            s += self.w.result_list.get()[i]["Result"] + "\n\n\n"
        
        pb = NSPasteboard.generalPasteboard()
        pb.clearContents()
        a = NSArray.arrayWithObject_(s.strip(" "))
        pb.writeObjects_(a)
    
    def update_font_list(self):
        font_list = []
        self.w.font_list.set(
            [
                {
                    "Font": "%s %s" % (
                        AllFonts()[i].info.familyName,
                        AllFonts()[i].info.styleName
                    ),
                } for i in range(len(AllFonts()))
            ]
        )
    
    def windowCloseCallback(self, sender):
        super(ProcessFonts, self).windowCloseCallback(sender)
