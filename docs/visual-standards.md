# TensorQuill visual and explanatory standards

These are TensorQuill's working criteria, informed by the references below. They are an interpretation of those examples, not an official 3Blue1Brown specification or a claim of affiliation.

## Reference approach

[ManimML](https://github.com/helblazer811/ManimML) supplies composable ML visualization primitives and layer animations. Use those primitives to preserve architectural structure and the order of operations. A successful primitive animation is a building block for an explanation.

The [3Blue1Brown neural-network lesson](https://www.3blue1brown.com/lessons/neural-networks/) motivates a concrete recognition problem, defines neurons and activations, and connects the visible network to its mathematical description. The [backpropagation lesson](https://www.3blue1brown.com/lessons/backpropagation/) develops intuition about an example before introducing the notation. The [calculus introduction](https://www.3blue1brown.com/lessons/essence-of-calculus/) develops a general idea through a concrete geometric problem. Our proposed flow draws on these approaches.

## Audit of the first rendered samples

The first samples were created to test the rendering and publication pipeline. Their existing reviews cover their original task requirements. This audit also asks whether they work as explanatory scenes.

The table records that initial audit. The identity sample has since been replaced by a reviewed GIF that forms each product, identifies the matching cross terms, and collects them into the final expression.

| Criterion | ManimML forward-pass sample | Identity figure |
| --- | --- | --- |
| Correct structure or expression | Pass: a 2–3–1 schematic, with no numerical prediction claim | Pass: exact algebraic check and LaTeX rendering |
| Stable objects and focused highlighting | Pass: fixed layout, activation moves left to right | Static figure; animation is not its primary deliverable |
| Meaning of visual elements | Partial: node and edge roles are described in the page text, but not labeled in the clip | The expression is visible, but has no geometric interpretation |
| Mechanism explained | Partial: sequence is visible; weighted sums and activation functions are absent | No derivation or visual demonstration of the identity |
| Connection from intuition to formalism | Absent | The formula is presented directly |
| Pacing for a standalone explanation | Insufficient: 4.5 seconds illustrates a sequence, without time to teach the mechanism | Not assessed as a standalone explanation |

Assessment: the network follows ManimML's basic animation flow. Neither sample yet demonstrates the full explanatory progression we want from 3Blue1Brown-inspired work. Rendering, typography, and mathematical checks passing do not establish that explanatory progression.

## Flow for explanatory animations

Write a short storyboard before coding. For a standalone explanation, the usual progression is:

1. Pose one concrete question or establish the problem.
2. Introduce a small example and define what its objects represent.
3. Reveal one causal operation at a time, directing attention to the relevant objects.
4. Make the mechanism visible: show how an input changes a quantity or result.
5. Connect the established intuition to LaTeX notation, using the same objects and consistent encodings.
6. Extend the example to the whole operation or a general statement.
7. Hold a clear final state and state the takeaway.

Adapt this progression to the audience and requested scope. An embedded loop can rely on its surrounding explanation, and a publication figure can express the sequence through labeled panels. A still image does not need an animation's introduction or timing. Each deliverable still needs a clear purpose and sufficient context.

## Review questions

- Can the intended reader identify the question and the final takeaway?
- Are nodes, edges, colors, labels, and arrows defined before they carry an argument?
- Does motion reveal a relationship or computation that would otherwise be hard to follow?
- Do quantities and object identities remain consistent through transitions?
- Are schematic highlights clearly distinguished from computed numerical activations or gradients?
- Does the notation describe something the viewer has already seen, with tensor dimensions and assumptions where relevant?
- Is there enough time to read each label and inspect the important states? Set timing from the storyboard rather than applying one global duration blindly.
- For figures, do the caption, labels, and panels make the same reasoning readable at the intended final size?

Keep all mathematics in LaTeX and prose in the selected Arial-family font. Contrast and readable layouts must work on the chosen background; a black background is not a requirement for this explanatory approach.

## Next explanatory examples

For a forward-pass explanation, introduce the input, hidden, and output roles; focus on one neuron; show its weighted sum and activation; then extend the same mechanism to a layer and its matrix expression. Choose explicit values only when that task's numerical example has been specified and independently checked.

The identity GIF now demonstrates the algebraic expansion term by term. A complementary geometric version could show a square partitioned into four regions, label their areas with LaTeX, and connect them to the same expanded expression.

Include the applicable storyboard and explanatory criteria in each new task's requirements. The reviewing agent must assess them from the actual rendered output; media validation cannot infer educational clarity.
