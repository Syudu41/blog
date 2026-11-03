from manim import Scene, Text, UP, DOWN, WHITE
from manim_ml.neural_network import FeedForwardLayer, NeuralNetwork
from tensorquill.manimml import forward_pass

class Visualization(Scene):
    def construct(self):
        title = Text("A neural network forward pass", font_size=32).to_edge(UP, buff=0.8)
        layers = [FeedForwardLayer(size, node_radius=0.18, node_spacing=0.6,
                                  rectangle_fill_color=WHITE, rectangle_stroke_width=0,
                                  node_color="#1756a9", animation_dot_color="#bd6200")
                  for size in (2, 3, 1)]
        network = NeuralNetwork(layers, layer_spacing=1.2)
        assert [layer.num_nodes for layer in network.input_layers] == [2, 3, 1]
        network.scale_to_fit_width(7).shift(DOWN * 0.4)
        for connection in network.connective_layers:
            connection.edges.set_stroke(color="#666666", width=2)
            connection.animation_dot_color = "#bd6200"
        self.add(title, network)
        self.wait(0.5)
        self.play(forward_pass(network, run_time=3))
        self.wait(1)
