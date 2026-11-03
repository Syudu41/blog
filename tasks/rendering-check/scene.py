from manim import Scene, Text, MathTex, VGroup, FadeIn, DOWN

class Visualization(Scene):
    def construct(self):
        title = Text("A simple identity", font_size=34)
        equation = MathTex(r"(a+b)^2 = a^2 + 2ab + b^2", font_size=44)
        group = VGroup(title, equation).arrange(DOWN, buff=0.7)
        self.play(FadeIn(group), run_time=1)
        self.wait(1)
