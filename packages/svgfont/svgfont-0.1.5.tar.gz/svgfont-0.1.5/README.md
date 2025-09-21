
# Table of Contents

1.  [Load SVG-fonts as NumPy polylines](#org1fca4d9)
    1.  [Install with PIP (TODO)](#orgc598b95)
    2.  [Install locally](#org8a0349c)
    3.  [Examples](#org6cb7195)



<a id="org1fca4d9"></a>

# Load SVG-fonts as NumPy polylines

Svgfont is a lightweight Python library that loads [SVG fonts](https://www.w3.org/TR/SVG11/fonts.html) as sequences of polylines. The polylines are represented as 2d numpy arrays (Nx2), each having N points.

The main use for this is to load [Hershey fonts](https://en.wikipedia.org/wiki/Hershey_fonts) for drawing with a plotter, robot or CNC machine. The library comes with some standard Hershey fonts bundled, and a curated list of fonts can be found [here](https://gitlab.com/oskay/svg-fonts).

The functionality of the Svgfont library is similar to the [Hershey extension](https://www.evilmadscientist.com/2011/hershey-text-an-inkscape-extension-for-engraving-fonts/) for the [InkScape](https://inkscape.org) vector drawing program, but this library allows you to easily load these kind fonts in any Python script.


<a id="orgc598b95"></a>

## Install with PIP (TODO)

    pip install svgfont


<a id="org8a0349c"></a>

## Install locally

Clone the repository, navigate to the directory and from there

    pip install -e .


<a id="org6cb7195"></a>

## Examples

A simple use case is:

    import svgfont
    import matplotlib.pyplot as plt
    
    font = svgfont.load_font('TwinSans')
    paths = svgfont.text_paths('Hello\nWorld', font, 20,
                               align='center',
                               pos=[50,20],
                               tol=0.1) # pos is optional
    plt.figure(figsize=(6,3))
    for P in paths:
        plt.plot(P[:,0], P[:,1], 'k')
    plt.axis('equal')
    plt.gca().invert_yaxis()
    plt.show()

![img](https://raw.githubusercontent.com/colormotor/svgfont/main/figures/hershey-base.png)

The `tol` parameter is optional and it determines the maximum error for sampling the Bezier curves that compose each character.

You can also fit the text to a rectangle (with optional padding) as follows:

    import svgfont
    import matplotlib.pyplot as plt
    from matplotlib import patches
    
    w, h = 200, 100
    font = svgfont.load_font('HersheyScript1')
    paths = svgfont.text_paths('Hello World', font, box=svgfont.rect(0, 0, w, h), padding=10)
    plt.figure(figsize=(6,3))
    for P in paths:
        plt.plot(P[:,0], P[:,1], 'k')
    plt.gca().add_patch(patches.Rectangle((0, 0), w, h, fill=False, edgecolor='r'))
    plt.axis('equal')
    plt.gca().invert_yaxis()
    plt.show()

![img](https://raw.githubusercontent.com/colormotor/svgfont/main/figures/hershey-box.png)

These examples use the Hershey fonts [bundled with the library](https://github.com/colormotor/svgfont/tree/main/svgfont/hershey), but a path to a
SVG font file can be provided also.

