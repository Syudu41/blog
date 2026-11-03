"""Show distribution, matching cross terms, and the square-of-a-sum identity."""

import json
from pathlib import Path

from manim import (
    Scene, Text, MathTex, VGroup, TransformMatchingTex, TransformFromCopy,
    ReplacementTransform, FadeIn, FadeOut, Create, SurroundingRectangle,
    CurvedArrow, UP, DOWN, RIGHT, UR, config,
)

BLUE = "#1756a9"
PURPLE = "#6d28d9"
ORANGE = "#b45309"


class Visualization(Scene):
    def hold(self, name, expression, duration):
        self.wait(duration / 2)
        self.stages[name] = {"time": float(self.time), "expression": expression}
        self.wait(duration / 2)

    def construct(self):
        self.stages = {}
        title = Text("A simple identity", font_size=32).move_to(UP * 2.9)
        caption = Text("Where does the middle term come from?", font_size=22).move_to(UP * 2.05)
        assumption = MathTex(r"a,b\in\mathbb{R}", font_size=24).to_corner(UR, buff=.4)
        square = MathTex(r"(a+b)^2", font_size=58).move_to(UP * .8)
        self.add(title, caption, assumption, square)
        self.hold("square", r"(a+b)^2", .9)

        factors = MathTex("(", "a", "+", "b", ")", "(", "a", "+", "b", ")", font_size=58).move_to(UP * .8)
        for index in (1, 6):
            factors[index].set_color(BLUE)
        for index in (3, 8):
            factors[index].set_color(ORANGE)
        self.play(TransformMatchingTex(square, factors), run_time=.8)
        self.hold("factors", r"(a+b)(a+b)", .7)
        instruction = Text("Multiply each term by each term", font_size=22).move_to(caption)
        self.play(ReplacementTransform(caption, instruction), run_time=.3)

        expressions = [r"a\cdot a", "+", r"a\cdot b", "+", r"b\cdot a", "+", r"b\cdot b"]
        products = VGroup(*(MathTex(expression, font_size=42) for expression in expressions))
        products.arrange(RIGHT, buff=.18).move_to(DOWN * .65)
        colors = [BLUE, PURPLE, PURPLE, ORANGE]
        pairs = [(1, 6), (1, 8), (3, 6), (3, 8)]
        for number, ((left, right), color) in enumerate(zip(pairs, colors)):
            target = products[number * 2].set_color(color)
            focus = VGroup(*(SurroundingRectangle(factors[index], color=color, buff=.05, stroke_width=2)
                             for index in (left, right)))
            arrows = VGroup(*(CurvedArrow(factors[index].get_bottom() + DOWN * .1,
                                         target.get_top() + UP * .12,
                                         angle=-.45, color=color, stroke_width=2, tip_length=.1)
                              for index in (left, right)))
            self.play(Create(focus), Create(arrows), run_time=.2)
            animations = [TransformFromCopy(VGroup(factors[left], factors[right]), target)]
            if number:
                animations.append(FadeIn(products[number * 2 - 1]))
            self.play(*animations, run_time=.65)
            self.hold(f"product-{number+1}", "+".join(expressions[:number*2+1:2]), .45)
            self.play(FadeOut(focus), FadeOut(arrows), run_time=.15)
        self.hold("distributed", r"a\cdot a+a\cdot b+b\cdot a+b\cdot b", .65)

        expanded = MathTex(r"a^2", "+", "ab", "+", "ba", "+", r"b^2", font_size=46).move_to(products)
        for index, color in zip((0, 2, 4, 6), colors):
            expanded[index].set_color(color)
        self.play(TransformMatchingTex(products, expanded), run_time=.8)
        self.hold("expanded", r"a^2+ab+ba+b^2", .8)

        cross_caption = Text("The two cross terms are equal", font_size=22).move_to(instruction)
        self.play(ReplacementTransform(instruction, cross_caption), run_time=.3)
        focus = SurroundingRectangle(VGroup(*expanded[2:5]), color=PURPLE, buff=.15)
        self.play(Create(focus), run_time=.25)
        commuted = MathTex(r"a^2", "+", "ab", "+", "ab", "+", r"b^2", font_size=46).move_to(expanded)
        for index, color in zip((0, 2, 4, 6), colors):
            commuted[index].set_color(color)
        self.play(TransformMatchingTex(expanded, commuted), run_time=.8)
        self.hold("matching-cross-terms", r"a^2+ab+ab+b^2", 1)
        self.play(FadeOut(focus), run_time=.2)

        combined = MathTex(r"a^2", "+", "2ab", "+", r"b^2", font_size=46).move_to(commuted)
        for index, color in zip((0, 2, 4), (BLUE, PURPLE, ORANGE)):
            combined[index].set_color(color)
        collect_caption = Text("Combine the matching terms", font_size=22).move_to(cross_caption)
        self.play(ReplacementTransform(cross_caption, collect_caption), TransformMatchingTex(commuted, combined), run_time=.8)
        self.hold("collected", r"a^2+2ab+b^2", .8)

        final = MathTex(r"(a+b)^2", "=", r"a^2", "+", "2ab", "+", r"b^2", font_size=50)
        final.move_to(DOWN * .05)
        for index, color in zip((2, 4, 6), (BLUE, PURPLE, ORANGE)):
            final[index].set_color(color)
        takeaway = Text("Four products. Two matching cross terms.", font_size=22).move_to(collect_caption)
        self.play(FadeOut(factors), TransformMatchingTex(combined, final),
                  ReplacementTransform(collect_caption, takeaway), run_time=.9)
        self.hold("final", r"(a+b)^2=a^2+2ab+b^2", 2.2)
        (Path(config.media_dir).parent / "stages.json").write_text(json.dumps(self.stages, indent=2) + "\n")
