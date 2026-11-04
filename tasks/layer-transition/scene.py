"""A simple computed forward pass using ManimML's feed-forward primitives."""
import json
from pathlib import Path
import numpy as np
from manim import (Scene, Text, MathTex, VGroup, Dot, FadeIn, FadeOut,
                   ReplacementTransform, AnimationGroup, MoveAlongPath,
                   ShowPassingFlash, interpolate_color, ManimColor, WHITE,
                   DOWN, UP, config, smooth)
from manim_ml.neural_network import FeedForwardLayer, NeuralNetwork

BLUE=ManimColor('#1767a6')
ORANGE='#cf6416'
INK='#18334b'


def compute():
    x=np.array([.8,.35,.6])
    w1=np.array([[.5,.3,.2],[-.4,.8,.5],[.7,-.2,.4],[.2,.4,-.1]])
    b1=np.array([.05,.1,-.05,.15])
    h=np.maximum(w1@x+b1,0)
    w2=np.array([[.8,-.3,.6,.2],[-.4,.7,.1,.5]])
    b2=np.array([-.1,.05]);y=1/(1+np.exp(-(w2@h+b2)))
    return dict(x=x,w1=w1,b1=b1,h=h,w2=w2,b2=b2,y=y)


class Visualization(Scene):
    def mark(self,name,duration=.5):
        self.wait(duration/2);self.stages[name]=float(self.time);self.wait(duration/2)

    def construct(self):
        self.stages={};data=compute()
        title=Text('Input → hidden → output',font_size=36,weight='BOLD',color=INK).move_to([0,3.15,0])
        legend=Text('Orange: signal flow     Blue: activation strength',font_size=20,color='#536c7f').move_to([0,2.55,0])
        layers=[FeedForwardLayer(n,node_radius=.28,node_spacing=.83,
                                rectangle_fill_color=WHITE,rectangle_stroke_width=0,
                                node_color=BLUE,node_stroke_width=2.5)
                for n in (3,4,2)]
        network=NeuralNetwork(layers,layer_spacing=3.4)
        network.scale_to_fit_width(10.8).move_to([0,-.05,0])
        for layer in layers:
            layer.surrounding_rectangle.set_fill(opacity=0)
            layer.node_group.set_z_index(2)
            for node in layer.node_group:node.set_fill(WHITE,opacity=1)
        for connection in network.connective_layers:
            connection.edges.set_stroke(color='#c7d6e1',width=1.5).set_z_index(-2)
        labels=VGroup(*(Text(name,font_size=25,color=INK).move_to([layer.get_center()[0],-2.40,0])
                        for name,layer in zip(('Input layer','Hidden layer','Output layer'),layers)))
        caption=Text('A forward pass, one layer at a time',font_size=23,color=INK).move_to([0,-3.05,0])
        note=Text('Fixed illustrative weights · ReLU hidden layer · Sigmoid outputs',font_size=16,color='#607587').move_to([0,-3.65,0])
        self.add(title,legend,network,labels,caption,note)
        values=[]
        for layer,key in zip(layers,('x','h','y')):
            group=VGroup(*(MathTex(f'{value:.2f}',font_size=21,color=INK).move_to(node)
                           for node,value in zip(layer.node_group,data[key]))).set_z_index(4)
            values.append(group)
        def say(text):
            nonlocal caption
            next_caption=Text(text,font_size=23,color=INK).move_to(caption)
            self.play(FadeOut(caption,shift=UP*.06),FadeIn(next_caption,shift=UP*.06),run_time=.35)
            caption=next_caption
        def activate(index,key):
            # All example activations lie in [0,1], so one intensity scale is
            # shared by input, hidden and output layers.
            self.play(*(node.animate.set_fill(interpolate_color(WHITE,BLUE,.65*float(value)),opacity=1)
                        for node,value in zip(layers[index].node_group,data[key])),
                      FadeIn(values[index],shift=DOWN*.06),run_time=.65)
        def send(index):
            paths=network.connective_layers[index].edges
            dots=VGroup(*(Dot(radius=.045,color=ORANGE).move_to(edge.get_start()) for edge in paths)).set_z_index(3)
            self.add(dots)
            self.play(AnimationGroup(*(AnimationGroup(
                MoveAlongPath(dot,edge,rate_func=smooth),
                ShowPassingFlash(edge.copy().set_stroke(color=ORANGE,width=3).set_z_index(1),time_width=.20))
                for dot,edge in zip(dots,paths)),lag_ratio=.035),run_time=1.8)
            self.remove(*dots,dots)
        self.mark('network-ready',.5)
        say('Inputs enter the network')
        activate(0,'x');self.mark('input-activations',.6)
        say('Inputs travel to the hidden layer')
        self.stages['input-hidden-start']=float(self.time)
        send(0);self.mark('signals-arrive-hidden',.2)
        say('Hidden neurons combine the inputs')
        activate(1,'h');self.mark('hidden-activations',.7)
        say('Hidden activations travel to the output')
        self.stages['hidden-output-start']=float(self.time)
        send(1);self.mark('signals-arrive-output',.2)
        say('Outputs receive the hidden activations')
        activate(2,'y');self.mark('output-activations',1.0)
        say('One forward pass is complete')
        self.mark('completed-forward-pass',1.7)
        self.play(*(FadeOut(value) for value in values),
                  *(node.animate.set_fill(WHITE,opacity=1) for layer in layers for node in layer.node_group),run_time=.8)
        say('A forward pass, one layer at a time');self.mark('reset',.5)
        run=Path(config.media_dir).parent
        layout=dict(nodes=[[node.get_center().tolist() for node in layer.node_group] for layer in layers],
                    edges=[len(c.edges) for c in network.connective_layers],
                    node_radius=float(layers[0].node_group[0].width/2),
                    label_y=-2.40)
        (run/'layout.json').write_text(json.dumps(layout,indent=2)+'\n')
        (run/'stages.json').write_text(json.dumps(self.stages,indent=2)+'\n')
        (run/'computation.json').write_text(json.dumps({k:v.tolist() for k,v in data.items()},indent=2)+'\n')
