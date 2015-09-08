import pymadx.Ptc
import pymadx.Beam
import pymadx.Builder
import pymadx.Tfs
import pybdsim.Beam
import pybdsim.Builder
import pybdsim.Data
import pybdsim.Convert
import pybdsim.Testing
import pymadx as _pymadx
import os as _os
import matplotlib.pyplot as _plt
import robdsim
import numpy as _np
import root_numpy as _rnp
import matplotlib.backends.backend_pdf
import time


class LatticeTest:
    def __init__(self,filepath, nparticles = 1000, verbose=False):        
        """
        Takes a .madx file containing description of a lattice and generates
        BDSIM and MadX PTC jobs from it as well as MadX optical functions 
        propagation plots.

        nparticles: specifies the number of particles to be used for BDSIM/PTC runs. Default = 1000
        verbose   : prints additional information
        """
        cwd        = _os.getcwd()
        path       = filepath.split("/")
        filename   = path[-1]                         #last element is the filename
        
        if(path[0]=="/"):                             #when absolute filepath is given
            folderpath = path[:-1]
        else:
            folderpath = cwd+"/"+"/".join(path[:-1])  #when relative filepath is given

        print "Filename: ",filename
        print "Folderpath: ",folderpath
        
        if filename[-5:] == ".madx":                
            self.filename    = filename[:-5]
            self.tfsfilename = str.lower(self.filename)
            self.filepath    = filepath
            self.folderpath  = folderpath
            self.ptcinrays   = self.filename+"_inrays.madx"
            self.ptcfilename = "ptc_"+self.filename+".madx"
            self.nparticles  = nparticles
            self.verbose     = verbose
            self.figureNr    = 1729
        else:
            raise IOError('Invalid file format')

    def CleanRunCompare(self):
        self.Clean()
        self.Run()
        self.Compare(addPrimaries=False)

    def Clean(self):
        """
        Delete all files produced during the testing, including
        .log .dat .tfs. .ps ptc* .txt .root .gmad inrays .png .pdf
        """
        _os.chdir(self.folderpath)
        
        _os.system("rm -rf *.log")
        _os.system("rm -rf *.dat")
        _os.system("rm -rf *.tfs")
        _os.system("rm -rf *.ps")
        _os.system("rm -rf ptc*")
        _os.system("rm -rf *.txt")
        _os.system("rm -rf *.root")
        _os.system("rm -rf *.gmad")
        _os.system("rm -rf *_inrays.madx")
        _os.system("rm -rf *.png")
        _os.system("rm -rf *.pdf")
        _os.system("rm trackone")

        # clean and close figures (10 figures in total)
        for i in range(11):
            _plt.close(self.figureNr+i)


    def Run(self):
        print 'Test> Lattice: ', self.filename 
        print 'Test> Destination filepath: ', self.filepath

        _os.chdir(self.folderpath)

        _os.system("madx < "+self.filename+".madx > madx.log")

        """
        a = pybdsim.Convert.MadxTfs2Gmad(''+self.tfsfilename+'.tfs','dump',beam=False)
        b = pybdsim.Beam.Beam('proton',10.0,'ptc')    #beam parameters need to be set manually
        b.SetDistribFileName('INRAYS.madx')           #This is for testing BDSIM 'ptc' beam distribution
        a.AddBeam(b)
        a.WriteLattice(self.filename)
        
        """ 
        pybdsim.Convert.MadxTfs2Gmad(self.tfsfilename+'.tfs', self.filename, verbose=self.verbose)                        
        
        _pymadx.MadxTfs2Ptc(''+self.tfsfilename+'.tfs', self.ptcfilename, self.ptcinrays)

        _os.system("bdsim --file="+self.filename+".gmad --ngenerate="+str(self.nparticles)+" --batch --output=root --outfile="+self.filename+" > bdsim.log")

        pybdsim.Testing.BdsimPrimaries2Ptc(''+self.filename+'.root', self.ptcinrays)

        _os.system("madx < "+self.ptcfilename+" > ptc_madx.log")


    def Compare(self, plot='beta', addPrimaries=False, showPlots=False):
        """
        Performs analysis and comparison of BDSIM, MADX and MADX-PTC output. 
       
        addPrimaries - True adds BDSIM primaries to histos. Default is False
        plot         - | beta | emittance | alpha |  - specify optical function to plot
        showPlots    - True diplays the plots to screen
        """

        _os.chdir(self.folderpath)

        #Load data
        isValid  = False
        attempts = 0
        
        while(isValid==False and attempts<=5):
            rootdata  = robdsim.RobdsimOutput(self.filename+".root")
            print "robdsim.RobdsimOutput> root file loaded"
        
            primchain = rootdata.GetSamplerChain('Primaries')
            bdsimprim = _rnp.tree2rec(primchain)
            Bx0 = bdsimprim['x']
            By0 = bdsimprim['y']
            Bxp0 = bdsimprim['xp']
            Byp0 = bdsimprim['yp']
            self.bdsimprimaries = {'x':Bx0,'y':By0,'xp':Bxp0,'yp':Byp0}
            
            endchain = rootdata.GetSamplerChain('Sampler_theendoftheline')
            bdsim = _rnp.tree2rec(endchain)
            Bx = bdsim['x']
            By = bdsim['y']
            Bxp = bdsim['xp']
            Byp = bdsim['yp']
            self.bdsimoutput = {'x':Bx,'y':By,'xp':Bxp,'yp':Byp}
            
            madxout = pymadx.Tfs("trackone")
            madxend = madxout.GetSegment(madxout.nsegments) #get the last 'segment' / sampler
            Mx = madxend.GetColumn('X')
            My = madxend.GetColumn('Y') 
            Mxp = madxend.GetColumn('PX')
            Myp = madxend.GetColumn('PY')
            self.ptcoutput = {'x':Mx,'y':My,'xp':Mxp,'yp':Myp}

            #Check all particles make it through
            if(len(Bx)!=len(Mx)):
                    print "Input particles: ",self.nparticles," BDS_out particles: ", len(Bx)," PTC_out particles: ", len(Mx)       
                    print "Warning:  Unequal number of output particles! Attempting again..."
                    attempts += 1
                    print "Attempt: ", attempts
                    self.Clean()
                    self.Run()                  
            else:
                isValid = True

            if(attempts==5):
                print "Run unsuccessful, please check parameters and try again"
                return
        
        
        #fractional errors
        fresx  = Mx - Bx
        fresy  = My - By
        fresxp = Mxp - Bxp
        fresyp = Myp - Byp
        self.residuals = {'x':fresx,'y':fresy,'xp':fresxp,'yp':fresyp}
        
        print "Average residuals:"," x(m): ",_np.mean(fresx)," y(m): ",_np.mean(fresy)
        print " xp(rad): ",_np.mean(fresxp)," yp(rad): ",_np.mean(fresyp)
        
        #standard deviation
        stdMx  = _np.std(Mx)
        stdMy  = _np.std(My)
        stdMxp = _np.std(Mxp)
        stdMyp = _np.std(Myp)

        stdBx  = _np.std(Bx)
        stdBy  = _np.std(By)
        stdBxp = _np.std(Bxp)
        stdByp = _np.std(Byp)

        #standard devation fractional errors
        frestdx  = _np.nan_to_num(stdMx - stdBx)
        frestdy  = _np.nan_to_num(stdMy - stdBy)
        frestdx  = _np.nan_to_num(frestdx / stdMx) #protect against nans for 0 diff
        frestdy  = _np.nan_to_num(frestdy / stdMy)
        frestdxp = _np.nan_to_num(stdMxp - stdBxp)
        frestdyp = _np.nan_to_num(stdMyp - stdByp)
        frestdxp = _np.nan_to_num(frestdxp / stdMxp)
        frestdyp = _np.nan_to_num(frestdyp / stdMyp)

        # write standard deviations to file
        with open(''+self.filename+'_stdev.txt', 'w') as stdout:
            timestamp = time.strftime("%Y/%m/%d-%H:%M:%S")
            t = timestamp+' '+self.filename+' Standard Deviations (particles = '+str(self.nparticles)+'): \n'
            h = 'BDSIM_X \t MX-PTC_X \t BDSIM_Y \t MX-PTC_Y \t BDSIM_XP'
            h+= ' \t MX-PTC_XP \t BDSIM_YP \t MX-PTC_YP \t FRCERR_X \t FRCERR_Y \t FRCERR_XP \t FRCERR_YP \n'
            s  = "{0:.4e}".format(stdBx)
            s += '\t' +  "{0:.4e}".format(stdMx)
            s += '\t' +  "{0:.4e}".format(stdBy)              
            s += '\t' +  "{0:.4e}".format(stdMy)
            s += '\t' +  "{0:.4e}".format(stdBxp)
            s += '\t' +  "{0:.4e}".format(stdMxp)
            s += '\t' +  "{0:.4e}".format(stdByp)
            s += '\t' +  "{0:.4e}".format(stdMyp)
            s += '\t' +  "{0:.4e}".format(frestdx)
            s += '\t' +  "{0:.4e}".format(frestdy)
            s += '\t' +  "{0:.4e}".format(frestdxp)
            s += '\t' +  "{0:.4e}".format(frestdyp) + '\n'
            stdout.writelines(t)
            stdout.writelines(h)
            stdout.writelines(s)
        
        #Loading output and processing optical functions
        madx = pymadx.Tfs(''+self.tfsfilename+'.tfs')

        print "robdsim.CalculateOpticalFunctions> processing..."        
        rootdata.CalculateOpticalFunctions(''+self.filename+'_optics.dat')
        bdata  = pybdsim.Data.Load(''+self.filename+'_optics.dat')

        print "ptcCaluclateOpticalFunctions> processing..."
        ptc      = _pymadx.PtcAnalysis(ptcOutput="trackone") 
        ptc.CalculateOpticalFunctions('ptc_'+self.filename+'_opticalfns.dat')
        ptcdata  = pybdsim.Data.Load('ptc_'+self.filename+'_opticalfns.dat')

        #Get the S coordinate from all outputs
        M_s       = madx.GetColumn('S')
        B_s       = bdata.S()
        PTC_s     = ptcdata.S()

        #optfn denotes the selected optical function to plot
        in_Tfs = True       #some of the calculated optical functions are not present in the tfs file (e.g emittance,sigmas)
                            #and hence plots and residuals between BDSIM and MADX cannot be obtained
        if (plot=='beta'):
            fn_name    = r'\beta' #this is a raw string for Latex labels and titles
            fn_rname   = 'beta'   #this is reduced name for filename of saved figure
            
            M_optfn_x  = madx.GetColumn('BETX') 
            M_optfn_y  = madx.GetColumn('BETY')

            B_optfn_x  = bdata.Beta_x()
            B_optfn_y  = bdata.Beta_y()

            PTC_optfn_x = ptcdata.Beta_x()
            PTC_optfn_y = ptcdata.Beta_y()

        elif (plot=='alpha'):
            fn_name    = r'\alpha'
            fn_rname   = 'alpha'
            
            M_optfn_x  = madx.GetColumn('ALFX') 
            M_optfn_y  = madx.GetColumn('ALFY')

            B_optfn_x  = bdata.Alph_x()
            B_optfn_y  = bdata.Alph_y()

            PTC_optfn_x = ptcdata.Alph_x()
            PTC_optfn_y = ptcdata.Alph_y()

        elif (plot=='emittance'):
            fn_name    = r'\epsilon'
            fn_rname   = 'emittance'

            print "WARNING: Emittance not present in MADX tfs file, plotting only MADX-PTC and BDSIM results "
            in_Tfs     = False
            
            B_optfn_x  = bdata.Emitt_x()
            B_optfn_y  = bdata.Emitt_y()

            PTC_optfn_x = ptcdata.Emitt_x()
            PTC_optfn_y = ptcdata.Emitt_y()
            
        else:
            print "Error: Unrecognised plotting option:",option
            return
            
        if(in_Tfs):
            M_s    = M_s[:len(B_s)]
            M_optfn_x = M_optfn_x[:len(B_optfn_x)]    #Madx arrays need to be sliced because they contain
            M_optfn_y = M_optfn_y[:len(B_optfn_y)]    #one too many columns. No information is lost in the slicing
                                                      #as the last Madx segment is default end of the line info and is
                                                      #degenerate with the last element segment
        PTC_s    = PTC_s[:len(B_s)]
        PTC_optfn_x = PTC_optfn_x[:len(B_optfn_x)]
        PTC_optfn_y = PTC_optfn_y[:len(B_optfn_y)]
        
        _plt.figure(self.figureNr, figsize=(11, 8), dpi=80, facecolor='w', edgecolor='k')
        _plt.clf()
        if(in_Tfs):
            _plt.plot(M_s,M_optfn_x,'.',color='r',linestyle='solid',label=r'$'+fn_name+r'_{x}$MDX')
            _plt.plot(M_s,M_optfn_y,'.',color='b',linestyle='solid',label=r'$'+fn_name+r'_{y}$MDX')
        _plt.plot(PTC_s,PTC_optfn_x,'*',color='r',linestyle=':',linewidth=1.2,label=r'$'+fn_name+r'_{x}$PTC')
        _plt.plot(PTC_s,PTC_optfn_y,'*',color='b',linestyle=':',linewidth=1.2,label=r'$'+fn_name+r'_{y}$PTC')
        _plt.plot(B_s,B_optfn_x,'.',color='r',linestyle='dashed',linewidth=1.2,label=r'$'+fn_name+r'_{x}$BDS')
        _plt.plot(B_s,B_optfn_y,'.',color='b',linestyle='dashed',linewidth=1.2,label=r'$'+fn_name+r'_{y}$BDS')
        _plt.xlabel(r'$S (m)$')
        _plt.ylabel(r'$'+fn_name+r'_{x,y}(m)$')
        _plt.legend(numpoints=1,loc=7)

        #optical function residuals
        if(in_Tfs):
            res_optfn_x = M_optfn_x-B_optfn_x        
            res_optfn_y = M_optfn_y-B_optfn_y
        
            _plt.figure(self.figureNr+1, figsize=(11, 8), dpi=80, facecolor='w', edgecolor='k')
            _plt.clf()
            _plt.plot(M_s,res_optfn_x,'*',color='r',linestyle='solid',label=r'$\beta_{x}$Res')
            _plt.plot(M_s,res_optfn_y,'*',color='b',linestyle='solid',label=r'$\beta_{y}$Res')
            _plt.title(self.filename+r' Plot of $'+fn_name+r'_{x,y}$ Residuals vs $S$')
            _plt.xlabel(r'$S (m)$')
            _plt.ylabel(r'$'+fn_name+r'_{x,y} Residuals(m)$')
            _plt.legend(numpoints=1,loc=7)
               
        # 2d plots
        arrow_width_scale = 1e-3  #Factor used to multiply minimum residual between BDSIM and PTC data in order to
                                  #heuristicaly obtain a width for the quiver plot arrows connecting the two data sets
                                  #Very crude, fix in the future

        f = _plt.figure(self.figureNr+2, figsize=(11, 8), dpi=80, facecolor='w', edgecolor='k')
        f.suptitle(self.filename)
        _plt.clf()
        
        #X vs Y
        ax1 = f.add_subplot(221)
        arrow_width = abs(_np.min(fresy))*arrow_width_scale
        _plt.quiver(Mx,My,-fresx,-fresy,angles='xy',scale_units='xy',scale=1,color='r',units='x',width=arrow_width,headwidth=3)
        _plt.plot(Mx,My,'b.',label='PTC')
        _plt.plot(Bx,By,'g.',label='BDSIM')
        if addPrimaries:
            _plt.plot(Bx0,By0,'r.',label='BDSIM prim')
        _plt.legend()
        _plt.xlabel(r"x (m)")
        _plt.ylabel(r"y (m)")
        startx, endx = ax1.get_xlim()
        starty, endy = ax1.get_ylim()
        ax1.xaxis.set_ticks([startx,0,endx])
        ax1.yaxis.set_ticks([starty,0,endy])

        #XP vs YP
        ax2 = f.add_subplot(222)
        arrow_width = abs(_np.min(fresyp))*arrow_width_scale
        _plt.quiver(Mxp,Myp,-fresxp,-fresyp,angles='xy',scale_units='xy',scale=1,color='r',units='x',width=arrow_width,headwidth=3)
        _plt.plot(Mxp,Myp,'b.',label='PTC')
        _plt.plot(Bxp,Byp,'g.',label='BDSIM')
        if addPrimaries:
            _plt.plot(Bxp0,Byp0,'r.',label='BDSIM prim')
        _plt.legend()
        _plt.xlabel(r"x' (m)")
        _plt.ylabel(r"y' (m)")
        startx, endx = ax2.get_xlim()
        starty, endy = ax2.get_ylim()
        ax2.xaxis.set_ticks([startx,0,endx])
        ax2.yaxis.set_ticks([starty,0,endy])

        #X vs XP
        arrow_width = abs(_np.min(fresxp))*arrow_width_scale
        ax3 = f.add_subplot(223)
        _plt.quiver(Mx,Mxp,-fresx,-fresxp,angles='xy',scale_units='xy',scale=1,color='r',units='x',width=arrow_width,headwidth=3)
        _plt.plot(Mx,Mxp,'b.',label='PTC')
        _plt.plot(Bx,Bxp,'g.',label='BDSIM')
        if addPrimaries:
            _plt.plot(Bx0,Bxp0,'r.',label='BDSIM prim')
        _plt.legend()
        _plt.xlabel(r"x (m)")
        _plt.ylabel(r"x' (rad)")
        startx, endx = ax3.get_xlim()
        starty, endy = ax3.get_ylim()
        ax3.xaxis.set_ticks([startx,0,endx])
        ax3.yaxis.set_ticks([starty,0,endy])

        #Y vs YP
        arrow_width = abs(_np.min(fresyp))*arrow_width_scale
        ax4 = f.add_subplot(224)
        _plt.quiver(My,Myp,-fresy,-fresyp,angles='xy',scale_units='xy',scale=1,color='r',units='x',width=arrow_width,headwidth=3)
        _plt.plot(My,Myp,'b.',label='PTC')
        _plt.plot(By,Byp,'g.',label='BDSIM')
        if addPrimaries:
            _plt.plot(By0,Byp,'r.',label='BDSIM prim')
        _plt.legend()
        _plt.xlabel(r"y (m)")
        _plt.ylabel(r"y' (rad)")
        startx, endx = ax4.get_xlim()
        starty, endy = ax4.get_ylim()
        ax4.xaxis.set_ticks([startx,0,endx])
        ax4.yaxis.set_ticks([starty,0,endy])

        _plt.subplots_adjust(left=0.1,right=0.9,top=0.95, bottom=0.15, wspace=0.35, hspace=0.2)
        
        # 1d plots
        # x comparison
        f = _plt.figure(self.figureNr+6, figsize=(11, 8), dpi=80, facecolor='w', edgecolor='k')
        f.suptitle(self.filename)
        _plt.clf()

        nbinsx = _np.linspace(min(Mx),max(Mx),10)    #fix bins to avoid potential underflow/overflow
        nbinsy = _np.linspace(min(My),max(My),10)
        nbinsxp = _np.linspace(min(Mxp),max(Mxp),10)
        nbinsyp = _np.linspace(min(Myp),max(Myp),10)

        ax1 = f.add_subplot(221)
        ax1.hist(Mx,nbinsx,color='b',label='PTC',histtype='step')
        ax1.hist(Bx,nbinsx,color='g',label='BDSIM',histtype='step')
        if addPrimaries:
            ax1.hist(Bx0,nbinsx,color='r',label='BDSIM prim',histtype='step')
        ax1.legend(fontsize='x-small',loc=0)
        ax1.set_xlabel(r"x (m)")
        startx, endx = ax1.get_xlim()
        starty, endy = ax1.get_ylim()
        ax1.xaxis.set_ticks([startx,0,endx])
        ax1.yaxis.set_ticks([starty,0,endy])
        
        # y comparison
        ax2 = f.add_subplot(222)
        ax2.hist(My,nbinsy,color='b',label='PTC',histtype='step')
        ax2.hist(By,nbinsy,color='g',label='BDSIM',histtype='step')
        if addPrimaries:
            ax2.hist(By0,nbinsy,color='r',label='BDSIM prim',histtype='step')
        ax2.legend(fontsize='x-small',loc=0)
        ax2.set_xlabel(r"y (m)")
        startx, endx = ax2.get_xlim()
        starty, endy = ax2.get_ylim()
        ax2.xaxis.set_ticks([startx,0,endx])
        ax2.yaxis.set_ticks([starty,0,endy])

        # xp comparison
        ax3 = f.add_subplot(223)
        ax3.hist(Mxp,nbinsxp,color='b',label='PTC',histtype='step')
        ax3.hist(Bxp,nbinsxp,color='g',label='BDSIM',histtype='step')
        if addPrimaries:
            ax3.hist(Bxp0,nbinsxp,color='r',label='BDSIM prim',histtype='step')
        ax3.legend(fontsize='x-small',loc=0)
        ax3.set_xlabel(r"x' (rad)")
        startx, endx = ax3.get_xlim()
        starty, endy = ax3.get_ylim()
        ax3.xaxis.set_ticks([startx,0,endx])
        ax3.yaxis.set_ticks([starty,0,endy])

        # yp comparison
        ax4 = f.add_subplot(224)
        ax4.hist(Myp,nbinsyp,color='b',label='PTC',histtype='step')
        ax4.hist(Byp,nbinsyp,color='g',label='BDSIM',histtype='step')
        if addPrimaries:
            ax4.hist(Byp0,nbinsyp,color='r',label='BDSIM prim',histtype='step')
        ax4.legend(fontsize='x-small',loc=0)
        ax4.set_xlabel(r"y' (rad)")
        startx, endx = ax4.get_xlim()
        starty, endy = ax4.get_ylim()
        ax4.xaxis.set_ticks([startx,0,endx])
        ax4.yaxis.set_ticks([starty,0,endy])
        
        _plt.subplots_adjust(left=0.1,right=0.9,top=0.95, bottom=0.15, wspace=0.3, hspace=0.2)
               
        # residuals in one plot
        nbins=50
        
        f = _plt.figure(self.figureNr+10, figsize=(11, 8), dpi=80, facecolor='w', edgecolor='k')
        _plt.clf()

        axX = f.add_subplot(221)
        hist, xedges, yedges = _np.histogram2d(Mx,fresx,bins=nbins)
        hist = _np.rot90(hist)                         #flip and rotate the plots to display them properly
        hist = _np.flipud(hist)
        histmasked = _np.ma.masked_where(hist==0,hist) # Mask pixels with a value of zero
        
        _plt.pcolormesh(xedges,yedges,histmasked)
        axX.set_xlabel('x(m)')
        axX.set_ylabel('Residuals_x(m)')
        cbar = _plt.colorbar()
        cbar.ax.set_ylabel('Counts')
        startx, endx = axX.get_xlim()
        starty, endy = axX.get_ylim()
        axX.xaxis.set_ticks([startx,0,endx])
        axX.yaxis.set_ticks([starty,0,endy])
        
        axX = f.add_subplot(222)
        hist, xedges, yedges = _np.histogram2d(My,fresy,bins=nbins)
        hist = _np.rot90(hist)
        hist = _np.flipud(hist)
        histmasked = _np.ma.masked_where(hist==0,hist)
        
        _plt.pcolormesh(xedges,yedges,histmasked)
        axX.set_xlabel('y(m)')
        axX.set_ylabel('Residuals_y(m)')
        cbar = _plt.colorbar()
        cbar.ax.set_ylabel('Counts')
        startx, endx = axX.get_xlim()
        starty, endy = axX.get_ylim()
        axX.xaxis.set_ticks([startx,0,endx])
        axX.yaxis.set_ticks([starty,0,endy])
        
        axX = f.add_subplot(223)
        hist, xedges, yedges = _np.histogram2d(Mxp,fresxp,bins=nbins)
        hist = _np.rot90(hist)
        hist = _np.flipud(hist)
        histmasked = _np.ma.masked_where(hist==0,hist)
        
        _plt.pcolormesh(xedges,yedges,histmasked)
        axX.set_xlabel('xp(rad)')
        axX.set_ylabel('Residuals_xp(rad)')
        cbar = _plt.colorbar()
        cbar.ax.set_ylabel('Counts')
        startx, endx = axX.get_xlim()
        starty, endy = axX.get_ylim()
        axX.xaxis.set_ticks([startx,0,endx])
        axX.yaxis.set_ticks([starty,0,endy])
        
        axX = f.add_subplot(224)
        hist, xedges, yedges = _np.histogram2d(Myp,fresyp,bins=nbins)
        hist = _np.rot90(hist)
        hist = _np.flipud(hist)
        histmasked = _np.ma.masked_where(hist==0,hist)
        
        _plt.pcolormesh(xedges,yedges,histmasked)
        axX.set_xlabel('yp(rad)')
        axX.set_ylabel('Residuals_yp(rad)')
        cbar = _plt.colorbar()
        cbar.ax.set_ylabel('Counts')
        startx, endx = axX.get_xlim()
        starty, endy = axX.get_ylim()
        axX.xaxis.set_ticks([startx,0,endx])
        axX.yaxis.set_ticks([starty,0,endy])

        _plt.subplots_adjust(left=0.15, right=0.95, top=0.95, bottom=0.15, wspace=0.39, hspace=0.25)

        #Open pdf output file and save all plots to it
        pdf = matplotlib.backends.backend_pdf.PdfPages(self.filename+"_plots.pdf")
        for i in _plt.get_fignums():
            pdf.savefig(i)
        pdf.close()
        
        if(showPlots):
            _plt.show()

        #print emittance
        print 'Horizontal emittance bdsim (before,after) ',bdata.Emitt_x()
        print 'Vertical emittance bdsim (before,after) ',bdata.Emitt_y()

        #print stdev fractional errors
        print 'stdFracErrX= ',frestdx,' stdFracErrY= ', frestdy, 'stdFracErrXP= ', frestdxp, 'stdFracErrX= ', frestdyp
        


       

        

            

        
            


        

    

