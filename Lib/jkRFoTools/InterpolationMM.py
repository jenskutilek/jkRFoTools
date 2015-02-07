# -*- coding: utf-8 -*-

from os.path import exists, join

from mojo.roboFont import RFont, RGlyph
from mutatorMath.objects.mutator import buildMutator

from fontMath.mathGlyph import MathGlyph
from fontMath.mathInfo import MathInfo
from fontMath.mathKerning import MathKerning

from jkRFTools.info import setFontInfo

from jkRFoTools.weight import getPanoseAndWeightForStyle


def notify(title, subtitle, message):
    from os import system
    t = '-title {!r}'.format(title)
    s = '-subtitle {!r}'.format(subtitle)
    m = '-message {!r}'.format(message)
    a = '-sender {!r}'.format("com.typemytype.robofont")
    system('terminal-notifier {}'.format(' '.join([m, t, s, a])))


class jkInstance(object):
    
    def __init__(self, location, style_name, features):
        self.features = features
        self.location = location
        self.style_name = style_name
        
        self.font = None


class jkInterpolator(object):
    
    def __init__(self, family_name, base_path=None, instance_dir=None, progressWindow=None):
        self.family_name = family_name
        self.base_path = base_path
        self.instance_dir = instance_dir
        
        self.masters = []
        self.instances = []
        self.target_glyphset = []
        
        if progressWindow is not None:
            self.progress = progressWindow
        else:
            self.progress = None
        
        if exists("/usr/bin/terminal-notifier"):
            self.use_notifications = True
        else:
            self.use_notifications = False
            print "In order to use notifications, install the command line program with:"
            print "$ sudo gem install terminal-notifier"
    
    def add_master(self, font, location):
        self.masters.append((location, font))
    
    def add_instance(self, location, style_name, features):
        self.instances.append(jkInstance(location, style_name, features))
    
    def set_target_glyphset(self, glyphnames=[]):
        self.target_glyphset = glyphnames
    
    def get_font_at_location(self, location, showUI=False):
        #print("\nBuilding font at location %s" % location)
        i_font = RFont(showUI=showUI) # showUI=False
        if self.target_glyphset == []:
            glyphset = self.masters[0][1].glyphOrder
        else:
            glyphset = self.target_glyphset
        self.interpolate_font_info(location, self.masters, i_font)
        groups = self.masters[0][1].groups
        for k in groups.keys():
            i_font.groups[k] = groups[k]
        self.interpolate_kerning(location, self.masters, i_font)
        self.interpolate_glyph_set(location, glyphset, self.masters, i_font)
        i_font.glyphOrder = glyphset
        return i_font
    
    def interpolate(self):
        if self.progress is not None:
            p = self.progress("Interpolation", tickCount = len(self.instances))
        for instance in self.instances:
            if self.progress is not None:
                p.update("%s %s %s ..." % (
                    self.family_name,
                    instance.style_name,
                    instance.location
                ))
            font = self.get_font_at_location(instance.location)
            weight_class, panose_weight = getPanoseAndWeightForStyle(instance.style_name)
            setFontInfo(font, self.family_name, instance.style_name, weight_class)
            if font.info.openTypeOS2Panose is not None:
                font.info.openTypeOS2Panose[2] = panose_weight
            font.features.text = instance.features
            instance.font = font
        if self.progress is not None:
            p.close()
    
    def generate(self):
        if self.progress is not None:
            p = self.progress("Generation", tickCount = len(self.instances))
        i = 0
        for instance in self.instances:
            if instance.font is not None:
                font = instance.font
                ps_name = font.info.postscriptFontName
                if self.progress is not None:
                    p.update("Generating %s ..." % ps_name)
                
                # save space by removing unneeded layers
                for l in font.layerOrder:
                    font.removeLayer(l)
                
                # save UFO
                font.save(join(self.base_path, self.instance_dir, "%s.ufo" % ps_name))
                
                # save OTF
                font_path = join(self.base_path, self.instance_dir, "%s.otf" % ps_name)
                font.generate(
                    path=font_path,
                    format="otf",
                    decompose=True,
                    checkOutlines=True,
                    autohint=False,
                    releaseMode=True,
                    glyphOrder=None,
                    progressBar=None,
                    useMacRoman=False,
                )
                if self.use_notifications:
                    notify("Font was generated", ps_name, font_path)
                i += 1
        if self.use_notifications:
            notify(
                "Fonts Generated",
                "%i fonts were generated." % i,
                "%s" % join(self.base_path, self.instance_dir)
            )
        if self.progress is not None:
            p.close()
    
    def interpolate_font_info(self, instanceLocation, masters, targetFont):
        infoMasters = [
            (infoLocation, MathInfo(masterFont.info))
            for infoLocation, masterFont in masters
        ]
        try:
            bias, iM = buildMutator(infoMasters)
            instanceInfo = iM.makeInstance(instanceLocation)
            instanceInfo.extractInfo(targetFont.info)
        except:
            print(u'Couldn’t interpolate font info')
    
    def interpolate_kerning(self, instanceLocation, masters, targetFont):
        kerningMasters = [
            (kerningLocation, MathKerning(masterFont.kerning))
            for kerningLocation, masterFont in masters
        ]
        try:
            bias, iK = buildMutator(kerningMasters)
            instanceKerning = iM.makeInstance(instanceLocation)
            instanceKerning.extractInfo(targetFont)
        except:
            print(u'Couldn’t interpolate font kerning')
    
    def interpolate_glyph_set(self, instanceLocation, glyphSet, masters, targetFont):
        for glyphName in glyphSet:
            masterGlyphs = [
                (masterLocation, MathGlyph(masterFont[glyphName]))
                for masterLocation, masterFont in masters
            ]
            try:
                bias, gM = buildMutator(masterGlyphs)
                newGlyph = RGlyph()
                instanceGlyph = gM.makeInstance(instanceLocation)
                targetFont.insertGlyph(instanceGlyph.extractGlyph(newGlyph), glyphName)
                targetFont[glyphName].unicode = masterFont[glyphName].unicode
                targetFont[glyphName].round()
                self.fix_component_order(masterFont[glyphName], targetFont[glyphName])
            except:
                #print(u'Incompatible glyph: %s' % glyphName)
                targetFont.newGlyph(glyphName)
                continue
    
    def fix_component_order(self, source_glyph, target_glyph):
        pass

