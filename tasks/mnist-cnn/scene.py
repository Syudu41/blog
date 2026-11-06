"""An original, numerically grounded MNIST CNN explanation on a black canvas."""
import hashlib
import json
from pathlib import Path

import numpy as np
from manim import (Scene, Group, VGroup, Text, MathTex, ImageMobject, Rectangle,
    RoundedRectangle, Line, Arrow, Dot, FadeIn, FadeOut, Transform,
    TransformFromCopy, Create, LaggedStart, ValueTracker, SurroundingRectangle,
    interpolate_color, ManimColor, WHITE, BLACK, LEFT, RIGHT, UP, DOWN, config,
    smooth, linear)

ROOT = Path(__file__).resolve().parent
TRACE_SHA256 = '10495cd69b1ec51a77e20a38549296fb491e8bf72467f4af261e659e613f5f11'
TRAINING_SHA256 = '9a09dd13dd37c43fdde4c473cedd61bdb6576ed5cec6c569ac6e1b562634cce9'
CYAN = '#55d9ec'
AMBER = '#ffbf69'
VIOLET = '#b59aff'
MUTED = '#9aa8bc'
BORDER = '#344253'


def load_trace():
    assert hashlib.sha256((ROOT / 'trace.npz').read_bytes()).hexdigest() == TRACE_SHA256
    return dict(np.load(ROOT / 'trace.npz'))


def prose(text, size=24, color=WHITE):
    return Text(text, font='Liberation Sans', font_size=size, color=color)


def math(text, size=30, color=WHITE):
    return MathTex(text, font_size=size, color=color)


def rgb(values, scale=1, color=CYAN, grayscale=False):
    values = np.clip(np.asarray(values) / max(float(scale), 1e-12), 0, 1)
    if grayscale:
        return np.repeat((values[..., None] * 255).astype(np.uint8), 3, axis=2)
    base = np.array([5, 11, 18])
    high = np.array(ManimColor(color).to_rgb()) * 255
    return (base + values[..., None] * (high-base)).astype(np.uint8)


def texture(values, scale=1, color=CYAN, grayscale=False):
    pixels = rgb(values, scale, color, grayscale)
    # Equal raster dimensions allow smooth transforms between 28/14/7-cell maps.
    return np.repeat(np.repeat(pixels, 112//len(values), axis=0), 112//len(values), axis=1)


class Tile(Group):
    def __init__(self, values, width, center, scale=1, color=CYAN, grayscale=False):
        super().__init__()
        self.values = np.array(values)
        self.n = len(values)
        self.side = width
        self.scale_value = scale
        self.tint = color
        self.grayscale = grayscale
        self.image = ImageMobject(texture(values, scale, color, grayscale)).set_resampling_algorithm(0)
        self.image.set_width(width).move_to(center)
        self.frame = Rectangle(width=width, height=width, stroke_color=color,
                               stroke_width=1.2).move_to(center)
        self.add(self.image, self.frame)

    def point(self, row, col):
        return self.image.get_center() + np.array([(col/self.n-.5)*self.side,
                                                   (.5-row/self.n)*self.side, 0])

    def window(self, row, col, size, color=AMBER):
        return Rectangle(width=self.side/self.n*size, height=self.side/self.n*size,
            stroke_color=color, stroke_width=2.5, fill_opacity=.08, fill_color=color
            ).move_to(self.point(row+size/2, col+size/2)).set_z_index(5)


def matrix(values, center, side=1.85, size=23, tint=CYAN):
    group = VGroup()
    rows, cols = values.shape
    for r in range(rows):
        for c in range(cols):
            position = np.array(center)+[(c-(cols-1)/2)*side/cols,
                                        ((rows-1)/2-r)*side/rows, 0]
            cell = Rectangle(width=side/cols, height=side/rows,
                             stroke_color=BORDER, stroke_width=1,
                             fill_color='#101923', fill_opacity=1).move_to(position)
            display = 0.0 if abs(values[r,c]) < .005 else values[r,c]
            label = math(f'{display:.2f}', size, AMBER if display<0 else tint).move_to(position)
            if label.width > side/cols*.87:
                label.scale_to_fit_width(side/cols*.87)
            group.add(VGroup(cell, label))
    return group


class Visualization(Scene):
    def mark(self, name, hold=1.0):
        self.wait(hold/2)
        self.stages[name] = float(self.time)
        self.layout[name] = [dict(bounds=[float(m.get_left()[0]), float(m.get_right()[0]),
            float(m.get_bottom()[1]), float(m.get_top()[1])]) for m in self.mobjects
            if m.width > 0 and m.height > 0]
        self.wait(hold/2)

    def change(self, number, title, caption):
        heading = prose(title, 26).move_to([-6.45, 2.63, 0], aligned_edge=LEFT)
        footer = prose(caption, 21, MUTED).move_to([0, -2.85, 0])
        if footer.width > 12.7:
            footer.scale_to_fit_width(12.7)
        self.play(FadeOut(self.heading), FadeOut(self.footer), run_time=.22)
        self.heading, self.footer = heading, footer
        self.play(FadeIn(heading, shift=UP*.06), FadeIn(footer),
                  self.progress.animate.stretch_to_fit_width(number*1.97).move_to(
                      [-5.91+number*.985, -3.8, 0]), run_time=.45)

    def clear_content(self):
        keep = [self.title, self.brand, self.rule, self.heading, self.footer,
                self.track, self.progress]
        leaving = [m for m in self.mobjects if m not in keep]
        if leaving:
            self.play(*(FadeOut(m) for m in leaving), run_time=.55)

    def construct(self):
        self.camera.background_color = BLACK
        d = load_trace()
        assert hashlib.sha256((ROOT/'training.json').read_bytes()).hexdigest() == TRAINING_SHA256
        metadata = json.loads((ROOT/'training.json').read_text())
        self.stages = {}
        self.layout = {}
        self.title = prose('MNIST / inside a convolutional network', 32)
        self.title.move_to([-6.45, 3.42, 0], aligned_edge=LEFT)
        self.brand = prose('TensorQuill', 17, MUTED).move_to([5.83, 3.43, 0])
        self.rule = Line([-6.45, 2.98, 0], [6.45, 2.98, 0], color=BORDER, stroke_width=1)
        self.track = Line([-5.91, -3.8, 0], [5.91, -3.8, 0], color=BORDER, stroke_width=2)
        self.progress = Rectangle(width=.02, height=.025, fill_color=CYAN,
                                  fill_opacity=1, stroke_width=0).move_to([-5.9,-3.8,0])
        self.heading = VGroup()
        self.footer = VGroup()
        self.add(self.title, self.brand, self.rule, self.track, self.progress)
        self.change(1, '01 / A real image, a fixed model', 'Frozen learned weights. One held-out image. A complete forward pass.')
        image = Tile(d['x'][0], 3.65, [-3.65,-.15,0], color=WHITE, grayscale=True)
        input_shape = math(r'1\times28\times28', 30, CYAN).move_to([-3.65,-2.4,0])
        question = prose('Which digit is this?', 35).move_to([2.5,1.17,0])
        intro = VGroup(math(r'x_{ij}=\mathrm{pixel}_{ij}/255',31).move_to([2.5,.25,0]),
                       math(r'y=7',34,AMBER).move_to([2.5,-.65,0]),
                       prose('Held-out MNIST image',20,MUTED).move_to([2.5,-1.48,0]))
        self.play(FadeIn(image, shift=UP*.1), FadeIn(input_shape), run_time=1.1)
        self.play(FadeIn(question), FadeIn(intro), run_time=.8)
        self.mark('input', 3.0)

        self.clear_content()
        self.change(2, '02 / One kernel, one receptive field', 'Patch and weights are displayed rounded; calculations retain full precision.')
        channel = 0
        row, col = np.unravel_index(np.argmax(d['a1'][channel,2:-2,2:-2]),(24,24))
        row, col = int(row+2), int(col+2)
        patch = d['x'][0,row-1:row+2,col-1:col+2]
        weights = d['conv1_weight'][channel,0]
        z = float(d['z1'][channel,row,col])
        bias = float(d['conv1_bias'][channel])
        self.detail = dict(channel=channel,row=row,col=col,patch=patch.tolist(),
                           kernel=weights.tolist(),bias=bias,z=z)
        image = Tile(d['x'][0], 2.8, [-4.8,.12,0], color=WHITE, grayscale=True)
        window = image.window(row-1,col-1,3)
        pixels = matrix(patch,[-1.47,.3,0])
        kernel = matrix(weights,[1.45,.3,0])
        names = VGroup(prose('Input patch',21).move_to([-1.47,1.7,0]),
                       prose('Learned kernel',21).move_to([1.45,1.7,0]),
                       math(r'K_0',24,AMBER).move_to([1.45,2.12,0]),
                       math(r'\odot',37,MUTED).move_to([0,.3,0]))
        output_box = RoundedRectangle(width=2.15,height=1.9,corner_radius=.12,
                            stroke_color=CYAN,stroke_width=1.3).move_to([4.85,.3,0])
        output = VGroup(prose('Weighted sum',20,MUTED).move_to([4.85,.85,0]),
                        math(f'z={z:.4f}',29,CYAN).move_to([4.85,.2,0]))
        arrow = Arrow([2.6,.3,0],[3.6,.3,0],buff=.05,color=AMBER,stroke_width=2)
        self.play(FadeIn(image),Create(window),run_time=.7)
        self.play(TransformFromCopy(window,pixels),FadeIn(kernel),FadeIn(names),run_time=1.1)
        self.mark('patch-and-kernel',2.2)
        products = matrix(patch*weights,[0,.3,0],tint=CYAN)
        product_name=prose('Elementwise products',20).move_to([0,1.7,0])
        self.play(Transform(pixels,products),Transform(names[0],product_name),
                  FadeOut(kernel),FadeOut(names[1]),FadeOut(names[2]),FadeOut(names[3]),run_time=1.1)
        equation=math(r'z_{0,'+str(row)+','+str(col)+r'}=\sum_{u,v}x_{'+str(row)+r'+u-1,'+str(col)+r'+v-1}K_{0,u,v}+b_0',27)
        equation.move_to([0,-1.8,0])
        evaluated=math(r'\sum(x\odot K_0)'+f'{bias:+.4f}={z:.4f}',29,CYAN).move_to([0,-2.4,0])
        self.play(FadeIn(equation),FadeIn(evaluated),Create(arrow),Create(output_box),FadeIn(output),run_time=.9)
        self.mark('convolution-arithmetic',3.5)
        relu=VGroup(math(r'\mathrm{ReLU}(z)',28,MUTED).move_to([4.85,-1.12,0]),
                    math(f'a={z:.4f}',30,CYAN).move_to([4.85,-1.75,0]))
        self.play(FadeIn(relu),run_time=.6)
        self.mark('relu-positive',1.7)
        negative=float(d['z1'][channel].min())
        negative_note=math(r'\mathrm{Elsewhere:}\quad z='+f'{negative:.4f}'+r'\quad\xrightarrow{\mathrm{ReLU}}\quad0',28,AMBER).move_to([0,-2.4,0])
        self.play(Transform(evaluated,negative_note),run_time=.7)
        self.mark('relu-negative',2.2)

        self.clear_content()
        self.change(2,'02 / Shared weights build a feature map', 'Stride one, zero padding one. The same learned kernel is reused at every location.')
        image=Tile(d['x'][0],3.65,[-4.15,-.05,0],color=WHITE,grayscale=True)
        feature=Tile(np.zeros((28,28)),3.65,[4.15,-.05,0],scale=float(d['a1'].max()))
        labels=VGroup(prose('Input',23).move_to([-4.15,2.05,0]),
                      prose('Activation / channel',23).move_to([3.8,2.05,0]),math('0',24,CYAN).move_to([5.55,2.05,0]),
                      math(r'1\times28\times28',25,MUTED).move_to([-4.15,-2.35,0]),
                      math(r'28\times28',25,CYAN).move_to([4.15,-2.35,0]))
        icon=matrix(weights,[0,.65,0],side=1.25,size=17)
        kernel_label=math(r'K_0',28,AMBER).move_to([0,1.65,0])
        operation=math(r'\sum(x\odot K_0)+b_0',23).move_to([0,-.55,0])
        operation2=math(r'\downarrow\ \mathrm{ReLU}',25,CYAN).move_to([0,-1.17,0])
        self.play(FadeIn(image),FadeIn(feature),FadeIn(labels),FadeIn(icon),FadeIn(kernel_label),FadeIn(operation),FadeIn(operation2),run_time=.8)
        positions=[(r,c) for r in range(28) for c in (range(28) if r%2==0 else range(27,-1,-1))]
        tracker=ValueTracker(0)
        def current():
            f=np.clip(tracker.get_value(),0,783);a=int(f);b=min(783,a+1);t=f-a
            return (1-t)*np.array(positions[a])+t*np.array(positions[b])
        scan=image.window(-1,-1,3)
        scan.add_updater(lambda m:m.become(image.window(*(current()-1),3)))
        cursor=Rectangle(width=3.65/28,height=3.65/28,color=AMBER,stroke_width=2).set_z_index(6)
        cursor.add_updater(lambda m:m.move_to(feature.point(*(current()+.5))))
        reveal=np.zeros((28,28))
        def update_feature(m):
            count=int(tracker.get_value())+1
            reveal[:]=0
            for r,c in positions[:count]:reveal[r,c]=d['a1'][0,r,c]
            new=ImageMobject(texture(reveal,float(d['a1'].max()))).set_resampling_algorithm(0)
            new.set_width(3.65).move_to(feature.image)
            m.become(new)
        feature.image.add_updater(update_feature)
        self.add(scan,cursor)
        self.stages['scan-start']=float(self.time)
        self.play(tracker.animate.set_value(783),run_time=8.5,rate_func=linear)
        for obj in (scan,cursor,feature.image):obj.clear_updaters()
        self.mark('scan-complete',1.4)
        self.play(FadeOut(scan),FadeOut(cursor),run_time=.35)

        self.clear_content()
        self.change(2,'02 / Four filters, four activation maps', 'Each channel is computed with its own learned kernel; all maps share one brightness scale.')
        maps=[]
        for c,x in enumerate((-4.8,-1.6,1.6,4.8)):
            tile=Tile(d['a1'][c],2.35,[x,.25,0],scale=float(d['a1'].max()))
            label=math(f'c={c}',25,CYAN).move_to([x,1.9,0])
            maps.append(tile)
            self.play(FadeIn(tile,shift=UP*.12),FadeIn(label),run_time=.45)
        dimension=math(r'4\times28\times28',32,CYAN).move_to([0,-1.6,0])
        legend=prose('Heatmaps: black = zero; brighter = stronger activation',19,MUTED).move_to([0,-2.35,0])
        self.play(FadeIn(dimension),FadeIn(legend),run_time=.5)
        self.mark('four-feature-maps',2.2)

        self.clear_content()
        self.change(3,'03 / Pool locally, preserve the strongest response', 'Each non-overlapping window becomes one value. Channels remain separate.')
        source=Tile(d['a1'][0],3.45,[-4.55,.1,0],scale=float(d['a1'].max()))
        pr,pc=row//2,col//2
        selected=source.window(pr*2,pc*2,2)
        pool_values=d['a1'][0,pr*2:pr*2+2,pc*2:pc*2+2]
        numbers=matrix(pool_values,[-.45,.35,0],side=1.9,size=28)
        dest=Tile(d['p1'][0],2.45,[4.55,.1,0],scale=float(d['a1'].max()))
        dest_window=dest.window(pr,pc,1)
        desc=VGroup(math(r'28\times28',27,MUTED).move_to([-4.55,-2.12,0]),
                    math(r'2\times2',25,AMBER).move_to([-.45,1.9,0]),
                    math(r'14\times14',27,CYAN).move_to([4.55,-1.64,0]))
        arrow=Arrow([.9,.35,0],[3.15,.35,0],buff=.12,color=AMBER,stroke_width=2)
        self.play(FadeIn(source),Create(selected),FadeIn(desc),run_time=.65)
        self.play(TransformFromCopy(selected,numbers),run_time=.85)
        self.mark('pool-window',1.5)
        winner=int(pool_values.argmax())
        highlight=SurroundingRectangle(numbers[winner],buff=.03,color=AMBER,stroke_width=2)
        result=math(r'\max='+f'{float(pool_values.max()):.4f}',30,CYAN).move_to([-.45,-1.35,0])
        self.play(Create(highlight),FadeIn(result),Create(arrow),run_time=.7)
        self.play(FadeIn(dest),TransformFromCopy(highlight,dest_window),run_time=.9)
        self.mark('pool-maximum',2.5)
        self.detail.update(pool_row=pr,pool_col=pc,pool_values=pool_values.tolist())

        self.clear_content()
        self.change(4,'04 / Combine channels, learn richer responses', 'Each output channel sums across all four input channels, then applies ReLU.')
        first=[];second=[]
        for c in range(4):
            x=-5.25+(c%2)*1.55;y=.83-(c//2)*1.8
            tile=Tile(d['p1'][c],1.28,[x,y,0],scale=float(d['a1'].max()))
            first.append(tile)
        for c in range(8):
            x=.5+(c%4)*1.78;y=.83-(c//4)*1.8
            tile=Tile(d['a2'][c],1.28,[x,y,0],scale=float(d['a2'].max()),color=VIOLET)
            second.append(tile)
        formula=math(r'z_{k,i,j}=b_k+\sum_{c=0}^{3}\sum_{u,v}K_{k,c,u,v}\,p_{c,i+u-1,j+v-1}',25).move_to([.4,1.97,0])
        arrow=Arrow([-2.8,0,0],[-.6,0,0],buff=.12,color=AMBER,stroke_width=2)
        name=math(r'3\times3',26,AMBER).move_to([-1.72,.6,0])
        shapes=VGroup(math(r'4\times14\times14',27,CYAN).move_to([-4.48,-2.3,0]),
                      math(r'8\times14\times14',27,VIOLET).move_to([3.17,-2.3,0]))
        self.play(*(FadeIn(t) for t in first),FadeIn(formula),FadeIn(shapes[0]),run_time=.8)
        self.play(Create(arrow),FadeIn(name),run_time=.65)
        self.play(LaggedStart(*(FadeIn(t,shift=RIGHT*.15) for t in second),lag_ratio=.13),FadeIn(shapes[1]),run_time=2)
        self.mark('second-convolution',3.0)
        pooled=[]
        for c,tile in enumerate(second):
            pooled.append(Tile(d['p2'][c],1.28,tile.get_center(),scale=float(d['a2'].max()),color=VIOLET))
        newshape=math(r'8\times7\times7',27,VIOLET).move_to(shapes[1])
        poolnote=math(r'\mathrm{MaxPool}\ (2\times2,\ s=2)',28,VIOLET).move_to([1,1.97,0])
        self.play(FadeOut(formula),FadeOut(name),FadeOut(arrow),
                  *(FadeOut(t) for t in first),FadeOut(shapes[0]),run_time=.35)
        self.change(4,'04 / Reduce spatial size, retain eight channels',
                    'Max pooling halves each spatial dimension independently in every channel.')
        pooling_explanation=VGroup(math(r'14\times14\ \longrightarrow\ 7\times7',28,VIOLET).move_to([-4.3,.5,0]),
            prose('One maximum per window',20,MUTED).move_to([-4.3,-.5,0]))
        self.play(FadeIn(pooling_explanation),run_time=.4)
        self.play(*(Transform(t,p) for t,p in zip(second,pooled)),Transform(shapes[1],newshape),FadeIn(poolnote),run_time=1.3)
        self.mark('second-pooling',2.0)

        self.clear_content()
        self.change(5,'05 / Flatten spatial responses into a feature vector', 'Flattening changes the shape, not the values. The classifier learns a weight for every feature.')
        tiles=[]
        for c in range(8):
            x=-5+(c%4)*1.32;y=.7-(c//4)*1.45
            tiles.append(Tile(d['p2'][c],1.05,[x,y,0],scale=float(d['a2'].max()),color=VIOLET))
        shape=math(r'8\times7\times7',30,VIOLET).move_to([-3.03,-2.12,0])
        feature_strip=ImageMobject(rgb(d['flat'].reshape(392,1),float(d['a2'].max()),VIOLET)).set_resampling_algorithm(0)
        feature_strip.set_height(3.6).stretch_to_fit_width(.45).move_to([.8,-.1,0])
        strip_border=SurroundingRectangle(feature_strip,buff=.03,color=VIOLET,stroke_width=1)
        arrow=Arrow([-1.1,0,0],[.3,0,0],buff=.1,color=AMBER,stroke_width=2)
        flatlabel=math(r'f\in\mathbb R^{392}',30,VIOLET).move_to([.8,-2.38,0])
        dense=VGroup(math(r'\ell=Wf+b',34).move_to([4.1,.8,0]),
                     math(r'W\in\mathbb R^{10\times392}',28,MUTED).move_to([4.1,-.1,0]),
                     math(r'\ell\in\mathbb R^{10}',30,CYAN).move_to([4.1,-1.03,0]))
        self.play(*(FadeIn(t) for t in tiles),FadeIn(shape),run_time=.7)
        self.play(Create(arrow),FadeIn(feature_strip),Create(strip_border),FadeIn(flatlabel),run_time=1.3)
        self.play(FadeIn(dense),run_time=.8)
        self.mark('flatten-and-classifier',3.0)

        self.clear_content()
        self.change(6,'06 / Ten logits become a prediction', 'Softmax probabilities describe this image. Test accuracy summarizes the full held-out test set.')
        thumbnail=Tile(d['x'][0],1.65,[-4.9,.8,0],color=WHITE,grayscale=True)
        prediction=VGroup(prose('Prediction',24,MUTED).move_to([-4.9,-.5,0]),
                          math('7',70,CYAN).move_to([-4.9,-1.35,0]),
                          math(r'y=7',26,AMBER).move_to([-4.9,-2.27,0]))
        table_header=VGroup(prose('Digit',18,MUTED).move_to([-2.6,1.9,0]),
                            prose('Logit',18,MUTED).move_to([-1.35,1.9,0]),
                            prose('Probability',18,MUTED).move_to([1.0,1.9,0]))
        rows=VGroup();bars=VGroup();labels=VGroup()
        probability_positions=[]
        for c in range(10):
            y=1.43-c*.385
            color=CYAN if c==7 else MUTED
            rows.add(math(str(c),23,color).move_to([-2.6,y,0]),
                     math(f'{float(d["logits"][c]):.2f}',22,color).move_to([-1.35,y,0]))
            track=Line([-.25,y,0],[2.0,y,0],stroke_color='#24303d',stroke_width=10)
            p=float(d['probabilities'][c])
            bar=Rectangle(width=max(.001,2.25*p),height=.095,fill_opacity=1,
                          fill_color=CYAN if c==7 else '#5a6b82',stroke_width=0)
            bar.move_to([-.25+max(.001,2.25*p)/2,y,0])
            bars.add(VGroup(track,bar))
            if c==7:
                text=f'{100*p:.4f}'+r'\%'
            else:
                exponent=int(np.floor(np.log10(p)));mantissa=p/10**exponent
                text=f'{mantissa:.2f}'+r'\times10^{'+str(exponent)+'}'
            labels.add(math(text,20,color).move_to([3.0,y,0]))
            probability_positions.append(dict(class_id=c,p=p,bar_length=2.25*p))
        softmax=math(r'p_k=\frac{e^{\ell_k}}{\sum_j e^{\ell_j}}',28).move_to([5.2,1.17,0])
        loss=float(-np.log(d['probabilities'][7]))
        loss_label=VGroup(prose('Sample cross-entropy',18,MUTED).move_to([5.2,-.15,0]),
                         math(r'-\log p_7',28).move_to([5.2,-.68,0]),
                         math(r'\approx'+f'{loss/1e-5:.4f}'+r'\times10^{-5}',25,CYAN).move_to([5.2,-1.22,0]))
        metrics=VGroup(prose('Test accuracy',18,MUTED).move_to([5.2,-1.95,0]),
                       math(f'{metadata["test"]["accuracy"]*100:.2f}'+r'\%',31,CYAN).move_to([5.2,-2.43,0]))
        self.play(FadeIn(thumbnail),FadeIn(table_header),FadeIn(rows),run_time=.8)
        self.mark('logits',2.0)
        self.play(FadeIn(softmax),LaggedStart(*(FadeIn(b) for b in bars),lag_ratio=.07),FadeIn(labels),run_time=1.6)
        self.play(FadeIn(prediction),run_time=.7)
        self.mark('probabilities',2.5)
        self.play(FadeIn(loss_label),FadeIn(metrics),run_time=.9)
        self.mark('prediction-and-metrics',5.0)
        run=Path(config.media_dir).parent
        (run/'stages.json').write_text(json.dumps(self.stages,indent=2)+'\n')
        (run/'layout.json').write_text(json.dumps(self.layout,indent=2)+'\n')
        (run/'detail.json').write_text(json.dumps(dict(**self.detail,probability_bars=probability_positions,
            display_scales=dict(a1=float(d['a1'].max()),a2=float(d['a2'].max())),
            sample_loss=loss,trace_sha256=TRACE_SHA256),indent=2)+'\n')
