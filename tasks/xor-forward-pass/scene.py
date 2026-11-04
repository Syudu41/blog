"""A restrained XOR explanation with a stable network and one detail panel."""
import json
from pathlib import Path
import numpy as np
from manim import (Scene, VGroup, Text, MathTex, Circle, Dot, Line, DashedLine,
                   Axes, FadeIn, FadeOut, Create, AnimationGroup, MoveAlongPath,
                   ShowPassingFlash, interpolate_color, ManimColor, WHITE, UP,
                   RIGHT, config, smooth)
from manim_ml.neural_network import NeuralNetwork, FeedForwardLayer

BLUE=ManimColor('#126b91')
ORANGE='#d46217'
INK='#193549'
GRAY='#647887'

def compute():
    w1=np.array([[1.,-1.],[-1.,1.]])
    w2=np.array([[10.,10.]])
    cases=[]
    for x in ([0.,0.],[0.,1.],[1.,0.],[1.,1.]):
        x=np.array(x);z=w1@x;h=np.maximum(z,0);logit=float((w2@h)[0]-5)
        p=float(1/(1+np.exp(-logit)));y=int(x[0]!=x[1])
        loss=float(-y*np.log(p)-(1-y)*np.log1p(-p))
        cases.append(dict(x=x.tolist(),z=z.tolist(),h=h.tolist(),logit=logit,p=p,y=y,loss=loss))
    return dict(w1=w1.tolist(),b1=[0.,0.],w2=w2.tolist(),b2=-5.,cases=cases)


class ActivationPlot(VGroup):
    def __init__(self,sigmoid=False):
        super().__init__()
        self.fn=(lambda z:1/(1+np.exp(-z))) if sigmoid else (lambda z:max(0,z))
        limits=[-6,6,3] if sigmoid else [-1.5,1.5,1]
        self.axes=Axes(x_range=limits,y_range=[0,1.2,.5],x_length=2.65,y_length=1.4,
                       axis_config={'color':'#a2b3be','stroke_width':1.2,'include_tip':False})
        self.axes.move_to([4.25,.15,0])
        self.curve=self.axes.plot(self.fn,x_range=[-6,6,.05] if sigmoid else [-1.4,1.2,.02],
                                  color=BLUE,stroke_width=3,use_smoothing=False)
        self.add(self.axes,self.curve)
        ticks=[-5,0,5] if sigmoid else [-1,0,1]
        for value in ticks:
            self.add(MathTex(str(value),font_size=18,color=GRAY).move_to(self.axes.c2p(value,0)+[0,-.19,0]))
        self.add(MathTex('1',font_size=18,color=GRAY).move_to(self.axes.c2p(0,1)+[-.17,0,0]))
        self.add(MathTex('z',font_size=20,color=GRAY).move_to(self.axes.c2p(limits[1],0)+[.15,.02,0]))
        self.add(MathTex('a',font_size=20,color=GRAY).move_to(self.axes.c2p(0,1.2)+[.03,.16,0]))


class Visualization(Scene):
    def mark(self,name,duration=.6):
        self.wait(duration/2);self.stages[name]=float(self.time);self.wait(duration/2)

    def construct(self):
        data=compute();case=data['cases'][2];self.stages={};traces=[];panel_bounds=[]
        title=Text('XOR: one forward pass',font_size=33,weight='BOLD',color=INK)
        title.move_to([-6.15,3.28,0],aligned_edge=np.array([-1,0,0]))
        subtitle=Text('Follow the values, one operation at a time',font_size=19,color=GRAY)
        subtitle.move_to([-6.15,2.7,0],aligned_edge=np.array([-1,0,0]))
        case_label=MathTex(r'x=(1,0),\quad y=1',font_size=28,color=INK).move_to([4.25,3.25,0])
        separator=Line([1.45,2.35,0],[1.45,-2.25,0],color='#dde6ec',stroke_width=1)
        footer_rule=Line([-6.15,-2.65,0],[6.15,-2.65,0],color='#e1e8ed',stroke_width=1)
        footer_note=Text('One forward pass · fixed illustrative weights',font_size=16,color=GRAY).move_to([0,-3.66,0])
        self.add(title,subtitle,case_label,separator,footer_rule,footer_note)
        locations=[[[-5.2,.65,0],[-5.2,-1.05,0]],[[-2.65,.65,0],[-2.65,-1.05,0]],[[.15,-.2,0]]]
        layers=[FeedForwardLayer(n,node_radius=.38,node_color=BLUE,node_stroke_width=2.4,
                                rectangle_stroke_width=0,rectangle_fill_color=WHITE) for n in(2,2,1)]
        network=NeuralNetwork(layers,layer_spacing=2)
        for layer,positions in zip(layers,locations):
            layer.surrounding_rectangle.set_opacity(0)
            for node,position in zip(layer.node_group,positions):
                node.move_to(position).set_fill(WHITE,opacity=1).set_z_index(3)
        for connection in network.connective_layers:
            paths=VGroup(*(Line(a.get_center(),b.get_center(),buff=.38,color='#c4d4df',stroke_width=1.4)
                           for a in connection.input_layer.node_group for b in connection.output_layer.node_group))
            connection.edges.become(paths).set_z_index(-2)
        headers=VGroup(*(Text(name,font_size=21,color=INK).move_to([x,1.9,0])
                         for name,x in [('Input',-5.2),('Hidden',-2.65),('Output',.15)]))
        symbols=VGroup()
        for layer,names in zip(layers,[(r'x_1',r'x_2'),(r'h_1',r'h_2'),(r'\hat y',)]):
            for node,name in zip(layer.node_group,names):
                symbols.add(MathTex(name,font_size=22,color=GRAY).move_to(node.get_center()+[0,.6,0]))
        self.play(FadeIn(network),FadeIn(headers),FadeIn(symbols),run_time=.8)
        node_labels=VGroup()
        def activate(node,value,label,run_time=.45):
            label=MathTex(label,font_size=27 if len(label)<3 else 22,color=INK).move_to(node).set_z_index(5)
            if label.width>.62:label.scale_to_fit_width(.62)
            self.play(FadeIn(label),node.animate.set_fill(interpolate_color(WHITE,BLUE,.55*value),opacity=1),run_time=run_time)
            node_labels.add(label)
        caption=VGroup();panel_title=VGroup();panel_formula=VGroup();result=VGroup()
        def crossfade(old,new,time=.3):
            if old.has_points() or len(old.submobjects):
                self.play(FadeOut(old),run_time=time*.4)
            self.play(FadeIn(new),run_time=time*.6)
            return new
        def say(words):
            nonlocal caption
            new=Text(words,font_size=22,color=INK).move_to([0,-3.12,0])
            caption=crossfade(caption,new)
        def panel(words,formula):
            nonlocal panel_title,panel_formula
            heading=Text(words,font_size=24,weight='BOLD',color=INK).move_to([4.25,2.05,0])
            equation=MathTex(formula,font_size=26,color=INK).move_to([4.25,1.45,0])
            if equation.width>3.8:equation.scale_to_fit_width(3.8)
            self.play(FadeOut(panel_title),FadeOut(panel_formula),run_time=.12)
            self.play(FadeIn(heading),FadeIn(equation),run_time=.22)
            panel_bounds.append(float(min(heading.get_left()[0],equation.get_left()[0])))
            panel_title,panel_formula=heading,equation
        def send(paths,name):
            self.stages[name]=float(self.time)
            dots=VGroup(*(Dot(radius=.04,color=ORANGE).move_to(edge.get_start()) for edge in paths)).set_z_index(4)
            self.add(dots)
            self.play(AnimationGroup(*(AnimationGroup(MoveAlongPath(dot,edge,rate_func=smooth),
                ShowPassingFlash(edge.copy().set_stroke(color=ORANGE,width=2.7).set_z_index(1),time_width=.28))
                for dot,edge in zip(dots,paths)),lag_ratio=.08),run_time=1.35)
            self.remove(*dots,dots)
        ring=Circle(.47,color=ORANGE,stroke_width=2.2).move_to(layers[1].node_group[0]).set_z_index(2)
        relu=ActivationPlot();sigmoid=ActivationPlot(sigmoid=True)
        def evaluate(plot,z,value,label,node,name):
            nonlocal result
            axes=plot.axes;fx=float(plot.fn(z))
            cursor=Dot(axes.c2p(z,0),radius=.052,color=ORANGE).set_z_index(6)
            vertical=DashedLine(axes.c2p(z,0),axes.c2p(z,max(.001,fx)),color=ORANGE,stroke_width=1.4)
            horizontal=DashedLine(axes.c2p(z,fx),axes.c2p(.001,fx),color=ORANGE,stroke_width=1.4)
            self.play(FadeIn(cursor),run_time=.25)
            self.play(cursor.animate.move_to(axes.c2p(z,fx)),FadeIn(vertical),run_time=.7)
            self.mark(name+'-on-curve',.55)
            self.play(cursor.animate.move_to(axes.c2p(0,fx)),FadeIn(horizontal),run_time=.5)
            next_result=MathTex(label,font_size=30,color=INK).move_to([4.25,-1.48,0])
            result=crossfade(result,next_result)
            self.mark(name+'-graph-result',.65)
            activate(node,value,'0.9933' if plot is sigmoid else f'{value:g}')
            self.play(FadeOut(cursor),FadeOut(vertical),FadeOut(horizontal),run_time=.25)
            self.mark(name+'-neuron-value',.65)
            traces.append(dict(z=z,activation=fx,on_curve=axes.c2p(z,fx).tolist(),on_y_axis=axes.c2p(0,fx).tolist(),
                               bounds=[float(plot.get_left()[0]),float(plot.get_right()[0]),float(plot.get_bottom()[1]),float(plot.get_top()[1])]))
        panel('The XOR question',r'1\oplus0=1')
        intro=Text('Exactly one input is active',font_size=20,color=GRAY).move_to([4.25,.25,0])
        self.play(FadeIn(intro),run_time=.3)
        say('Can this network recognize unequal inputs?');self.mark('architecture',1)
        activate(layers[0].node_group[0],1,'1');activate(layers[0].node_group[1],0,'0')
        say('First, evaluate the upper hidden neuron')
        panel('Hidden activation',r'z_1=x_1-x_2=1')
        self.play(FadeOut(intro),FadeIn(ring),run_time=.3)
        incoming=network.connective_layers[0].edges
        send(VGroup(incoming[0],incoming[2]),'input-hidden-start')
        self.mark('hidden-weighted-sums',.65)
        self.play(FadeIn(relu),run_time=.4)
        evaluate(relu,1,1,r'\mathrm{ReLU}(1)=1',layers[1].node_group[0],'relu-positive')
        say('A negative weighted sum is clipped to zero')
        panel('Hidden activation',r'z_2=x_2-x_1=-1')
        self.play(ring.animate.move_to(layers[1].node_group[1]),FadeOut(result),run_time=.4)
        result=VGroup()
        send(VGroup(incoming[1],incoming[3]),'input-hidden-second-start')
        evaluate(relu,-1,0,r'\mathrm{ReLU}(-1)=0',layers[1].node_group[1],'relu-negative')
        say('Both hidden values now feed the output')
        panel('Output activation',r'z=10(1)+10(0)-5=5')
        self.play(FadeOut(relu),FadeOut(result),ring.animate.move_to(layers[2].node_group[0]),run_time=.4)
        result=VGroup()
        send(network.connective_layers[1].edges,'hidden-output-start')
        self.mark('output-logit',.8)
        self.play(FadeIn(sigmoid),run_time=.4)
        evaluate(sigmoid,5,case['p'],r'\sigma(5)\approx0.9933',layers[2].node_group[0],'sigmoid')
        say('The prediction matches the XOR target')
        self.mark('prediction',.8)
        panel('Prediction',r'\hat y=0.9933')
        self.play(FadeOut(sigmoid),FadeOut(result),FadeOut(ring),run_time=.4)
        summary=VGroup(MathTex(r'\hat y>0.5\quad\Rightarrow\quad\mathrm{class}=1',font_size=26,color=INK).move_to([4.25,.55,0]),
                       Text('Matches the target',font_size=21,color='#23735a').move_to([4.25,-.05,0]),
                       MathTex(r'\mathcal L=-\ln\hat y\approx0.006715',font_size=24,color=GRAY).move_to([4.25,-1.15,0]))
        self.play(FadeIn(summary),run_time=.6)
        say('One forward pass. No weight update.');self.mark('completed-forward-pass',3)
        run=Path(config.media_dir).parent
        (run/'stages.json').write_text(json.dumps(self.stages,indent=2)+'\n')
        (run/'computation.json').write_text(json.dumps(data,indent=2)+'\n')
        layout=dict(nodes=locations,edges=[len(c.edges) for c in network.connective_layers],radius=.38,graphs=traces,
                    network_right=float(max(headers.get_right()[0],symbols.get_right()[0],
                        max(node.get_right()[0] for layer in layers for node in layer.node_group))),
                    panel_left=float(min(*panel_bounds,summary.get_left()[0],*(g['bounds'][0] for g in traces))),separator_x=1.45)
        (run/'layout.json').write_text(json.dumps(layout,indent=2)+'\n')
