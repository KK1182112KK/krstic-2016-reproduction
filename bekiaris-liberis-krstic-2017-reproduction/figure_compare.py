"""Optional comparison to supplied 2017 PDF vector paths, not OCR.
Calibration follows visually inspected published axes. Original curve data
remain local; author PDFs are not redistributed. Comparison is not raw data.
"""
from pathlib import Path
import argparse,json
import numpy as np
import fitz

def extract(pg,index,box,xmax,ymin,ymax):
 g=pg.get_drawings()[index];pts=[]
 for it in g['items']:
  if it[0]=='l':pts.extend([(it[1].x,it[1].y),(it[2].x,it[2].y)])
 if len(pts)<100:raise ValueError('Unexpected PDF path')
 q=np.asarray(pts);xx=(q[:,0]-box[0])/(box[2]-box[0])*xmax;yy=ymax-(q[:,1]-box[1])/(box[3]-box[1])*(ymax-ymin)
 xx[np.abs(xx)<1e-5]=0.;xx[np.abs(xx-xmax)<1e-5]=xmax
 k=np.argsort(xx,kind='stable');xx=xx[k];yy=yy[k];x,j=np.unique(xx,return_index=True)
 return x,yy[j]

def main(pdf):
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 root=Path(__file__).parent;out=root/'figure_audit';out.mkdir(exist_ok=True);doc=fitz.open(pdf)
 specs=[(3,10,[56,57,58],(336.967987,72.283997,531.646973,222.348022),100.,-.4,.5,[1,2,3],'predictor_h0.0025'),
 (4,11,[24,25],(68.765999,72.565979,263.453003,226.429993),100.,-.8,.4,[5,4],'predictor_h0.0025'),
 (5,11,[74,75,76],(68.571999,321.326996,263.25,471.391998),15.,-10.,6.,[3,2,1],'uncompensated_continuous_tol1e-12')]
 result=[]
 for fig,p,ids,box,tmax,ymin,ymax,cols,case in specs:
  sim=np.loadtxt(root/'results'/f'{case}.csv',delimiter=',',skiprows=1)
  for j,col in zip(ids,cols):
   t,y=extract(doc[p],j,box,tmax,ymin,ymax);m=(t>=0)&(t<=tmax);t=t[m];y=y[m]
   ys=np.interp(t,sim[:,0],sim[:,col]);delta=ys-y
   row={'figure':fig,'path':j,'column':col,'case':case,'max_abs_difference':float(abs(delta).max()),'rms_difference':float(np.sqrt(np.mean(delta**2))), 'source_initial':float(y[0]),'source_final':float(y[-1])}
   if fig==5:
    for end in [5,10,12,15]:row[f'max_difference_through_{end}s']=float(abs(delta[t<=end]).max())
   result.append(row)
   np.savetxt(out/f'fig{fig}_column{col}.csv',np.column_stack([t,y,ys]),delimiter=',',header='time,published_vector_curve,own_simulation',comments='')
  f,ax=plt.subplots(figsize=(8,4.2))
  for j,col in zip(ids,cols):
   t,y=extract(doc[p],j,box,tmax,ymin,ymax)
   label=('U'+str(col-3)) if fig==4 else ('X'+str(col))
   ax.plot(t,y,'--',label=label+' published curve',linewidth=1.)
   mm=sim[:,0]<=tmax;ax.plot(sim[mm,0],sim[mm,col],label=label+' original-plant run',linewidth=.8)
  ax.set(xlabel='Time (s)',ylabel='Input' if fig==4 else 'State',title=f'Figure {fig}: vector-curve comparison, not author raw data');ax.grid(alpha=.25);ax.legend(fontsize=7)
  f.tight_layout();f.savefig(out/f'fig{fig}_comparison.png',dpi=160);plt.close(f)
 (out/'comparison.json').write_text(json.dumps(result,indent=2))
 print(json.dumps(result,indent=2))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--pdf',required=True);main(ap.parse_args().pdf)
