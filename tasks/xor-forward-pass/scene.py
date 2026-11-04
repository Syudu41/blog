"""One XOR forward pass, with graphical activation-function evaluation."""
import json
from pathlib import Path
import numpy as np
from manim import (Scene, VGroup, Text, MathTex, Circle, Dot, Line, DashedLine,
                   Rectangle, SurroundingRectangle, Axes, Arrow, FadeIn, FadeOut,
                   TransformFromCopy, AnimationGroup, MoveAlongPath, ShowPassingFlash,
                   interpolate_color, ManimColor, WHITE, UP, RIGHT, config, smooth)
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


class FunctionGraph(VGroup):
    def __init__(self,center,name,sigmoid=False):
        super().__init__()
        self.sigmoid=sigmoid
        box=Rectangle(width=2.05,height=1.67,stroke_color='#d1e1e9',stroke_width=1,
                      fill_color=WHITE,fill_opacity=1).move_to(center).set_z_index(1)
        xr=[-6,6,3] if sigmoid else [-1.4,1.4,1]
        self.axes=Axes(x_range=xr,y_range=[0,1.2,.5],x_length=1.55,y_length=.88,
                       axis_config={'color':GRAY,'stroke_width':1.2,'include_tip':False}).move_to(np.array(center)+[0,-.08,0]).set_z_index(2)
        self.fn=(lambda z:1/(1+np.exp(-z))) if sigmoid else (lambda z:max(0,z))
        self.curve=self.axes.plot(self.fn,x_range=[-6,6,.08] if sigmoid else [-1.35,1.15,.02],
                                  color=BLUE,stroke_width=2.5,use_smoothing=False).set_z_index(3)
        header=MathTex(name,font_size=21,color=INK).move_to(np.array(center)+[0,.63,0]).set_z_index(4)
        xlabel=MathTex('z',font_size=16,color=GRAY).move_to(self.axes.c2p(xr[1],0)+[.11,.06,0]).set_z_index(4)
        ylabel=MathTex('a',font_size=16,color=GRAY).move_to(self.axes.c2p(0,1.2)+[-.11,.07,0]).set_z_index(4)
        self.result=Dot(np.array(center)+[0,-.65,0],radius=.001).set_opacity(0).set_z_index(5)
        self.box=box
        self.add(box,self.axes,self.curve,header,xlabel,ylabel,self.result)


class Visualization(Scene):
    def mark(self,name,duration=.6):
        self.wait(duration/2);self.stages[name]=float(self.time);self.wait(duration/2)

    def construct(self):
        self.stages={};data=compute();case=data['cases'][2]
        title=Text('XOR: inside a forward pass',font_size=34,weight='BOLD',color=INK).move_to([0,3.55,0])
        input_header=MathTex(r'x=(1,0),\quad y=1',font_size=28,color=INK).move_to([-4.6,2.15,0])
        input_note=Text('One input · chosen weights',font_size=16,color=GRAY).move_to([-4.6,1.65,0])
        layers=[FeedForwardLayer(n,node_radius=.29,node_spacing=2.7,node_color=BLUE,
                                node_stroke_width=2.2,rectangle_stroke_width=1,
                                rectangle_fill_color=WHITE) for n in (2,2,1)]
        net=NeuralNetwork(layers,layer_spacing=3.8)
        locations=[[[-4.8,.4,0],[-4.8,-2.3,0]],[[0,.4,0],[0,-2.3,0]],[[4.7,-.9,0]]]
        for layer,positions in zip(layers,locations):
            for node,point in zip(layer.node_group,positions):
                node.move_to(point).set_fill(WHITE,opacity=1).set_z_index(3)
            layer.surrounding_rectangle.become(SurroundingRectangle(layer.node_group,buff=.16,
                              color='#b9d1dd',stroke_width=1,fill_opacity=0)).set_z_index(-3)
        for connection in net.connective_layers:
            paths=VGroup(*(Line(a.get_center(),b.get_center(),buff=.29,color='#b5cbd7',stroke_width=1.2)
                           for a in connection.input_layer.node_group for b in connection.output_layer.node_group))
            connection.edges.become(paths).set_z_index(-2)
        layer_labels=VGroup(*(Text(name,font_size=21,color=INK).move_to([x,-2.9,0])
                             for name,x in [('Input layer',-4.8),('Hidden layer',0),('Output layer',4.7)]))
        self.add(title,input_header,input_note,net,layer_labels)
        graphs=[FunctionGraph([0,2.05,0],r'h_1=\mathrm{ReLU}(z_1)'),
                FunctionGraph([0,-1.02,0],r'h_2=\mathrm{ReLU}(z_2)'),
                FunctionGraph([4.7,1.30,0],r'\hat y=\sigma(z)',sigmoid=True)]
        for graph in graphs:self.add(graph)
        graph_links=VGroup(*(Arrow(graph.get_bottom()+[0,-.03,0],node.get_top()+[0,.03,0],
                                    buff=.03,stroke_width=1,color='#8ca9b9',max_tip_length_to_length_ratio=.14)
                            for graph,node in zip(graphs,[*layers[1].node_group,*layers[2].node_group])))
        self.add(graph_links)
        caption=VGroup()
        def say(words,formula=None):
            nonlocal caption
            text=Text(words,font_size=21,color=INK).move_to([0,-3.28,0])
            parts=[text]
            if formula:parts.append(MathTex(formula,font_size=25,color=INK).move_to([0,-3.72,0]))
            next_group=VGroup(*parts)
            self.play(FadeOut(caption),FadeIn(next_group),run_time=.3)
            caption=next_group
        def node_value(node,value,text):
            label=MathTex(text,font_size=23,color=INK).move_to(node).set_z_index(5)
            self.play(node.animate.set_fill(interpolate_color(WHITE,BLUE,.55*value),opacity=1),FadeIn(label),run_time=.4)
            return label
        def send(index):
            edges=net.connective_layers[index].edges
            dots=VGroup(*(Dot(radius=.045,color=ORANGE).move_to(edge.get_start()) for edge in edges)).set_z_index(4)
            self.add(dots)
            self.play(AnimationGroup(*(AnimationGroup(MoveAlongPath(dot,edge,rate_func=smooth),
                ShowPassingFlash(edge.copy().set_stroke(color=ORANGE,width=3).set_z_index(2),time_width=.25))
                for dot,edge in zip(dots,edges)),lag_ratio=.10),run_time=1.7)
            self.remove(*dots,dots)
        def evaluate(graph,z,result,formula,node,name):
            axes=graph.axes;fx=graph.fn(z)
            self.play(graph.box.animate.set_stroke(color=ORANGE,width=2),run_time=.25)
            cursor=Dot(axes.c2p(0,0),radius=.045,color=ORANGE).set_z_index(6)
            x_tag=MathTex(f'{z:g}',font_size=18,color=ORANGE).move_to(axes.c2p(z,0)+[0,-.16,0]).set_z_index(6)
            vertical=DashedLine(axes.c2p(z,0),axes.c2p(z,max(fx,.001)),color=ORANGE,stroke_width=1.3).set_z_index(5)
            horizontal=DashedLine(axes.c2p(z,fx),axes.c2p(.001,fx),color=ORANGE,stroke_width=1.3).set_z_index(5)
            self.add(cursor)
            self.play(cursor.animate.move_to(axes.c2p(z,0)),FadeIn(x_tag),run_time=.65)
            self.play(cursor.animate.move_to(axes.c2p(z,fx)),FadeIn(vertical),run_time=.8)
            self.mark(name+'-on-curve',.55)
            self.play(cursor.animate.move_to(axes.c2p(0,fx)),FadeIn(horizontal),FadeOut(x_tag),run_time=.65)
            result_label=MathTex(formula,font_size=19,color=INK).move_to(graph.result).set_z_index(6)
            self.play(FadeIn(result_label),run_time=.3)
            self.mark(name+'-graph-result',.7)
            text='0.9933' if graph.sigmoid else f'{result:g}'
            label=MathTex(text,font_size=22 if graph.sigmoid else 25,color=INK).move_to(node).set_z_index(6)
            if graph.sigmoid:label.scale_to_fit_width(.48)
            self.play(TransformFromCopy(result_label,label),
                      node.animate.set_fill(interpolate_color(WHITE,BLUE,.55*result),opacity=1),run_time=.8)
            self.play(FadeOut(cursor),FadeOut(vertical),FadeOut(horizontal),
                      graph.box.animate.set_stroke(color='#d1e1e9',width=1),run_time=.25)
            self.mark(name+'-neuron-value',.65)
        say('Follow one input through the XOR network')
        self.mark('architecture',1.2)
        node_value(layers[0].node_group[0],1,'1');node_value(layers[0].node_group[1],0,'0')
        say('Inputs form two weighted sums',r'z_1=x_1-x_2=1,\qquad z_2=x_2-x_1=-1')
        self.stages['input-hidden-start']=float(self.time);send(0);self.mark('hidden-weighted-sums',1.8)
        say('The first ReLU passes a positive value',r'h_1=\max(0,1)=1')
        evaluate(graphs[0],1,1,r'\mathrm{ReLU}(1)=1',layers[1].node_group[0],'relu-positive')
        say('The second ReLU clips a negative value to zero',r'h_2=\max(0,-1)=0')
        evaluate(graphs[1],-1,0,r'\mathrm{ReLU}(-1)=0',layers[1].node_group[1],'relu-negative')
        say('Hidden activations feed the output neuron',r'z=10h_1+10h_2-5')
        # Show the contribution weights without cluttering the input crossings.
        weights=VGroup(*(MathTex('10',font_size=22,color=GRAY).move_to(edge.get_center()+[0,.16,0]).set_z_index(5)
                         for edge in net.connective_layers[1].edges))
        self.play(FadeIn(weights),run_time=.3)
        self.stages['hidden-output-start']=float(self.time);send(1)
        say('The weighted sum becomes the sigmoid input',r'z=10(1)+10(0)-5=5')
        self.mark('output-logit',1.5)
        evaluate(graphs[2],5,case['p'],r'\sigma(5)\approx0.9933',layers[2].node_group[0],'sigmoid')
        say('The prediction matches the XOR target',r'\hat y=0.9933>0.5\quad\Longrightarrow\quad\mathrm{class}=1=y')
        self.mark('prediction',1.8)
        loss=MathTex(r'\mathcal L=-\ln(\hat y)\approx0.006715',font_size=22,color=INK).move_to([4.7,-1.95,0])
        loss_title=Text('Loss after prediction',font_size=16,color=GRAY).move_to([4.7,-1.55,0])
        self.play(FadeIn(loss_title),FadeIn(loss),run_time=.6)
        say('One forward pass is complete; the weights stay fixed')
        self.mark('completed-forward-pass',3)
        run=Path(config.media_dir).parent
        (run/'stages.json').write_text(json.dumps(self.stages,indent=2)+'\n')
        (run/'computation.json').write_text(json.dumps(data,indent=2)+'\n')
        layout=dict(nodes=locations,edges=[len(c.edges) for c in net.connective_layers],
                    radius=.29,graphs=[dict(center=list(g.get_center()),bounds=[float(g.get_left()[0]),float(g.get_right()[0]),float(g.get_bottom()[1]),float(g.get_top()[1])],
                    z=z,activation=float(g.fn(z)),on_curve=g.axes.c2p(z,g.fn(z)).tolist(),
                    on_y_axis=g.axes.c2p(0,g.fn(z)).tolist()) for g,z in zip(graphs,[1,-1,5])])
        (run/'layout.json').write_text(json.dumps(layout,indent=2)+'\n')
