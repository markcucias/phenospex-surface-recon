# Development notes

My working log for this exercise: how I approached it, what I learned along the way, and why I made
the decisions I made. It is written as I go, so early entries can contain assumptions that later turn
out to be wrong — later entries correct them. The README is the cleaned-up summary of this file.

## 1. Getting oriented

### Refreshing the basics
Before touching the data, I needed to refresh what a point cloud and a mesh actually are. A point cloud
is a set of loose 3D samples without any connections between them; a mesh adds triangles built from
vertices and edges. I read about why triangles are used, what properties a good mesh should have, and
what information usually comes with a scan.

### Reading the PLY header
Next, I looked at the header of the supplied file to understand what data I actually have, and from
that, what the scanning device looks like. The scene was captured by two PlantEye scanner heads, and
for every point the file stores which head measured it (`scanner_id`), the scan line it belongs to
(`profile`) and its position along that line (`x_pos`), in addition to x, y, z and four reflectance
channels (red, green, blue, NIR).

This is beneficial for me: if my assumption about `x_pos` is correct, I don't need to calculate the
positions of the points, since I already have them. I just need to properly create triangles out of
them.

### Surveying the algorithms
I read about the algorithms that are usually used for surface reconstruction. I won't be implementing
them, but it is good to understand what each one does, so that I know which one fits this data.

I also read about best practices for filtering points: what outliers are, how to decide which points to
remove, the usual problems I can run into (thin leaves, outliers, etc.), and how to deal with them.

### Tools
I looked at which tools are helpful for this kind of work. Python and its libraries are better for
prototyping and exploration; C++ is what I will use for the actual implementation.

### Project setup
I revised how to set up and structure a project and where everything should live. With AI assistance I
set up a Makefile and a CI workflow so that testing is easier and the result is consistent across all
platforms and devices, which ensures the result's correctness.

## Open questions (to verify with the data)

- Is `x_pos` really the pixel column along the laser line?
- How are the two scanner heads arranged, and where do their views overlap?
- Does z point up (height) or down (distance from the scanner)?
- Why does scanner 0 have almost twice as many points as scanner 1?