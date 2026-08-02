import pylab as _pl
import pymad8 as _m8
import matplotlib.patches as _mpt
import matplotlib.pyplot as _plt


def testOneDim():
    s = _m8.Output("./test/atf_v5.1/survey.tape", "survey")
    od = OneDim(s, False)
    od.plot()
    return od    


def testTwoDim():
    s = _m8.Output("./test/atf_v5.1/survey.tape", "survey")
    td = TwoDim(s, False, False, True)
    td.plot()
    return td


def transformedRect(xyc, dx, dy, theta):
    x = xyc[0]
    y = xyc[1]

    # basic rectangle
    xy = _pl.array([[-dx/2.0, -dy/2.0],
                   [-dx/2.0, +dy/2.0],
                   [+dx/2.0, +dy/2.0],
                   [+dx/2.0, -dy/2.0]])

    # transform to correct location 
    p  = transformedPoly(xy, xyc, theta)
    
    return p


def transformedPoly(xy, xyc, theta):
    # Rotate in place
    r = _pl.array([[_pl.cos(theta), -_pl.sin(theta)],
                   [_pl.sin(theta), _pl.cos(theta)]])
    xy = xy.dot(r)

    # Translate to new centre 
    xy = xy + xyc 
    p = _mpt.Polygon(xy)

    # Return transformed poly
    return p


def MakeCombinedSurveyPlot(name, QUAD=True, RBEN=True, SBEN=True, MONI=True, MARK=True):
    """MakeCombinedSurveyPlot(name,QUAD=True,RBEN=True,SBEN=True,MONI=True,MARK=True)
    Takes a list of Survey filenames, plots them all on the same 2D plot. For branching machines or segmented models. Elements selectable via booleans, default to true"""
    Combined = _plt.figure()
    _plt.xlabel("x (m)")
    _plt.ylabel("y (m)")
    ax = Combined.add_subplot(111)
    for file in name:	
        loadname = file
        plotname = str.replace(loadname, "SURVEY_", "")
        loader = _m8.Output()
        loader.fileName = loadname
        surveydata = loader.readSurveyFile()
        TwoD = _m8.Visualisation.TwoDim(surveydata)
        TwoD.x = TwoD.survey.data[0:, TwoD.survey.keys['x']]
        TwoD.y = TwoD.survey.data[0:, TwoD.survey.keys['y']]
        TwoD.z = TwoD.survey.data[0:, TwoD.survey.keys['z']]
        ax.plot(TwoD.z, TwoD.x, '--', label=plotname)
        if QUAD:
            TwoD.drawElements("QUAD") 
        if RBEN:
            TwoD.drawElements("RBEN") 
        if SBEN:
            TwoD.drawElements("SBEN") 
        if MONI:
            TwoD.drawElements("MONI") 
        if MARK:
            TwoD.drawElements("MARK")

        xmin = TwoD.x.min()
        xmax = TwoD.x.max()
        zmin = TwoD.z.min()
        zmax = TwoD.z.max()
        ax.legend(loc='upper left')
        if zmin < ax.get_xlim()[0]:
            ax.xlim(zmin-10, ax.get_xlim()[1])
        if zmax > ax.get_xlim()[1]:
            ax.xlim(ax.get_xlim()[0], zmax)

        if xmin < ax.get_ylim()[0]:
            ax.ylim(xmin-10, ax.get_ylim()[1])
        if xmax > ax.get_ylim()[1]:
            ax.ylim(ax.get_ylim()[0], xmax)

    Combined.savefig( "./combined_plot.pdf")


class OneDim:
    def __init__(self, survey, debug):
        self.survey = survey 

        self.x    =  self.survey.data[:, self.survey.keys['x']]
        self.y    =  self.survey.data[:, self.survey.keys['y']]
        self.z    = -self.survey.data[:, self.survey.keys['z']]
        self.suml =  self.survey.data[:, self.survey.keys['suml']]

        self.debug    = debug 
        # self.annotate = annotate
        self.quadWidth = 0.1
        self.bendWidth = 0.1
        self.sextWidth = 0.1

        self._offcolour = '0.9'
        self._no_colour = '0.2'

    def plot(self, colour=True):
        s = self.survey.data[:, self.survey.keys['suml']]
        z = _pl.zeros(s.shape)

        # plot beam line
        _pl.plot(s, z, 'k-')
        _pl.ylim(-1.5, 1.5)

        # Draw specific types of element
        self._drawElements("QUAD", colour)
        self._drawElements("SBEN", colour)
        self._drawElements("RBEN", colour)
        self._drawElements("SEXT", colour)

    def _drawElements(self, type, colour=True):
        if self.debug:
            print('pymad8.Visualisation.OneDim.drawElements>')

        ilist = self.survey.getIndexByTypes(type)
        for i in ilist:
            self._drawElement(i, colour)
    
    def _drawElement(self, elem, colour=True):
        if self.debug:
            print('pymad8.Visualisation.OneDim.drawElement>', elem)
            print('pymad8.Visualisation.OneDim.drawElement> Use Colour -> ', colour)

        # find element if string
        if type(elem) == str:
            i = self.survey.getIndexByNames(elem)[0]
        else:
            i = elem

        t    = self.survey.getTypesByIndex(i)
        n    = self.survey.getNamesByIndex(i)
        s    = self.survey.getRowsByIndex(i)
        suml = self.suml[i]

        if t == 'QUAD':
            self._drawQuad(s, suml, colour)
        elif t == 'MULT':
            self._drawMult(s, suml, colour)
        elif t == 'SBEN':
            self._drawBend(s, suml, colour)
        elif t == 'RBEN':
            self._drawBend(s, suml, colour)
        elif t == 'SEXT':
            self._drawSext(s, suml, colour)
        elif t == 'HKIC':
            self._drawHkic(s, suml, colour)
        elif t == 'VKIC':
            self._drawVkic(s, suml, colour)
        elif t == 'MONI':
            self._drawMoni(s, suml, colour)
        elif t == 'WIRE':
            self._drawWire(s, suml, colour)
        elif t == 'PROF':
            self._drawProf(s, suml, colour)
        elif t == 'INST':
            self._drawInst(s, suml, colour)
        elif t == 'MARK':
            self._drawMark(s, suml, colour)
        else:
            print('pymad8.Visualisation.OneDim> Type not known')

        # Annotate element

    def _drawQuad(self, s, suml, colour=True):
        ql = s['l']
        qk = s['k1']
        poscolour = 'r'
        negcolour = 'b'
        if not colour:
            poscolour, negcolour = self._no_colour, self._no_colour
        
        if qk > 0:
            qr = _mpt.Rectangle((suml-ql/2.0, 0), ql, self.quadWidth, color=poscolour)
        elif qk < 0:
            qr = _mpt.Rectangle((suml-ql/2.0, -self.quadWidth), ql, self.quadWidth,color=negcolour)
        elif qk == 0:
            qr = _mpt.Rectangle((suml-ql/2.0, -self.quadWidth/2.0), ql, self.quadWidth, color=self._offcolour)
            
        ax = _plt.gca()
        ax.add_patch(qr)

    def _drawMult(self, s, suml, colour=True):
        pass

    def _drawBend(self, s, suml, colour=True):
        # colour argument unused but added for compliance
        bl = s['l']
        br = _mpt.Rectangle((suml-bl/2.0, -self.bendWidth/2.0), bl, self.bendWidth, color='k')
        ax = _plt.gca()
        ax.add_patch(br)

    def _drawSext(self, s, suml, colour=True):
        sl = s['l']
        ax = _plt.gca()
        # original but looks like thin lens for most lattices rather
        # than hexagon
        # sh = mpt.RegularPolygon((suml-sl/2.0,0),6,
        #                        sl,color='g')
        if colour == True:
            sext_colour = 'g'
        else:
            sext_colour = 'grey'
        
        sh = _mpt.Rectangle((suml-sl/2.0, -self.bendWidth/2.0), sl, self.bendWidth, color=sext_colour)
        ax.add_patch(sh)        

    def _drawHkic(self, s, suml, colour=True):
        pass

    def _drawVkic(self, s, suml, colour=True):
        pass
        
    def _drawMoni(self, s, suml, colour=True):
        pass
    
    def _drawWire(self, s, suml, colour=True):
        pass

    def _drawProf(self, s, suml, colour=True):
        pass

    def _drawInst(self, s, suml, colour=True):
        pass
    
    def _drawMark(self, s, suml, colour=True):
        pass


class TwoDim:
    def __init__(self, survey, debug=False, annotate=False, fancy=False):
        self.debug     = debug
        self.annotate  = annotate
        self.fancy     = fancy
        self.survey    = survey
        self.quadWidth = 0.75

    def plot(self, event=None):
        print('Visualisation.TwoDim.plot>')
        self.x = self.survey.data[:, self.survey.keys['x']]
        self.y = self.survey.data[:, self.survey.keys['y']]
        self.z = -self.survey.data[:, self.survey.keys['z']]

        self.f  = _plt.figure()
#        self.rec = self.f.canvas.mpl_connect('draw_event',self.plotUpdate)        

        xmin = self.x.min()
        xmax = self.x.max()
        zmin = self.z.min()
        zmax = self.z.max()

        self.ax = _plt.gca()
        self.ax.clear()        

        _pl.plot(self.z, self.x, '--')
        _pl.xlim(zmin-10, zmax+10)
        _pl.ylim(xmin-10, xmax+10)

        self._drawElements("QUAD")
        self._drawElements("RBEN")
        self._drawElements("SBEN")
        self._drawElements("MONI")
        self._drawElements("MARK")
        
    def plotUpdate(self, event):
        print('Visualisation.TwoDim.plotUpdate>')
        self._drawElements("QUAD")

    def _drawElements(self, type):
        if self.debug:
            print('pymad8.Visualisation.TwoDim.drawElements>')

        ilist = self.survey.getIndexByTypes(type)
        for i in ilist:
            self._drawElement(i)

    def _drawElement(self, elem):
        if self.debug:
            print('pymad8.Visualisation.TwoDim.drawElement>', elem)

        # find element if string
        if type(elem) == str:
            i = self.survey.getIndexByNames(elem)[0]
        else :
            i = elem

        t = self.survey.getTypesByIndex(i)
        n = self.survey.getNamesByIndex(i)
        s = self.survey.getRowsByIndex(i)

        # plot marker
        ex = self.x[i]
        ey = self.y[i]
        ez = self.z[i]

        if t == 'QUAD':
            self._drawQuad(s, ex, ey, ez)
        elif t == 'SBEN':
            self._drawBend(s, ex, ey, ez)
        elif t == 'RBEN':
            self._drawBend(s, ex, ey, ez)
        elif t == 'MONI':
            self._drawMoni(s, ex, ey, ez)
        elif t == 'MARK':
            self._drawMark(s, ex, ey, ez)
        else:
            print('pymad8.Visualisation.TwoDim> Type not known')
        # pl.plot([z[i]],[x[i]],"+")

        # Annotate element

    def _drawQuad(self, s, x, y, z):
        if self.debug:
            print('Visualisation.TwoDim.drawQuad>')
            print('>', s)
        if self.fancy:
            # get data
            ql = s['l']
            qk = s['k1']
            qt = s['theta']

            # make patch
            qr = transformedRect([z, x], ql, self.quadWidth, qt)
            qr.set_color('r')
            qr.set_alpha(0.6)

            # add patch
            ax = _plt.gca()
            ax.add_patch(qr)
        else:
            _pl.plot([z], [x], 'r+')

    def _drawBend(self, s, x, y, z):
        if self.debug:
            print('Visualisation.TwoDim.drawDipole>')

        if self.fancy:
            # get data
            bl = s['l']
            bt = s['theta']
            
        else:
            _pl.plot([z], [x], 'b+')

    def _drawMoni(self, s, x, y, z):
        if self.debug:
            print('Visualisation.TwoDim.drawMoni>')

        _pl.plot([z], [x], 'g+')

    def _drawMark(self, s, x, y, z):
        if self.debug:
            print('Visualisation.TwoDim.drawMark>')

        _pl.plot([z], [x], 'b+')
    
