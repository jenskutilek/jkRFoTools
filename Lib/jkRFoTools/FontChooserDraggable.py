from Cocoa import NSStringPboardType, NSDragOperationMove, NSArray
import vanilla
from defconAppKit.windows.baseWindow import BaseWindowController
from defconAppKit.windows.progressWindow import ProgressWindow
from lib.scripting.codeEditor import CodeEditor
from robofab.world import AllFonts

class ProcessFonts(BaseWindowController):
    def __init__(self, message="Choose Fonts", function=None, show_results=True, width=400, height=300):
        """Open a window containing a list of all open fonts, to select some fonts and process them with a supplied function.
            
            message:      The title to display in the title bar, e. g. the name of your script
            function:     A function that will be called for each selected font with the RFont as its argument
            show_results: Boolean to indicate if your function returns a result which should be displayed in the result box
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
            doubleClickCallback = self.copy_result,
            selectionCallback = self.show_result,
            selfDropSettings = {
                "type": NSStringPboardType,
                "operation": NSDragOperationMove,
                "callback": self.list_drop,
            },
            dragSettings = {
                "type": NSStringPboardType,
                "dropDataFormat": None,
                "callback": self.list_drag,
            },
        )
        
        self.w.result_box = CodeEditor((10, 150, -10, -42), "", lexer="text")
        
        self.w.copy_button = vanilla.Button(
            (10, -32, 110, -10),
            "Copy results",
            callback = self.copy_result,
        )
        
        self.w.cancel_button = vanilla.Button(
            (-180, -32, -100, -10),
            "Cancel",
            callback = self.cancel,
        )
        
        self.w.ok_button = vanilla.Button(
            (-90, -32, -10, -10),
            "Process",
            callback = self.ok,
        )
        
        self.setUpBaseWindowBehavior()
        self._drag_src_rows = []
        self.update_font_list()
        self.w.open()
    
    def cancel(self, sender=None):
        self.w.close()
    
    def ok(self, sender=None):
        self.w.cancel_button.enable(False)
        self.w.ok_button.enable(False)
        self.w.copy_button.enable(False)
        
        fonts = self.w.font_list.getSelection()
        
        progress = ProgressWindow(
            "",
            tickCount = len(fonts),
            parentWindow = self.w,
        )
        
        results = []
        for i in range(len(AllFonts())):
            font = AllFonts()[i]
            if i in fonts:
                progress.update("Processing %s %s ..." % (font.info.familyName, font.info.styleName))
                result = self.function(font)
                if result is None:
                    result = "Unknown"
                results.append(
                    {
                        "Font": "%s %s" % (font.info.familyName, font.info.styleName),
                        "Result": result,
                    }
                )
            else:
                results.append(
                    {
                        "Font": "%s %s" % (font.info.familyName, font.info.styleName),
                        "Result": self.w.font_list.get()[i]["Result"],
                    }
                )
        progress.close()
        self.w.font_list.set(results)
        self.w.font_list.setSelection(fonts)
        
        self.w.cancel_button.setTitle("Close")
        self.w.cancel_button.enable(True)
        self.w.ok_button.enable(True)
        self.w.copy_button.enable(True)
    
    def copy_result(self, sender):
        from string import strip
        from AppKit import NSPasteboard, NSArray
        
        s = u""
        
        results = self.w.font_list.getSelection()
        
        for i in results:
            s += self.w.font_list.get()[i]["Font"] + "\n\n"
            s += self.w.font_list.get()[i]["Result"] + "\n\n\n"
        
        pb = NSPasteboard.generalPasteboard()
        pb.clearContents()
        a = NSArray.arrayWithObject_(s.strip("\n"))
        pb.writeObjects_(a)
    
    def show_result(self, sender=None):
        results = self.w.font_list.getSelection()
        if len(results) > 0:
            self.w.result_box.set(self.w.font_list.get()[results[0]]["Result"])
            selection_empty = False
        else:
            self.w.result_box.set("")
            selection_empty = True
        if selection_empty:
            self.w.ok_button.enable(False)
            self.w.copy_button.enable(False)
        else:
            self.w.ok_button.enable(True)
            self.w.copy_button.enable(True)
    
    def update_font_list(self):
        font_list = []
        self.w.font_list.set(
            [
                {
                    "Font": "%s %s" % (
                        AllFonts()[i].info.familyName,
                        AllFonts()[i].info.styleName
                    ),
                    "Result": ""
                } for i in range(len(AllFonts()))
            ]
        )
    
    def list_drag(self, sender=None, drop_info=None):
        self._drag_src_rows = drop_info
        print "Drag Source Rows:", drop_info
        data = [self.w.font_list[i] for i in drop_info]
        return data
    
    def list_drop(self, sender=None, drop_info=None):
        if drop_info is not None:
            if drop_info["isProposal"]:
                # TODO: check if drop is acceptable
                return True
            else:
                print "DEBUG: dropped item in position %i" % drop_info["rowIndex"]
                print " Data: %s" % drop_info["data"]
                print drop_info
                # TODO: accept the drop (actually do something)
                self.insert_data(drop_info["data"], drop_info["rowIndex"])
                return True
    
    def delete_rows(self, row_index_list):
        for row_index in row_index_list:
            del self.w.font_list[i]
    
    def insert_data(self, data, row_index):
        print "insert_data"
        #print type(data), data
        for i in range(len(data)-1, -1, -1):
            print "Insert:", row_index, i, data[i]
            self.w.font_list.insert(row_index, data[i])
    
    def windowCloseCallback(self, sender):
        super(ProcessFonts, self).windowCloseCallback(sender)

if __name__ == "__main__":
    ProcessFonts()