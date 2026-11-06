"""MNIST CNN with native ManimML layers and coupled receptive-field volumes."""
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from manim import (ThreeDScene, VGroup, Group, Text, MathTex, DecimalNumber, Integer,
    ImageMobject, Rectangle, Polygon, Line, Dot, FadeIn, FadeOut, Create, Transform,
    LaggedStart, MoveAlongPath, ValueTracker, AnimationGroup, interpolate_color,
    ManimColor, WHITE, BLACK, LEFT, UP, DEGREES, config, linear, smooth)
import manim_ml
from manim_ml.neural_network import Convolutional2DLayer, MaxPooling2DLayer, FeedForwardLayer
from manim_ml.neural_network.layers.convolutional_2d_to_convolutional_2d import Filters, get_rotated_shift_vectors

ROOT=Path(__file__).resolve().parent
TRACE_SHA256='10495cd69b1ec51a77e20a38549296fb491e8bf72467f4af261e659e613f5f11'
TRAINING_SHA256='9a09dd13dd37c43fdde4c473cedd61bdb6576ed5cec6c569ac6e1b562634cce9'
BLUE='#58c4dd';ORANGE='#ff9f43';GRAY='#a8b1bd';LINE='#536779'


def text(words,size=24,color=WHITE):
    return Text(words,font='Liberation Sans',font_size=size,color=color)


def tex(source,size=28,color=WHITE):
    return MathTex(source,font_size=size,color=color)


def input_pixels(layer,values):
    """Place true grayscale pixels on the native layer's rotated input face."""
    corners=layer.feature_maps[0].get_corners_dict()
    tl=corners['top_left'].get_center();tr=corners['top_right'].get_center();bl=corners['bottom_left'].get_center()
    right=(tr-tl)/28;down=(bl-tl)/28
    pixels=VGroup()
    for row,col in np.argwhere(values>0):
        origin=tl+row*down+col*right
        color=ManimColor(np.full(3,float(values[row,col])))
        pixels.add(Polygon(origin,origin+right,origin+right+down,origin+down,
            stroke_width=0,fill_color=color,fill_opacity=1,shade_in_3d=False))
    return pixels


class Visualization(ThreeDScene):
    def mark(self,name,hold=1):
        self.wait(hold/2);self.stages[name]=float(self.time)
        layers=[]
        for i,layer in enumerate(self.layers):
            maps=getattr(layer,'feature_maps',[])
            layers.append(dict(name=self.names[i],type=type(layer).__name__,shape=self.shapes[i],
                center=layer.get_center().tolist(),maps=len(maps),nodes=[n.get_center().tolist() for n in getattr(layer,'node_group',[])],
                map_corners=[{k:v.get_center().tolist() for k,v in m.get_corners_dict().items()} for m in maps],
                bounds=[float(layer.get_left()[0]),float(layer.get_right()[0]),float(layer.get_bottom()[1]),float(layer.get_top()[1])]))
        projected=[]
        for m in self.mobjects:
            points=m.get_all_points()
            if len(points) and (m.width>0 or m.height>0):
                p=self.camera.project_points(points)
                projected.append([float(p[:,0].min()),float(p[:,0].max()),float(p[:,1].min()),float(p[:,1].max())])
        self.layouts[name]=dict(layers=layers,bounds=projected)
        self.wait(hold/2)

    def say(self,caption,metric):
        new=text(caption,21,GRAY).move_to([0,-2.92,0])
        if new.width>12.7:new.scale_to_fit_width(12.7)
        value=tex(metric,27,ORANGE).move_to([0,2.98,0])
        if value.width>12.8:value.scale_to_fit_width(12.8)
        self.play(FadeOut(self.caption),FadeOut(self.metric),run_time=.18)
        self.caption,self.metric=new,value
        self.play(FadeIn(new),FadeIn(value),run_time=.32)

    def clear_readout(self):
        if self.readout:
            self.play(FadeOut(self.readout),run_time=.25)
        self.readout=VGroup()

    def light(self,index,color=BLUE):
        layer=self.layers[index]
        if hasattr(layer,'feature_maps'):
            self.play(*(m.animate.set_color(color) for m in layer.feature_maps),run_time=.45)
        else:self.play(layer.animate.set_color(color),run_time=.45)

    def scan(self,source_index,target_index,key,channel,seconds,name,pool=False):
        source=self.layers[source_index];target=self.layers[target_index]
        if pool:
            a=SimpleNamespace(feature_maps=VGroup(source.feature_maps[channel]),cell_width=source.cell_width)
            b=SimpleNamespace(feature_maps=VGroup(target.feature_maps[channel]),cell_width=target.cell_width,
                filter_size=(2,2),filter_color=ORANGE,padding=(0,0))
            volume=Filters(a,b,cell_width=source.cell_width,show_grid_lines=True,stroke_width=1.6)
        else:
            volume=Filters(source,target,cell_width=source.cell_width,show_grid_lines=True,
                stroke_width=1.6,output_feature_map_to_connect=channel)
        volume.add(volume.input_rectangles,volume.connective_lines,volume.output_rectangles)
        volume.set_z_index(6)
        bases_in=[m.get_center().copy() for m in volume.input_rectangles]
        bases_out=[m.get_center().copy() for m in volume.output_rectangles]
        right,down=get_rotated_shift_vectors(source)
        out_right,out_down=get_rotated_shift_vectors(target)
        n=self.data[key].shape[1];stride=2 if pool else 1;padding=0 if pool else 1
        for window,base in zip(volume.input_rectangles,bases_in):window.move_to(base-padding*(right+down))
        volume.connective_lines.become(volume.make_connective_lines())
        route=[(r,c) for r in range(n) for c in (range(n) if r%2==0 else range(n-1,-1,-1))]
        tracker=ValueTracker(0)
        labels=VGroup(tex(f'c={channel}',24,ORANGE).move_to([-3.6,-2.05,0]),
            tex('i=',24,GRAY).move_to([-2,-2.05,0]),tex('j=',24,GRAY).move_to([-.5,-2.05,0]),
            tex('a=',24,BLUE).move_to([1.15,-2.05,0]))
        row_number=Integer(0,font_size=25,color=WHITE).move_to([-1.45,-2.05,0])
        col_number=Integer(0,font_size=25,color=WHITE).move_to([.05,-2.05,0])
        number=DecimalNumber(float(self.data[key][channel,0,0]),num_decimal_places=4,font_size=29,color=BLUE).move_to([2.35,-2.05,0])
        self.readout=VGroup(labels,row_number,col_number,number)
        self.play(FadeIn(self.readout),FadeIn(volume),run_time=.45)
        self.mark(name+'-origin',.9)
        self.stages[name+'-start']=float(self.time)
        def update(m):
            f=float(np.clip(tracker.get_value(),0,len(route)-1));i=int(f);j=min(i+1,len(route)-1);t=f-i
            r,c=np.array(route[i])*(1-t)+np.array(route[j])*t
            shift=(stride*r-padding)*down+(stride*c-padding)*right
            for window,base in zip(m.input_rectangles,bases_in):window.move_to(base+shift)
            for window,base in zip(m.output_rectangles,bases_out):window.move_to(base+r*out_down+c*out_right)
            m.connective_lines.become(m.make_connective_lines())
            ir,ic=route[i];value=float(self.data[key][channel,ir,ic])
            row_number.set_value(ir).move_to([-1.45,-2.05,0]);col_number.set_value(ic).move_to([.05,-2.05,0])
            number.set_value(value).move_to([2.35,-2.05,0])
            # Runtime positions and values are retained for independent geometry/media review.
            self.trace_samples.append(dict(time=float(self.time),scan=name,key=key,channel=channel,
                row=ir,col=ic,value=value,input_centers=[x.get_center().tolist() for x in m.input_rectangles],
                output_centers=[x.get_center().tolist() for x in m.output_rectangles],
                input_corners=[{k:v.get_center().tolist() for k,v in w.get_corners_dict().items()} for w in m.input_rectangles],
                output_corners=[{k:v.get_center().tolist() for k,v in w.get_corners_dict().items()} for w in m.output_rectangles],
                input_base=[x.tolist() for x in bases_in],output_base=[x.tolist() for x in bases_out],
                position=[float(r),float(c)],input_step_right=right.tolist(),input_step_down=down.tolist(),
                output_step_right=out_right.tolist(),output_step_down=out_down.tolist(),stride=stride,padding=padding))
        # Flag the changing number glyphs so Cairo refreshes them during filter motion.
        for value in (row_number,col_number,number):value.add_updater(lambda m:None)
        volume.add_updater(update);self.add(tracker)
        self.play(tracker.animate.set_value(len(route)-1),run_time=seconds,rate_func=linear)
        volume.clear_updaters()
        for value in (row_number,col_number,number):value.clear_updaters()
        self.mark(name,1.2)
        self.play(FadeOut(volume),run_time=.35);self.remove(tracker)
        self.clear_readout()

    def save_evidence(self):
        run=Path(config.media_dir).parent
        evidence=dict(trace_sha256=TRACE_SHA256,training_sha256=TRAINING_SHA256,
            parameter_counts=[0,40,0,296,0,0,3930,0],
            camera=dict(focal_distance=float(self.camera.get_focal_distance()),rotation_matrix=self.camera.get_rotation_matrix().tolist()),
            probabilities=[dict(class_id=k,p=p,width=float(bar.width),center=bar.get_center().tolist()) for k,(bar,p,y) in enumerate(self.output_bars)],
            samples=self.trace_samples,layer_style='native ManimML vector feature maps and Filters',
            color_meaning='blue planes depict layers; orange volumes depict receptive fields, not fabricated activations')
        for name,value in [('stages.json',self.stages),('layout.json',self.layouts),('detail.json',evidence)]:
            (run/name).write_text(json.dumps(value,indent=2)+'\n')

    def construct(self):
        self.camera.background_color=BLACK
        self.set_camera_orientation(focal_distance=100)
        assert hashlib.sha256((ROOT/'trace.npz').read_bytes()).hexdigest()==TRACE_SHA256
        assert hashlib.sha256((ROOT/'training.json').read_bytes()).hexdigest()==TRAINING_SHA256
        self.data=d=dict(np.load(ROOT/'trace.npz'));self.meta=json.loads((ROOT/'training.json').read_text())
        self.stages={};self.layouts={};self.trace_samples=[];self.readout=VGroup()
        manim_ml.config.three_d_config.rotation_angle=65*DEGREES
        self.names=['Input','Conv 1 + ReLU','Pool 1','Conv 2 + ReLU','Pool 2','Flatten','Dense','Softmax']
        self.shapes=[[1,28,28],[4,28,28],[4,14,14],[8,14,14],[8,7,7],[392],[10],[10]]
        cell=.102;spacing=.16
        style=dict(cell_width=cell,filter_spacing=spacing,color=BLUE,fill_opacity=.12,stroke_width=1.6)
        native=[Convolutional2DLayer(1,28,3,**style),Convolutional2DLayer(4,28,3,**style),
            MaxPooling2DLayer(kernel_size=2,stride=2,**{k:v for k,v in style.items() if k!='fill_opacity'}),
            Convolutional2DLayer(8,14,3,**style),
            MaxPooling2DLayer(kernel_size=2,stride=2,**{k:v for k,v in style.items() if k!='fill_opacity'})]
        for i,layer in enumerate(native):layer.construct_layer(native[i-1] if i else None,native[i+1] if i<4 else None)
        xs=[-6.0,-4.1,-2.15,.1,2.35,3.85,4.85,6.05]
        for layer,x in zip(native,xs):layer.move_to([x,-.08,0])
        for layer in native:
            for plane in layer.feature_maps:
                # Invisible grid strokes do not need hundreds of renderable line objects.
                rectangle=plane.exterior_rectangle if hasattr(plane,'exterior_rectangle') else plane
                rectangle[1].set_opacity(0)
        native[0].feature_maps[0].exterior_rectangle.rectangle.set_fill(BLACK,opacity=1)
        self.pixels=input_pixels(native[0],d['x'][0]);native[0].feature_maps[0].add(self.pixels)
        flat=VGroup(Rectangle(width=.12,height=2.5,stroke_color=BLUE,stroke_width=1.5).move_to([xs[5],-.08,0]))
        self.feature_bands=VGroup()
        maximum=float(d['p2'].max())
        for i,value in enumerate(d['flat']):
            color=interpolate_color(ManimColor('#101923'),ManimColor(BLUE),float(value)/maximum)
            self.feature_bands.add(Line([xs[5]-.043,1.16-i*2.48/392,0],[xs[5]+.043,1.16-i*2.48/392,0],color=color,stroke_width=.6))
        dense=FeedForwardLayer(10,node_radius=.073,node_spacing=.25,node_color=BLUE,
            rectangle_color=WHITE,rectangle_fill_color=BLACK,rectangle_stroke_width=1.4,node_stroke_width=1.7)
        dense.construct_layer(None,None);dense.move_to([xs[6],-.08,0]);dense.node_group.set_z_index(3)
        output=VGroup();self.output_bars=[]
        for k,p in enumerate(d['probabilities']):
            y=1.045-k*.25
            label=tex(str(k),18,GRAY).move_to([5.6,y,0])
            rail=Line([5.82,y,0],[6.7,y,0],color=LINE,stroke_width=1)
            bar=Rectangle(width=.002,height=.095,stroke_width=0,fill_color=BLUE,fill_opacity=1).move_to([5.821,y,0])
            output.add(label,rail,bar);self.output_bars.append((bar,float(p),y))
        self.layers=[*native,flat,dense,output]
        headers=VGroup();settings=[r'x/255',r'3\times3,\ s=1,\ p=1',r'2\times2,\ s=2',r'3\times3,\ s=1,\ p=1',r'2\times2,\ s=2',r'0\ \mathrm{params}',r'\mathrm{linear}',r'0\ \mathrm{params}']
        for i,(name,shape,x,spec) in enumerate(zip(self.names,self.shapes,xs,settings)):
            label=text(name,21).move_to([x,2.45,0])
            limit=.88 if i>=5 else 1.9
            if label.width>limit:label.scale_to_fit_width(limit)
            dim=tex(r'\times'.join(map(str,shape)),25,BLUE).move_to([x,2.05,0])
            if dim.width>1.85:dim.scale_to_fit_width(1.85)
            setting=tex(spec,19,GRAY).move_to([x,1.67,0])
            limit=1.05 if i>=5 else 1.9
            if setting.width>limit:setting.scale_to_fit_width(limit)
            headers.add(label,dim,setting)
        title=text('MNIST / through a convolutional network',32).move_to([-6.5,3.58,0],aligned_edge=LEFT)
        self.add(title,text('TensorQuill',16,GRAY).move_to([5.9,3.58,0]),headers,*self.layers)
        self.caption=VGroup();self.metric=VGroup()
        self.say('Orange volumes connect receptive fields to their output locations.',r'4266\ \mathrm{learned\ parameters}\qquad y=7')
        if config.save_last_frame:
            self.add(self.feature_bands)
            for k,node in enumerate(reversed(dense.node_group)):node.set_fill(BLUE,opacity=.85 if k==int(d['logits'].argmax()) else .12)
            for bar,p,y in self.output_bars:bar.stretch_to_fit_width(max(.002,.88*p)).move_to([5.82+max(.002,.88*p)/2,y,0])
            self.final_summary(animate=False);self.mark('complete-network',.1);self.save_evidence();return
        self.mark('architecture',2.7)
        self.say('Each filter reuses its weights across the image.',r'\mathrm{Conv\ 1:}\quad40\ \mathrm{params}\qquad a_{\max}='+f'{float(d["a1"].max()):.4f}')
        self.scan(0,1,'a1',0,10.0,'convolution-1')
        # The first filter's detailed scan establishes the operation; other filters
        # are highlighted in turn without pretending they share the same values.
        for channel in (1,2,3):
            native[1].feature_maps[channel].set_color(ORANGE)
            self.mark(f'conv1-channel-{channel}',.45)
            native[1].feature_maps[channel].set_color(BLUE)
        self.mark('four-channels',1)
        self.say('Pool each channel independently. A local maximum becomes one output.',
            r'\mathrm{Pool\ 1:}\quad28\times28\to14\times14\qquad\max(p_{0,:,:})='+f'{float(d["p1"][0,12,5]):.4f}')
        self.scan(1,2,'p1',0,4.5,'pooling-1',pool=True)
        self.say('This receptive field spans all four incoming channels.',
            r'\mathrm{Conv\ 2:}\quad296\ \mathrm{params}\qquad a_{\max}='+f'{float(d["a2"].max()):.4f}')
        self.scan(2,3,'a2',0,6.0,'convolution-2')
        for channel in range(1,8):
            native[3].feature_maps[channel].set_color(ORANGE)
            self.mark(f'conv2-channel-{channel}',.23)
            native[3].feature_maps[channel].set_color(BLUE)
        self.mark('eight-channels',1)
        self.say('The channel count stays eight; each spatial side is halved.',
            r'\mathrm{Pool\ 2:}\quad8\times14\times14\to8\times7\times7')
        self.scan(3,4,'p2',0,3.5,'pooling-2',pool=True)
        self.say('Unfold the pooled stack into one feature vector.',r'\mathrm{Flatten:}\quad8\cdot7\cdot7=392\ \mathrm{values}')
        self.play(FadeIn(self.feature_bands),run_time=.9);self.mark('flatten',1.6)
        self.say('Every class score combines the same pooled feature vector.',
            r'\mathrm{Dense:}\quad392\times10+10=3930\ \mathrm{params}\qquad\ell_7='+f'{float(d["logits"][7]):.4f}')
        fan=VGroup(*(Line(flat.get_right(),node.get_left(),color=GRAY,stroke_width=.7) for node in dense.node_group))
        self.add(fan);dots=VGroup(*(Dot(edge.get_start(),radius=.025,color=ORANGE) for edge in fan));self.add(dots)
        self.play(LaggedStart(*(MoveAlongPath(dot,edge) for dot,edge in zip(dots,fan)),lag_ratio=.05),run_time=1.5)
        self.remove(dots,*dots)
        self.play(*(node.animate.set_fill(BLUE,opacity=.85 if k==int(d['logits'].argmax()) else .12) for k,node in enumerate(reversed(dense.node_group))),run_time=.6)
        self.mark('dense',1.6)
        self.say('Normalize the logits into digit probabilities.',r'p_7='+f'{float(d["probabilities"][7])*100:.4f}'+r'\%\qquad\hat y=7')
        self.play(*(bar.animate.stretch_to_fit_width(max(.002,.88*p)).move_to([5.82+max(.002,.88*p)/2,y,0]) for bar,p,y in self.output_bars),run_time=1)
        self.final_summary();self.mark('complete-network',4.0);self.save_evidence()

    def final_summary(self,animate=True):
        meta=self.meta
        summary=VGroup(text('Prediction',18,GRAY).move_to([-4.1,-1.95,0]),
            tex(r'7\quad(99.9989\%)',30,BLUE).move_to([-4.1,-2.38,0]),
            text('Cross-entropy',18,GRAY).move_to([0,-1.95,0]),
            tex(r'1.0921\times10^{-5}',29,BLUE).move_to([0,-2.38,0]),
            text('Test accuracy',18,GRAY).move_to([4.1,-1.95,0]),
            tex(f'{meta["test"]["accuracy"]*100:.2f}'+r'\%',30,BLUE).move_to([4.1,-2.38,0]))
        if animate:self.play(FadeIn(summary),run_time=.8)
        else:self.add(summary)
