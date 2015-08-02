import Rhino
from Rhino.Geometry import *
import scriptcontext
from math import floor
import StringIO

def main():
    bed = VinzBed(
        matraceDimensions = Point3d(900, 2000, 240),
        frameThickness = 20, frameWidth = 140,
        feetDimensions = Point3d(80, 80, 350),
        lathThickness = 10, lathWidth = 70,
        caseThickness = 5, caseHeight = 450, caseFloorSpace = 15,
        caseBookshelfSpacer = 300
    )
    bed.build();
    bed.draw();
    scriptcontext.doc.Views.Redraw()

class VinzBed:
    def __init__(
        self, matraceDimensions, frameThickness, frameWidth, feetDimensions,
        lathThickness, lathWidth, caseThickness, caseHeight, caseFloorSpace,
        caseBookshelfSpacer
    ):
        self.matraceDimensions = matraceDimensions
        self.frameThickness = frameThickness
        self.frameWidth = frameWidth
        self.feetDimensions = feetDimensions
        self.lathThickness = lathThickness
        self.lathWidth = lathWidth
        self.caseThickness = caseThickness
        self.caseHeight = caseHeight
        self.caseFloorSpace = caseFloorSpace
        self.caseBookshelfSpacer = caseBookshelfSpacer
        self.info = StringIO.StringIO()
        self._breps = []
        
    def build(self):
        self.buildFrame()
        self.buildFeet()
        self.buildLaths()
        self.buildMatrace()
        self.buildCase()

    def buildFrame(self):
        frameLeft = BoundingBox(
            Point3d(0, 0, 0),
            Point3d(self.frameThickness, self.matraceDimensions.Y, self.frameWidth)
        ).ToBrep()
        self._breps.append(frameLeft);
        
        frameRight = frameLeft.DuplicateBrep();
        frameRight.Transform(Transform.Translation(self.matraceDimensions.X-self.frameThickness, 0, 0))
        self._breps.append(frameRight);
        
        frameBottom = BoundingBox(
            Point3d(self.frameThickness, 0, 0),
            Point3d(self.matraceDimensions.X-self.frameThickness, self.frameThickness, self.frameWidth)
        ).ToBrep()
        self._breps.append(frameBottom);
        
        frameTop = frameBottom.DuplicateBrep();
        frameTop.Transform(Transform.Translation(0, self.matraceDimensions.Y-self.frameThickness, 0))
        self._breps.append(frameTop);
        
        BoundingBox(
            Point3d(self.frameThickness, self.matraceDimensions.Y-self.frameThickness, 0),
            Point3d(self.matraceDimensions.X-self.frameThickness, self.matraceDimensions.Y, self.frameWidth)
        ).ToBrep()
        self._breps.append(frameTop);
        
        self.info.write("2x Rahmen Seite:\t\t%s x %s x %s\n" %
            (Helpers.format_measure(self.matraceDimensions.Y), Helpers.format_measure(self.frameWidth), Helpers.format_measure(self.frameThickness)))
        self.info.write("2x Rahmen Seite:\t\t%s x %s x %s\n" %
            (Helpers.format_measure(self.matraceDimensions.X-self.frameThickness*2), Helpers.format_measure(self.frameWidth), Helpers.format_measure(self.frameThickness)))

    def buildFeet(self):
        footLeftBottom = BoundingBox(
            Point3d(self.frameThickness, self.frameThickness, 0-self.feetDimensions.Z+self.frameWidth),
            Point3d(self.frameThickness+self.feetDimensions.X, self.frameThickness+self.feetDimensions.Y, self.frameWidth)
        ).ToBrep()
        
        footRightBottom = footLeftBottom.DuplicateBrep();
        footRightBottom.Transform(Transform.Translation(self.matraceDimensions.X-self.frameThickness*2-self.feetDimensions.X, 0, 0))
        
        transMoveToTop = Transform.Translation(0, self.matraceDimensions.Y-self.frameThickness*2-self.feetDimensions.Y, 0)
        
        footLeftTop = footLeftBottom.DuplicateBrep();
        footLeftTop.Transform(transMoveToTop)
        
        footRightTop = footRightBottom.DuplicateBrep();
        footRightTop.Transform(transMoveToTop)
        
        self._breps.append(footLeftBottom);
        self._breps.append(footRightBottom);
        self._breps.append(footLeftTop);
        self._breps.append(footRightTop);
        
        self.info.write("4x Fuss:\t\t\t%s x %s x %s\n" % 
            (Helpers.format_measure(self.feetDimensions.Z), Helpers.format_measure(self.feetDimensions.X), Helpers.format_measure(self.feetDimensions.Y)))
        
    def buildLaths(self):
        lathPrototype = BoundingBox(
            Point3d(0, 0, self.frameWidth),
            Point3d(self.matraceDimensions.X, self.lathWidth, self.frameWidth+self.lathThickness)
        ).ToBrep()
        self._breps.append(lathPrototype);
        
        numberOfLaths = int(((self.matraceDimensions.Y/self.lathWidth)-1)/2)
        spaceBetweenLaths = (self.matraceDimensions.Y-self.lathWidth*numberOfLaths)/(numberOfLaths-1)
        
        transLath = Transform.Translation(0, self.lathWidth + spaceBetweenLaths, 0)
        
        for i in range(1, numberOfLaths):
            newLath = lathPrototype.DuplicateBrep()
            newLath.Transform(transLath)
            self._breps.append(newLath);
            lathPrototype = newLath
            
        self.info.write("%dx Latte:\t\t\t%s x %s x %s\n" % 
            (numberOfLaths, Helpers.format_measure(self.matraceDimensions.Y), Helpers.format_measure(self.lathWidth), Helpers.format_measure(self.lathThickness)))
        self.info.write("Abstand zwischen Latten:\t%s\n" % Helpers.format_measure(spaceBetweenLaths))
            
    def buildMatrace(self):
        self._breps.append(BoundingBox(
            Point3d(0, 0, self.frameWidth+self.lathThickness),
            Point3d(self.matraceDimensions.X, self.matraceDimensions.Y, self.frameWidth+self.lathThickness+self.matraceDimensions.Z)
        ).ToBrep())
        
    def buildCase(self):
        caseZBottom = self.frameWidth-self.feetDimensions.Z+self.caseFloorSpace
        caseZTop = caseZBottom+self.caseHeight
        caseFront = BoundingBox(
            Point3d(-self.caseThickness, -self.caseThickness, caseZBottom),
            Point3d(self.matraceDimensions.X, 0, caseZTop)
        ).ToBrep()
        self._breps.append(caseFront);
        self.info.write("1x Gehaeuse vorne:\t\t%s x %s x %s\n" %
            (Helpers.format_measure(self.matraceDimensions.X+self.caseThickness), Helpers.format_measure(self.caseHeight), Helpers.format_measure(self.caseThickness)))
        caseSpacer = BoundingBox(
            Point3d(0, self.matraceDimensions.Y, caseZBottom),
            Point3d(-self.caseThickness, self.matraceDimensions.Y-self.caseBookshelfSpacer, caseZTop)
        ).ToBrep()
        self._breps.append(caseSpacer);
        self.info.write("1x Gehaeuse Spacer:\t\t%s x %s x %s\n" %
            (Helpers.format_measure(self.caseBookshelfSpacer), Helpers.format_measure(self.caseHeight), Helpers.format_measure(self.caseThickness)))
            
        drawerFront = BoundingBox(
            Point3d(0, self.matraceDimensions.Y-self.caseBookshelfSpacer, caseZBottom),
            Point3d(-self.caseThickness, 0, caseZTop)
        ).ToBrep()
        self._breps.append(drawerFront);
        self.info.write("1x Gehaeuse Schublade:\t%s x %s x %s\n" %
            (Helpers.format_measure(self.matraceDimensions.Y-self.caseBookshelfSpacer), Helpers.format_measure(self.caseHeight), Helpers.format_measure(self.caseThickness)))
    
    def draw(self):
        for brep in self._breps:
            scriptcontext.doc.Objects.AddBrep(brep)
        print(self.info.getvalue());
            
class Helpers:
    @staticmethod
    def format_measure(number):
        if number > 10 and number%10==0:
            return "%dcm" % (number / 10)
        return "%dmm" % number

main()