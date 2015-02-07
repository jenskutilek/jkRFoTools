import platform
from os.path import join, exists
from mojo.roboFont import OpenFont
from defconAppKit.windows.progressWindow import ProgressWindow

def get_factor(stem, stem_min, stem_max):
    return (stem-stem_min)/(stem_max-stem_min)

def notify(title, subtitle, message):
    from os import system
    t = '-title {!r}'.format(title)
    s = '-subtitle {!r}'.format(subtitle)
    m = '-message {!r}'.format(message)
    a = '-sender {!r}'.format("com.typemytype.robofont")
    system('terminal-notifier {}'.format(' '.join([m, t, s, a])))

class jkInstance(object):
    
    def __init__(self, style_name, master0, master1, factor, weight_class, features):
        self.style_name = style_name
        self.master0 = master0
        self.master1 = master1
        self.factor = factor
        self.weight_class = weight_class
        self.features = features
        self.font = None
    

class jkGenerator(object):
    
    def __init__(self, family_name, base_path=None, instance_dir=None, show_ui=False):
        self.family_name = family_name
        self.base_path = base_path
        self.instance_dir = instance_dir
        self.show_ui = show_ui
        
        self.masters = {}
        self.instances = []
        
        if exists("/usr/bin/terminal-notifier"):
            self.use_notifications = True
        else:
            self.use_notifications = False
            print "In order to use notifications, install the command line program with:"
            print "$ sudo gem install terminal-notifier"
    
    
    def add_master(self, ufo_name):
        self.masters[ufo_name] = OpenFont(join(self.base_path, ufo_name), showUI=self.show_ui)
    
    
    def add_instance(self, style_name, master0, master1, factor, weight_class, features):
        self.instances.append(jkInstance(style_name, master0, master1, factor, weight_class, features))
    
    
    def interpolate(self):
        progress = ProgressWindow(
            "Interpolation",
            tickCount = len(self.instances),
        )

        for instance in self.instances:
            #ip = NewFont(self.family_name, instance.style_name, showUI=self.show_ui)
            ip = self.masters[instance.master0].copy()
            ip.info.familyName = self.family_name
            ip.info.styleName = instance.style_name
            progress.update("Interpolating %s %s ..." % (self.family_name, instance.style_name))
            
            ip.interpolate(
                instance.factor,
                self.masters[instance.master0],
                self.masters[instance.master1],
                doProgress=False
            )
            
            ip.info.openTypeOS2WeightClass = instance.weight_class
            ip.features.text = instance.features
            
            self.post_interpolation(ip)
            
            instance.font = ip
        progress.close()
    
    def post_interpolation(self, ip):
        
        ip["Delta"].unicode = 0x2206
        ip["Omega"].unicode = 0x2126
        ip["mu"].unicode = 0x00b5
        
        for gn in "ordfeminine ordmasculine Eth dcroat Hbar hbar Lslash lslash Tbar tbar uni040B uni0414 uni042A uni0434 uni044A uni0490 uni0491 uni0492 uni0493 uni04A0 uni04A1 uni04B0 uni04B1 uni04B8 uni04B9 uni04CC daggerdbl uni2116 cent.lf daggerdbl.lf notequal.lf eth.sc hbar.sc lslash.sc eng.sc tbar.sc uni0434.sc uni044A.sc uni045B.sc uni0491.sc uni0493.sc uni04A1.sc uni04B1.sc uni04B9.sc uni04CC.sc uni0525.sc".split():
            ip[gn].decompose()
        
        for glyph in ip:
            glyph.round()
    
    def generate(self):
        progress = ProgressWindow(
            "Generation",
            tickCount = len(self.instances) * 2,
        )
        i = 0
        for instance in self.instances:
            font = instance.font
            ps_name = "%s-%s" % (font.info.familyName, font.info.styleName)
            ps_name = ps_name.replace(" ", "")
            
            self.pre_generate(font, progress)
            
            font_path = join(self.base_path, self.instance_dir, "%s.otf" % ps_name)
            font.generate(
                path=font_path,
                format="otf",
                decompose=True,
                checkOutlines=True,
                autohint=True,
                releaseMode=True,
                glyphOrder=None,
                progressBar=None,
                useMacRoman=False,
            )
            if self.use_notifications:
                notify("Font was generated", ps_name, font_path)
            font.close()
            i += 1
        if self.use_notifications:
            notify("Fonts Generated", "%i fonts were generated." % i, "%s" % join(self.base_path, self.instance_dir))
        progress.close()
    
    def pre_generate(self, font, progress=None):
        ps_name = "%s-%s" % (font.info.familyName, font.info.styleName)
        ps_name = ps_name.replace(" ", "")
        font.info.postscriptFontName = ps_name
        if progress is not None:
            progress.update("Processing %s ..." % ps_name)
        font.info.openTypeNameDesigner = "Jens Kutilek"
        font.info.openTypeNameDesignerURL = "http://www.kutilek.de/"
        font.info.openTypeNameManufacturer = "Jens Kutilek"
        font.info.openTypeNameManufacturerURL = "http://www.kutilek.de/"
        font.info.openTypeNameLicense = "For internal use only"
        font.info.openTypeNameLicenseURL = ""
        font.info.copyright = "Copyright 2014 by Jens Kutilek."
        font.info.trademark = "A trademark of Jens Kutilek"
        font.info.openTypeOS2Type = [2, 8]
        font.info.openTypeOS2VendorID = "jens"
        
        # save space by removing unneeded layers
        for l in font.layerOrder:
            font.removeLayer(l)
        font.save(join(self.base_path, self.instance_dir, "%s.ufo" % ps_name))
        
        if progress is not None:
            progress.update("Generating %s ..." % ps_name)
