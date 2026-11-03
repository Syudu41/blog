"""Narrow compatibility helpers for the tested ManimML feed-forward layers."""


def forward_pass(network, run_time=3):
    """Compose layer animations without ManimML's empty connection groups."""
    from manim import Succession
    from manim_ml.neural_network.layers.feed_forward import FeedForwardLayer
    from manim_ml.neural_network.layers.feed_forward_to_feed_forward import FeedForwardToFeedForward

    layers = list(network.all_layers)
    if not layers or any(not isinstance(layer, (FeedForwardLayer, FeedForwardToFeedForward)) for layer in layers):
        raise ValueError("This adapter supports nonempty, fully connected feed-forward networks only")
    if any(isinstance(layer, FeedForwardLayer) and layer.num_nodes <= 0 for layer in layers):
        raise ValueError("Feed-forward layers must contain at least one node")
    animations = [layer.make_forward_pass_animation() for layer in layers]
    return Succession(*animations, run_time=run_time)
