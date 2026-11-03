"""A small Manim-drawn sculptor builds a neural network's hidden layer."""

import json
from pathlib import Path

import numpy as np
from manim import (
    Scene, Text, Circle, Dot, Line, Polygon, Rectangle, VGroup,
    Create, FadeIn, FadeOut, ReplacementTransform, Rotate,
    UP, DOWN, RIGHT, WHITE, config, rate_functions,
)

BLUE = "#1756a9"
INK = "#374151"
STONE = "#e6e1d7"
ORANGE = "#b45309"


class Visualization(Scene):
    def hold(self, name, duration):
        self.wait(duration / 2)
        self.stages[name] = float(self.time)
        self.wait(duration / 2)

    def construct(self):
        self.stages = {}
        title = Text("WORK IN PROGRESS", font_size=36, weight="BOLD").move_to(UP * 2.9)
        subtitle = Text("Shaping the hidden layer", font_size=23).move_to(DOWN * 2.65)
        credit = Text("Made with Manim", font_size=17, color="#666666").move_to(DOWN * 3.35)
        labels = VGroup(
            Text("Input", font_size=20).move_to([-5.1, 1.85, 0]),
            Text("Hidden layer", font_size=20, color=BLUE).move_to([1.65, 2.05, 0]),
            Text("Output", font_size=20).move_to([5.25, 1.85, 0]),
        )
        inputs = VGroup(*(Circle(.32, color=BLUE, fill_color=WHITE, fill_opacity=1, stroke_width=3)
                          .move_to([-5.1, y, 0]) for y in (.7, -.7)))
        output = Circle(.32, color=BLUE, fill_color=WHITE, fill_opacity=1, stroke_width=3).move_to([5.25, 0, 0])
        centers = [np.array([1.65, y, 0]) for y in (1.05, 0, -1.05)]
        edges = VGroup()
        for center in centers:
            for node in inputs:
                edges.add(Line(node.get_center(), center, buff=.32, color="#c8cdd2", stroke_width=1.5))
            edges.add(Line(center, output.get_center(), buff=.32, color="#c8cdd2", stroke_width=1.5))
        edges.set_z_index(-3)
        rocks = VGroup()
        for center in centers:
            vertices = [center + np.array([x, y, 0]) for x, y in
                        [(-.52, -.18), (-.42, .35), (-.03, .52), (.45, .32), (.52, -.17), (.12, -.48), (-.3, -.43)]]
            rocks.add(Polygon(*vertices, color="#9a9182", stroke_width=2, fill_color=STONE, fill_opacity=1))
        carved = [Circle(.34, color=BLUE, stroke_width=3, fill_color="#edf6ff", fill_opacity=1).move_to(center)
                  for center in centers]
        rough_template = rocks.copy()

        head = Circle(.23, color=INK, stroke_width=2, fill_color="#efd2b3", fill_opacity=1).move_to([-.65, .65, 0])
        eye = Dot([-.51, .69, 0], radius=.025, color=INK)
        cap = Polygon([-.92, .83, 0], [-.78, 1.01, 0], [-.46, .99, 0], [-.36, .8, 0],
                      color=INK, fill_color=ORANGE, fill_opacity=1, stroke_width=2)
        torso = Polygon([-.9, .24, 0], [-.44, .22, 0], [-.23, -.78, 0], [-.98, -.78, 0],
                        color=INK, fill_color=BLUE, fill_opacity=1, stroke_width=2)
        pocket = Rectangle(width=.26, height=.24, color="#c6e2f5", stroke_width=1).move_to([-.61, -.36, 0])
        legs = VGroup(Line([-.74, -.76, 0], [-.98, -1.65, 0], color=INK, stroke_width=7),
                      Line([-.44, -.76, 0], [-.18, -1.65, 0], color=INK, stroke_width=7),
                      Line([-1.1, -1.65, 0], [-.79, -1.65, 0], color=INK, stroke_width=7),
                      Line([-.27, -1.65, 0], [.06, -1.65, 0], color=INK, stroke_width=7))
        arms = VGroup(Line([-.44, .12, 0], [.04, -.12, 0], color=INK, stroke_width=5),
                      Line([.04, -.12, 0], [.62, .15, 0], color=INK, stroke_width=5),
                      Line([-.52, .21, 0], [-.14, .45, 0], color=INK, stroke_width=5),
                      Line([-.14, .45, 0], [.15, .55, 0], color=INK, stroke_width=5))
        hands = VGroup(Dot([.62, .15, 0], radius=.07, color="#efd2b3"),
                       Dot([.15, .55, 0], radius=.07, color="#efd2b3"))
        sculptor = VGroup(legs, torso, pocket, arms, head, eye, cap, hands).set_z_index(3)
        ground = Line([-1.7, -1.8, 0], [3, -1.8, 0], color="#d6d6d6", stroke_width=1.5)
        pivot = np.array([.15, .55, 0])
        handle = Line(pivot, [.7, .9, 0], color="#80512d", stroke_width=5)
        hammer_head = Rectangle(width=.45, height=.19, color=INK, fill_color=INK, fill_opacity=1)
        hammer_head.rotate(-.56).move_to([.7, .9, 0])
        hammer = VGroup(handle, hammer_head).set_z_index(4)
        chisel = Line([.62, .15, 0], [1.14, 1.05, 0], color="#687787", stroke_width=5).set_z_index(2)
        self.add(edges, inputs, output, rocks, ground, title, labels, subtitle, credit, sculptor, chisel, hammer)
        self.hold("rough-hidden-layer", .8)

        for index, center in enumerate(centers):
            aimed = Line([.62, .15, 0], [1.14, center[1], 0], color="#687787", stroke_width=5).set_z_index(2)
            if index:
                self.play(ReplacementTransform(chisel, aimed), run_time=.25)
                chisel = aimed
            self.play(Rotate(hammer, angle=-1.22, about_point=pivot), run_time=.22, rate_func=rate_functions.ease_in_quad)
            chips = VGroup(*(Polygon([0, .06, 0], [-.05, -.04, 0], [.05, -.04, 0],
                                     color=ORANGE, fill_color=STONE, fill_opacity=1, stroke_width=1)
                             .move_to([1.12, center[1], 0]) for _ in range(4)))
            self.add(chips)
            flights = []
            for chip, offset in zip(chips, [(-.45, .25), (-.38, -.25), (-.2, -.5), (.1, -.3)]):
                flights.append(chip.animate.shift(np.array([offset[0], offset[1], 0])).set_opacity(0))
            self.play(*flights, ReplacementTransform(rocks[index], carved[index]),
                      Rotate(hammer, angle=1.22, about_point=pivot), run_time=.5)
            self.remove(chips)
            self.hold(f"carved-node-{index+1}", .65)

        self.play(edges.animate.set_stroke(color="#829eb3", width=2), run_time=.35)
        self.hold("shaped-hidden-layer", 1.2)
        # Return to the initial pose for an unobtrusive repeat.
        fresh_rocks = rough_template.copy()
        self.play(*(FadeOut(node) for node in carved), FadeIn(fresh_rocks),
                  edges.animate.set_stroke(color="#c8cdd2", width=1.5), run_time=.45)
        reset_chisel = Line([.62, .15, 0], [1.14, 1.05, 0], color="#687787", stroke_width=5).set_z_index(2)
        self.play(ReplacementTransform(chisel, reset_chisel), run_time=.2)
        self.hold("loop-reset", .5)
        (Path(config.media_dir).parent / 'stages.json').write_text(json.dumps(self.stages, indent=2) + '\n')
