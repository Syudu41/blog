"""A visual, numerically recorded 4–4–4 classification and learning example."""
import json
from pathlib import Path
import numpy as np
from manim import *
from manim_ml.neural_network import NeuralNetwork, FeedForwardLayer

ROOT=Path(__file__).resolve().parent
TEAL='#69d5c0';PINK='#e88ba8';AMBER='#f2c66d';MUTED='#a7b0bd';DIM='#36404b'


def prose(s,size=24,color=WHITE):
    return Tex(s,font_size=size,color=color)

def math(s,size=23,color=WHITE):
    return MathTex(s,font_size=size,color=color)

def number(x,n=2):
    return f'{x:.{n}f}' if abs(x)>=.5*10**(-n) else f'{0:.{n}f}'

def tile(values,side=.56):
    group=VGroup()
    for i,v in enumerate(values):
        group.add(Square(side_length=side/2,stroke_color=MUTED,stroke_width=.8,
            fill_color=interpolate_color(BLACK,WHITE,float(v)),fill_opacity=1)
            .move_to([(i%2-.5)*side/2,(.5-i//2)*side/2,0]))
    return group

class Visualization(Scene):
    def mark(self,key,hold=1):
        self.wait(hold/2)
        self.stages[key]=float(self.time)
        self.geometry[key]=dict(objects=[dict(name=n,bounds=[float(o.get_left()[0]),float(o.get_right()[0]),
            float(o.get_bottom()[1]),float(o.get_top()[1])]) for n,o in self.tracked if o in self.mobjects],
            values=self.current_state,rendered=self.read_rendered() if hasattr(self,'read_rendered') else {})
        self.wait(hold/2)

    def construct(self):
        self.camera.background_color=BLACK
        trace=json.loads((ROOT/'trace.json').read_text());snapshots=trace['snapshots'];initial=snapshots[0]
        self.stages={};self.geometry={};self.tracked=[];self.current_state={};self.signals=[];self.actual_readouts={}
        def track(name,obj):
            self.tracked.append((name,obj));return obj
        def add_named(name,obj):self.add(track(name,obj));return obj
        add_named('title',prose('Four pixels. Four possible patterns.',34).move_to([0,3.55,0]))
        add_named('subtitle',prose('Predict the pattern in a tiny grayscale image',23,MUTED).move_to([0,3.04,0]))
        image=tile(initial['example']['x'],1.05).move_to([-6.12,-.65,0])
        add_named('image',image)
        add_named('image-label',prose('Image',21).move_to([-6.12,.22,0]))
        add_named('pixel-range',math(r'0\leq x_i\leq1',18,MUTED).move_to([-6.12,-1.47,0]))
        add_named('pixel-order',prose('Row-major',17,MUTED).move_to([-6.12,-1.85,0]))
        # Actual native ManimML layer objects, laid out explicitly to reserve matrix space.
        xs=[-4.65,-.75,3.15];ys=[.08,-.67,-1.42,-2.17]
        layers=[FeedForwardLayer(4,node_radius=.235,node_color=WHITE,node_stroke_width=1.5,
                    rectangle_stroke_width=0,rectangle_fill_color=BLACK) for _ in range(3)]
        network=NeuralNetwork(layers,layer_spacing=2)
        for layer,x in zip(layers,xs):
            layer.surrounding_rectangle.set_opacity(0)
            for node,y in zip(layer.node_group,ys):
                node.move_to([x,y,0]).set_fill(BLACK,opacity=1).set_z_index(3)
        edges=[]
        for c in network.connective_layers:
            row_edges=VGroup(*(Line(a.get_center(),b.get_center(),buff=.25,stroke_width=1,color=DIM)
                for b in c.output_layer.node_group for a in c.input_layer.node_group))
            c.edges.become(row_edges).set_z_index(-1);edges.append(c.edges)
        self.network=network
        headers=VGroup(prose('Pixels',23).move_to([xs[0],.65,0]),
            prose('Hidden: ReLU',23).move_to([xs[1],.65,0]),
            prose('Class probabilities',23).move_to([4.3,.65,0]))
        pixel_indices=VGroup(*(math('x_'+str(i+1),18,MUTED).move_to([-5.17,y,0]) for i,y in enumerate(ys)))
        class_objects=VGroup();bar_bases=VGroup();bars=VGroup();prob_labels=VGroup()
        for k,(label,y) in enumerate(zip(trace['classes'],ys)):
            glyph=tile(trace['prototypes'][k],.37).move_to([3.92,y,0])
            name=prose(label,19,TEAL if k==0 else WHITE).move_to([5.05,y+.17,0])
            base=Rectangle(width=1.55,height=.105,stroke_width=0,fill_color=DIM,fill_opacity=.7).move_to([5.05,y-.14,0])
            class_objects.add(glyph,name);bar_bases.add(base)
            bars.add(Rectangle(width=.002,height=.105,stroke_width=0,fill_color=TEAL if k==0 else MUTED,
                fill_opacity=1).move_to(base.get_left()+[.001,0,0]))
            prob_labels.add(math(r'\cdots',20).move_to([6.28,y,0]))
        target=prose('Target: Vertical',20,TEAL).move_to([5.05,-2.65,0])
        # Exact values in the scene are rounded only for labels; all computations are recorded float64.
        matrix_groups=[];matrix_entries=[];bias_groups=[]
        def matrix_object(w,index):
            mat=Matrix([[number(v) for v in row] for row in w],element_to_mobject=lambda s:math(s,22),
                h_buff=.76,v_buff=.29,bracket_h_buff=.13,bracket_v_buff=.13)
            mat.move_to([(-2.7 if index==0 else 1.2),1.94,0])
            mat.get_brackets().set_color(WHITE)
            for entry,v in zip(mat.get_entries(),np.array(w).flat):entry.set_color(TEAL if v>=0 else PINK)
            return mat
        for k in range(2):
            mat=matrix_object(initial['params'][2*k],k);matrix_groups.append(mat);matrix_entries.append(mat.get_entries())
            label=math(r'W^{('+str(k+1)+r')}\quad\text{'+('pixel to hidden' if k==0 else 'hidden to class')+'}',21,MUTED)
            label.move_to([(-2.7 if k==0 else 1.2),2.65,0]);add_named(f'matrix-heading-{k}',label)
            bias=math(r'b^{('+str(k+1)+r')}=('+','.join(number(v) for v in initial['params'][2*k+1])+')',18,MUTED)
            bias.move_to([(-2.7 if k==0 else 1.2),1.1,0]);bias_groups.append(bias)
        legend=VGroup(prose('Weight sign',17,MUTED),math('+',21,TEAL),math('-',21,PINK),
            prose('width = magnitude',17,MUTED)).arrange(RIGHT,buff=.13).move_to([5.25,2.3,0])
        legend.scale_to_fit_width(3.0);add_named('legend',legend)
        add_named('model-size',prose('40 learned parameters',17,MUTED).move_to([5.25,1.72,0]))
        labels=[VGroup() for _ in range(3)]
        equation=VGroup();caption=VGroup();badge=VGroup()
        def message(formula,words,hold=1.7):
            nonlocal equation,caption
            new=math(formula,25).move_to([0,-2.94,0])
            if new.width>12.65:new.scale_to_fit_width(12.65)
            text=prose(words,23).move_to([0,-3.52,0])
            if text.width>12.7:text.scale_to_fit_width(12.7)
            self.play(FadeOut(equation),FadeOut(caption),run_time=.16)
            equation,caption=new,text
            self.play(FadeIn(equation),FadeIn(caption),run_time=.3)
            self.wait(hold)
        def node_values(layer,values):
            return VGroup(*(math(number(v,3 if layer==2 else 2),16 if layer==2 else 18,BLACK if v>.75 else WHITE)
                .move_to(node).set_z_index(5) for node,v in zip(layers[layer].node_group,values)))
        def fills(layer,values,scale=1):
            return [node.animate.set_fill(interpolate_color(BLACK,ManimColor(TEAL),min(.85,float(v)/scale*.85)),opacity=1)
                    for node,v in zip(layers[layer].node_group,values)]
        def edge_style(w,index):
            for edge,v in zip(edges[index],np.array(w).flat):
                edge.set_stroke(TEAL if v>=0 else PINK,width=.6+min(2.4,abs(v)*1.15),opacity=.34)
        def transmit(paths,reverse=False,key='forward'):
            self.signals.append(dict(key=key,time=float(self.time),reverse=reverse,count=len(paths)))
            dots=VGroup(*(Dot(radius=.035,color=AMBER if reverse else TEAL).move_to(e.get_end() if reverse else e.get_start()) for e in paths)).set_z_index(6)
            self.add(dots)
            self.play(*(MoveAlongPath(dot,edge.copy().reverse_points() if reverse else edge,rate_func=smooth)
                for dot,edge in zip(dots,paths)),run_time=1.15)
            self.remove(dots,*dots)
        def show_values(layer,values):
            nonlocal labels
            new=node_values(layer,values)
            self.play(FadeOut(labels[layer]),FadeIn(new),*fills(layer,values,scale=3 if layer==1 else 1),run_time=.55)
            labels[layer]=new
        def probabilities(case,run_time=.65):
            new_labels=VGroup(*(math(number(v,3),20,TEAL if i==0 else WHITE).move_to([6.28,ys[i],0]) for i,v in enumerate(case['p'])))
            nonlocal prob_labels
            newbars=VGroup()
            for i,p in enumerate(case['p']):
                width=max(.002,1.55*p)
                newbars.add(Rectangle(width=width,height=.105,stroke_width=0,fill_color=TEAL if i==0 else MUTED,fill_opacity=1)
                    .move_to(bar_bases[i].get_left()+[width/2,0,0]))
            self.play(Transform(bars,newbars),Transform(prob_labels,new_labels),run_time=run_time)
        def state(s):
            self.current_state=dict(step=s['step'],params=s['params'],x=s['example']['x'],h=s['example']['h'],p=s['example']['p'],loss=s['example']['loss'],test_correct=s['test_correct'])
        def replace_parameters(s):
            animations=[]
            for k in range(2):
                new=matrix_object(s['params'][2*k],k)
                animations.append(ReplacementTransform(matrix_groups[k],new))
                old=matrix_groups[k];matrix_groups[k]=new
                self.tracked=[(name,new if obj is old else obj) for name,obj in self.tracked]
                newbias=math(r'b^{('+str(k+1)+r')}=('+','.join(number(v) for v in s['params'][2*k+1])+')',18,MUTED).move_to(bias_groups[k])
                animations.append(ReplacementTransform(bias_groups[k],newbias))
                old=bias_groups[k];bias_groups[k]=newbias
                self.tracked=[(name,newbias if obj is old else obj) for name,obj in self.tracked]
                # Animate the exact new signed encoding, with no reordering of edge identities.
                for edge,value in zip(edges[k],np.array(s['params'][2*k]).flat):
                    animations.append(edge.animate.set_stroke(TEAL if value>=0 else PINK,width=.6+min(2.4,abs(value)*1.15),opacity=.34))
            self.play(*animations,run_time=.85)
        def dump():
            run=Path(config.media_dir).parent
            (run/'stages.json').write_text(json.dumps(self.stages,indent=2)+'\n')
            (run/'layout.json').write_text(json.dumps(self.geometry,indent=2)+'\n')
            (run/'signals.json').write_text(json.dumps(self.signals,indent=2)+'\n')
        def read_rendered():
            matrix_text=[[entry.get_tex_string() for entry in m.get_entries()] for m in matrix_groups]
            gaps=[]
            for m in matrix_groups:
                entries=m.get_entries()
                gaps.extend(float(entries[j+1].get_left()[0]-entries[j].get_right()[0]) for j in range(16) if j%4<3)
            return dict(matrix_entries=matrix_text,minimum_entry_gap=min(gaps),
                node_labels=[[m.get_tex_string() for m in group] for group in labels],
                probability_bar_values=[bar.width/1.55 for bar in bars],
                biases=[b.get_tex_string() for b in bias_groups],
                brackets=[m.get_brackets()[0].get_color().to_hex() for m in matrix_groups],
                edge_geometry=[dict(start=e.get_start().tolist(),end=e.get_end().tolist()) for group in edges for e in group],
                native_layer_types=[type(layer).__name__ for layer in layers])
        self.read_rendered=read_rendered
        # Static companion is the actual final trained model, not a separate concept illustration.
        if config.save_last_frame:
            final=snapshots[-1]
            self.add(network,headers,pixel_indices,class_objects,bar_bases,bars,prob_labels,target,*matrix_groups,*bias_groups)
            for k in range(2):matrix_groups[k].become(matrix_object(final['params'][2*k],k));edge_style(final['params'][2*k],k)
            for k,val in enumerate([final['example']['x'],final['example']['h'],final['example']['p']]):self.add(node_values(k,val))
            # Biases and probabilities also correspond to this exact checkpoint.
            replace_parameters(final);probabilities(final['example']);state(final)
            message(r'\hat y=\operatorname{softmax}(W^{(2)}\operatorname{ReLU}(W^{(1)}x+b^{(1)})+b^{(2)})',
                'A four-pixel image becomes a probability for each named pattern.',0)
            dump();return
        # Establish the problem before introducing any arithmetic.
        deferred=[obj for name,obj in self.tracked if name.startswith('matrix-heading') or name in ['legend','model-size']]
        self.remove(*deferred)
        intro_names=['image-label','pixel-range','pixel-order']
        intro_labels=[obj for name,obj in self.tracked if name in intro_names]
        saved=[obj.get_center().copy() for obj in intro_labels]
        for obj in intro_labels:obj.shift(RIGHT*3.62)
        image.scale(1.8).move_to([-2.5,-.65,0])
        intro_labels[0].move_to([-2.5,.65,0]);intro_labels[1].move_to([-2.5,-1.88,0]);intro_labels[2].move_to([-2.5,-2.25,0])
        self.play(FadeIn(class_objects),FadeIn(target),run_time=.7)
        message(r'x=(0.1,\,0.9,\,0.1,\,0.9)^{\mathsf T}',
            'Which pattern do these four grayscale pixels represent?',2.3)
        self.mark('problem',1.5)
        self.play(image.animate.scale(1/1.8).move_to([-6.12,-.65,0]),
            *(obj.animate.move_to(position) for obj,position in zip(intro_labels,saved)),run_time=1.1)
        self.play(*(FadeIn(obj) for obj in deferred),run_time=.4)
        for k in range(2):edge_style(initial['params'][2*k],k)
        self.play(FadeIn(network),FadeIn(headers),FadeIn(pixel_indices),FadeIn(bar_bases),FadeIn(bars),FadeIn(prob_labels),run_time=1)
        pixel_copies=VGroup(*(image[i].copy() for i in range(4)))
        self.add(pixel_copies)
        self.play(*(pixel.animate.scale(.6).move_to(layers[0].node_group[i]) for i,pixel in enumerate(pixel_copies)),run_time=1.3)
        self.play(FadeOut(pixel_copies),run_time=.25);show_values(0,initial['example']['x'])
        self.play(*(FadeIn(o) for o in matrix_groups+bias_groups),run_time=.9)
        for k,o in enumerate(matrix_groups):track(f'weight-matrix-{k}',o)
        for k,o in enumerate(bias_groups):track(f'bias-{k}',o)
        track('network',network);track('headers',headers);track('classes',class_objects);track('probabilities',prob_labels)
        message(r'W^{(1)},W^{(2)}\in\mathbb R^{4\times4},\qquad b^{(1)},b^{(2)}\in\mathbb R^4',
            'Each matrix row is one neuron\'s incoming weight vector.',2.3)
        state(initial);self.mark('architecture-and-weights',1.4)
        row1=SurroundingRectangle(VGroup(*matrix_groups[0].get_entries()[:4]),buff=.07,color=AMBER,stroke_width=1.5)
        ring=Circle(radius=.30,color=AMBER,stroke_width=1.8).move_to(layers[1].node_group[0])
        selected=VGroup(*(e.copy().set_stroke(AMBER,width=2.4,opacity=.8) for e in edges[0][:4]))
        self.play(Create(row1),Create(ring),FadeIn(selected),run_time=.6)
        transmit(edges[0][:4],key='pixel-to-selected-hidden')
        ex=initial['example'];w=np.array(initial['params'][0])[0];z=ex['z'][0]
        formula=r'z_1='+ '+'.join(r'('+number(a)+r')('+number(b,1)+r')' for a,b in zip(w,ex['x']))+r'+0.20\approx '+number(z,3)
        message(formula,'Multiply each pixel by its weight, then add the bias.',2.2)
        self.mark('selected-weight-vector',1)
        message(r'h_1=\operatorname{ReLU}(z_1)=\max(0,'+number(z,3)+')='+number(ex['h'][0],3),
            'The hidden neuron passes only the nonnegative part.',2)
        transmit(edges[0],key='all-pixels-to-hidden');show_values(1,ex['h'])
        self.play(FadeOut(row1),FadeOut(ring),FadeOut(selected),run_time=.4)
        message(r'z\approx ('+','.join(number(v,3) for v in ex['z'])+r')^{\mathsf T}\quad\longrightarrow\quad h=('+','.join(number(v,3) for v in ex['h'])+r')^{\mathsf T}',
            'ReLU clips the negative weighted sum to zero.',2.2)
        self.mark('hidden-activations',1)
        row2=SurroundingRectangle(VGroup(*matrix_groups[1].get_entries()[:4]),buff=.07,color=AMBER,stroke_width=1.5)
        self.play(Create(row2),run_time=.4);transmit(VGroup(*(e for idx,e in enumerate(edges[1]) if ex['h'][idx%4]>0)),key='hidden-to-class-logits')
        message(r'\ell=W^{(2)}h+b^{(2)}\approx ('+','.join(number(v,3) for v in ex['logits'])+r')^{\mathsf T}',
            'Output weights combine hidden features, not image pixels.',2)
        self.play(FadeOut(row2),run_time=.3);show_values(2,ex['p']);probabilities(ex)
        message(r'p_k=\frac{e^{\ell_k}}{\sum_j e^{\ell_j}},\qquad\sum_k p_k=1',
            'Each output is a probability for its named pattern.',2.5)
        self.mark('initial-prediction',1.5)
        loss=ex['loss']
        message(r'y=(1,0,0,0)^{\mathsf T},\qquad\mathcal L=-\ln p_{\rm Vertical}='+number(loss,4),
            'The target is Vertical. Anti-diagonal currently leads.',2.4)
        self.mark('cross-entropy',1)
        d=np.array(ex['p']);d[0]-=1
        message(r'\delta^{(2)}=p-y=('+','.join(number(v,3) for v in d)+r')^{\mathsf T}',
            'Backpropagation sends the prediction error toward the hidden layer.',2)
        transmit(edges[1],reverse=True,key='output-error-backward')
        message(r'\delta^{(1)}=((W^{(2)})^{\mathsf T}\delta^{(2)})\odot\mathbf1_{z>0}',
            'The inactive ReLU blocks its gradient; the other hidden paths remain.',2)
        transmit(VGroup(*(edge for j in range(4) if ex['z'][j]>0 for edge in edges[0][j*4:(j+1)*4])),reverse=True,key='hidden-gradient-backward')
        self.mark('backpropagation',1)
        gradient=ex['gradients'][0][0][1];old=initial['params'][0][0][1];new=snapshots[1]['params'][0][0][1]
        gval=ex['delta_hidden'][0]
        gradient_box=SurroundingRectangle(matrix_groups[0].get_entries()[1],buff=.05,color=AMBER,stroke_width=1.5)
        gradient_edge=edges[0][1].copy().set_stroke(AMBER,width=2.5,opacity=.9)
        self.play(Create(gradient_box),FadeIn(gradient_edge),run_time=.45)
        message(r'\frac{\partial\mathcal L}{\partial W^{(1)}_{1,2}}=\delta^{(1)}_1x_2=('+number(gval,5)+r')(0.9)\approx '+number(gradient,5),
            'One visible edge: how much would changing this weight change loss?',2.5)
        self.mark('selected-gradient',1)
        message(r'W^{(1)}_{1,2}\leftarrow '+number(old,5)+r'-0.08('+number(gradient,5)+r')\approx '+number(new,5),
            'SGD updates all 40 parameters together from the old gradients.',2.5)
        self.play(FadeOut(gradient_box),FadeOut(gradient_edge),run_time=.3)
        replace_parameters(snapshots[1]);state(snapshots[1]);self.mark('sgd-update',1)
        transmit(edges[0],key='replay-input-hidden');show_values(1,snapshots[1]['example']['h'])
        transmit(VGroup(*(e for idx,e in enumerate(edges[1]) if snapshots[1]['example']['h'][idx%4]>0)),key='replay-hidden-output');show_values(2,snapshots[1]['example']['p']);probabilities(snapshots[1]['example'])
        message(r'p_{\rm Vertical}: '+number(ex['p'][0],4)+r'\to '+number(snapshots[1]['example']['p'][0],4)+
            r',\qquad\mathcal L: '+number(loss,4)+r'\to '+number(snapshots[1]['example']['loss'],4),
            'Same image, updated network: the target becomes more likely.',2.5)
        self.mark('same-image-after-update',1)
        self.play(FadeOut(equation),FadeOut(caption),run_time=.35)
        # A compact, honest sampled loss plot supports the dominant persistent network.
        axes=Axes(x_range=[0,2048,512],y_range=[0,1.5,.5],x_length=4.0,y_length=.65,
            axis_config=dict(color=DIM,stroke_width=1,include_tip=False)).move_to([-3.7,-3.22,0])
        plot_title=prose('Loss on the same image',18,MUTED).move_to([-3.7,-2.7,0])
        xlabels=VGroup(math('0',16,MUTED).move_to(axes.c2p(0,0)+[0,-.16,0]),
            math('2048',16,MUTED).move_to(axes.c2p(2048,0)+[0,-.16,0]))
        ylabels=VGroup(math('0',16,MUTED).move_to(axes.c2p(0,0)+[-.2,0,0]),
            math('1.5',16,MUTED).move_to(axes.c2p(0,1.5)+[-.25,0,0]))
        self.play(FadeIn(axes),FadeIn(plot_title),FadeIn(xlabels),FadeIn(ylabels),run_time=.5)
        plotted=VGroup();metrics=VGroup();previous=None
        initial_point=axes.c2p(0,initial['example']['loss'])
        initial_dot=Dot(initial_point,radius=.035,color=TEAL);self.add(initial_dot);plotted.add(initial_dot);previous=initial_point
        for s in snapshots[1:]:
            if s['step']>1:
                replace_parameters(s);show_values(1,s['example']['h']);show_values(2,s['example']['p']);probabilities(s['example'])
                transmit(edges[1],key=f'checkpoint-{s["step"]}-forward')
            state(s)
            point=axes.c2p(s['step'],s['example']['loss']);dot=Dot(point,radius=.035,color=TEAL)
            if previous is not None:
                segment=Line(previous,point,color=TEAL,stroke_width=1.5);self.play(Create(segment),run_time=.22);plotted.add(segment)
            self.play(FadeIn(dot),run_time=.15);plotted.add(dot);previous=point
            next_metrics=VGroup(math(r'\text{SGD updates: }'+str(s['step'])+r'\qquad\mathcal L='+number(s['example']['loss'],4),23),
                prose(f'Held-out toy images: {s["test_correct"]} / 64 correct',21,MUTED)).arrange(DOWN,buff=.18).move_to([2.6,-3.16,0])
            self.play(FadeOut(metrics),FadeIn(next_metrics),run_time=.25);metrics=next_metrics
            self.mark('training-'+str(s['step']),1.7 if s['step']<2048 else 3)
        final_note=prose('Toy data; rounded labels. 128 training images; 64 held-out images.',18,MUTED).move_to([0,-3.83,0])
        self.play(FadeIn(final_note),run_time=.35)
        self.mark('complete-network',4)
        dump()
