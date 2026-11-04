"""Original CNN showcase: computed features and continuous receptive-field scans."""
import json
from pathlib import Path
import numpy as np
from manim import (
    Scene, VGroup, Polygon, Line, Circle, Text, MathTex, Dot, ValueTracker,
    FadeIn, FadeOut, LaggedStart, AnimationGroup, MoveAlongPath, interpolate_color,
    WHITE, UP, DOWN, config, smooth, linear, ManimColor,
)

BLUE = ManimColor('#1767a6')
INK = '#18334b'
ORANGE = '#d66a16'
PALE = '#e9f2f8'


def compute():
    x = np.array([[0,0,.1,.9,.1,0,0], [0,.1,.8,1,.7,.1,0],
                  [0,.7,1,.3,1,.7,0], [.1,1,.5,0,.5,1,.1],
                  [.4,1,1,1,1,1,.4], [.8,.6,.1,0,.1,.6,.8],
                  [.6,.2,0,0,0,.2,.6]], dtype=float)[None]
    rng = np.random.default_rng(23)
    k1 = np.array([[[[0,0,0],[-1,0,1],[0,0,0]]],
                   [[[0,-1,0],[0,0,0],[0,1,0]]],
                   [[[0,1,0],[1,-3,1],[0,1,0]]]],dtype=float)
    k2 = rng.normal(0,.3,(4,3,3,3))
    def conv(a,k,b):
        windows=np.lib.stride_tricks.sliding_window_view(a,(3,3),axis=(1,2))
        return np.maximum(np.einsum('cijuv,ocuv->oij',windows,k)+b[:,None,None],0)
    a=conv(x,k1,np.array([.12,.12,.15]))
    b=conv(a,k2,np.full(4,.2))
    w=rng.normal(0,.25,(5,36)); bias=np.full(5,.15)
    h=np.maximum(w@b.reshape(-1)+bias,0)
    v=rng.normal(0,.6,(3,5)); ob=np.array([.1,-.1,.2])
    logits=v@h+ob; p=np.exp(logits-logits.max());p/=p.sum()
    return dict(x=x,a=a,b=b,h=h,p=p,k1=k1,k2=k2,w=w,bias=bias,v=v,ob=ob)


class Plane(VGroup):
    U=np.array([.31,.025,0]); V=np.array([-.105,.31,0])
    def __init__(self, values, center):
        super().__init__(); self.values=values;self.n=len(values);self.origin=np.array(center,dtype=float)
        self.cells={}
        for row in range(self.n):
            for col in range(self.n):
                cell=Polygon(*(self.point(col+dx,row+dy) for dx,dy in [(0,0),(1,0),(1,1),(0,1)]),
                             color='#b8cede',stroke_width=.65,fill_color=WHITE,fill_opacity=1)
                self.cells[row,col]=cell;self.add(cell)
        self.border=Polygon(*(self.point(c,r) for c,r in [(0,0),(self.n,0),(self.n,self.n),(0,self.n)]),
                            color=BLUE,stroke_width=1.6,fill_opacity=0)
        self.add(self.border)
    def point(self,c,r):
        return self.origin+(c-self.n/2)*self.U+(self.n/2-r)*self.V
    def window(self,row,col,size):
        return Polygon(*(self.point(col+dc,row+dr) for dc,dr in [(0,0),(size,0),(size,size),(0,size)]),
                       color=ORANGE,stroke_width=2.4,fill_color=ORANGE,fill_opacity=.10)
    def fill_value(self,row,col,scale):
        value=float(self.values[row,col]);color=interpolate_color(WHITE,BLUE,.10+.85*value/scale)
        return self.cells[row,col].animate.set_fill(color,opacity=1)


class Visualization(Scene):
    def mark(self,name,duration=.35):
        self.wait(duration/2);self.stages[name]=float(self.time);self.wait(duration/2)

    def construct(self):
        self.stages={};data=compute()
        title=Text('From pixels to prediction',font_size=36,weight='BOLD',color=INK).move_to([0,3.05,0])
        subtitle=Text('Convolutional neural network',font_size=20,color='#607587').move_to([0,2.5,0])
        self.add(title,subtitle)
        centers=[[-5.6,0,0],[-2.5,0,0],[.3,0,0]]
        stacks=[]
        for key,center in zip(('x','a','b'),centers):
            planes=[]
            for channel,values in enumerate(data[key]):
                offset=np.array([.20,.15,0])*channel
                planes.append(Plane(values,np.array(center)+offset))
            stacks.append(planes)
        # Draw rear maps first, so overlap consistently communicates depth.
        for planes in stacks:
            for plane in reversed(planes): self.add(plane)
        labels=VGroup()
        for x,name,dim in [(-5.6,'Input',r'1\times7\times7'),(-2.3,'Convolution + ReLU',r'3\times5\times5'),
                            (.6,'Convolution + ReLU',r'4\times3\times3'),(3.5,'Dense',r'36\to5'),(6,'Softmax',r'3')]:
            labels.add(Text(name,font_size=20,color=INK).move_to([x,-2.05,0]),
                       MathTex(dim,font_size=26,color=BLUE).move_to([x,-2.52,0]))
        caption=Text('Fixed illustrative weights · activations computed from the input',font_size=17,color='#607587').move_to([0,-3.35,0])
        self.add(labels,caption)
        hidden=VGroup(*(Circle(.14,color=BLUE,stroke_width=1.6,fill_color=WHITE,fill_opacity=1)
                        .move_to([3.5,y,0]) for y in np.linspace(1.15,-1.15,5)))
        outputs=VGroup(*(Circle(.19,color=BLUE,stroke_width=1.8,fill_color=WHITE,fill_opacity=1)
                         .move_to([6,y,0]) for y in (.85,0,-.85)))
        edges=VGroup()
        for i,node in enumerate(hidden):
            for j,target in enumerate(outputs):
                edge=Line(node.get_right(),target.get_left(),color='#c9d8e3',stroke_width=.7+abs(data['v'][j,i])*.5)
                edges.add(edge)
        fans=VGroup(*(Line(plane.point(3,row+.5),node.get_left(),color='#d9e4ec',stroke_width=.65)
                      for plane in stacks[2] for row in (0,1,2) for node in hidden))
        self.add(fans,edges,hidden,outputs)
        for planes in stacks:
            for plane in planes: plane.save_state()
        max0=max(float(data['x'].max()),1e-8)
        self.play(AnimationGroup(*(stacks[0][0].fill_value(r,c,max0) for r in range(7) for c in range(7))),run_time=.8)
        self.mark('input-ready',.4)

        def scan(source,destination,key,duration):
            n=destination[0].n
            tracker=ValueTracker(0)
            positions=[(r,c) for r in range(n) for c in (range(n) if r%2==0 else reversed(range(n)))]
            def coordinates():
                progress=np.clip(tracker.get_value(),0,len(positions)-1)
                a=int(progress);b=min(a+1,len(positions)-1);t=progress-a
                return (1-t)*np.array(positions[a])+t*np.array(positions[b])
            windows=VGroup()
            for plane in reversed(source):
                window=plane.window(0,0,3)
                window.add_updater(lambda m,plane=plane:m.become(plane.window(*coordinates(),3)))
                windows.add(window)
            connectors=VGroup()
            for plane in destination:
                for offset in [(0,0),(1,0),(1,1),(0,1)]:
                    line=Line(source[0].point(0,0),plane.point(0,0),stroke_width=1,color=ORANGE,stroke_opacity=.45)
                    def update(m,plane=plane,offset=offset):
                        row,col=coordinates();dc,dr=offset
                        m.put_start_and_end_on(source[0].point(col+dc*3,row+dr*3),plane.point(col+dc,row+dr))
                    line.add_updater(update);connectors.add(line)
            self.play(FadeIn(windows),FadeIn(connectors),run_time=.3)
            scale=max(float(data[key].max()),1e-8)
            for index,(row,col) in enumerate(positions):
                animations=[tracker.animate.set_value(index)]
                animations.extend(plane.fill_value(row,col,scale) for plane in destination)
                self.play(*animations,run_time=duration,rate_func=linear)
            for obj in [windows,connectors]:obj.clear_updaters(recursive=True)
            self.mark(key+'-scan-complete',.25)
            self.play(FadeOut(windows),FadeOut(connectors),run_time=.35)

        scan(stacks[0],stacks[1],'a',.11)
        self.mark('first-features',.45)
        scan(stacks[1],stacks[2],'b',.19)
        self.mark('second-features',.45)
        # Flattened feature flow is represented by connections from each map row.
        fan_pulses=VGroup(*(Dot(radius=.025,color=ORANGE) for _ in fans))
        self.add(fan_pulses)
        self.play(LaggedStart(*(MoveAlongPath(dot,edge) for dot,edge in zip(fan_pulses,fans)),
                             lag_ratio=.006),run_time=.9)
        self.remove(*fan_pulses,fan_pulses)
        hscale=max(float(data['h'].max()),1e-8)
        self.play(*(node.animate.set_fill(interpolate_color(WHITE,BLUE,.12+.85*float(value)/hscale),opacity=1)
                    for node,value in zip(hidden,data['h'])),run_time=.5)
        self.mark('dense-activations',.4)
        pulses=VGroup(*(Dot(radius=.035,color=ORANGE) for _ in edges));self.add(pulses)
        self.play(LaggedStart(*(MoveAlongPath(dot,edge) for dot,edge in zip(pulses,edges)),lag_ratio=.018),run_time=1.05)
        self.remove(*pulses,pulses)
        scores=VGroup(*(MathTex(f'{value:.2f}',font_size=21,color=INK).next_to(node, direction=np.array([1,0,0]),buff=.16)
                        for node,value in zip(outputs,data['p'])))
        self.play(*(node.animate.set_fill(interpolate_color(WHITE,BLUE,float(value)),opacity=1)
                    for node,value in zip(outputs,data['p'])),FadeIn(scores,shift=UP*.08),run_time=.55)
        winner=int(np.argmax(data['p']))
        ring=Circle(.25,color=ORANGE,stroke_width=2.5).move_to(outputs[winner])
        self.play(FadeIn(ring),run_time=.3)
        self.mark('prediction',1.5)
        # Reset the actual objects, keeping all geometry fixed across the seam.
        self.play(FadeOut(scores),FadeOut(ring),
                  *(plane.animate.restore() for planes in stacks for plane in planes),
                  *(node.animate.set_fill(WHITE,opacity=1) for node in [*hidden,*outputs]),run_time=.8)
        self.mark('reset',.5)
        run=Path(config.media_dir).parent
        (run/'stages.json').write_text(json.dumps(self.stages,indent=2)+'\n')
        (run/'computation.json').write_text(json.dumps({k:v.tolist() for k,v in data.items()},indent=2)+'\n')
