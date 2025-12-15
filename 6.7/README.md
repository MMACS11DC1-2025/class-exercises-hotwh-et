# Chart Image Analyzer
## Objective
Determine the percent change in an image of a graph\
The user should be able to provide an image of any line graph, and the program will isolate and analyze only the line of the chart

## Identifying the visual feature
For the line of a line chart, these facts are very commonly true, in order of most common to least common:
- It contrasts from the background
- It is a contiguous and connected group of pixels
- It spans across the entire chart area
- It spans vertical space (goes up and down)

The program takes advantage of each of these traits to identify the line.

### It contrasts from the background
Logically speaking, the line must contrast in colour from the background to make it easy for humans to read. This also provides
a clear criteria for the program to detect. To detect the contrast from the background, it is necessary to determine the background
colour. This is done by looping over every pixel in the image to get the average colour, which is most likely at least close to the
background colour. While doing this, it also gets the colour range to check how varied the overall colours in the image are. These are
used in combination to check if a colour contrasts enough to be considered a foreground element.

### It is a contiguous and connected group of pixels
A line must be connected across the entirety of its length. It is necessary to determine which pixels are connected groups. This is 
done using [Connected Component Labelling (CCL)](https://en.wikipedia.org/wiki/Connected-component_labeling). At a high level, this
algorithm checks each "foreground" (where foreground is desired and background is not) pixel in the image. It then checks all neighbouring
pixels to see if they are also foreground pixels. This process is repeated until there are no new neighbour pixels that are foreground
pixels. The "labelling" aspect of this is done by assigning a label to each connected group. After all neighbour pixels are checked, the
label number is incremented, so different groups are given a different label.

This program utilized the [pseudocode given on the Wikipedia page](https://en.wikipedia.org/wiki/Connected-component_labeling#One_component_at_a_time).
A custom class (`ImageLabelMatrix`) is used to store the labels in a matrix (list of lists) representing each pixel, which is used in
later processing. All pixels with the same label hereafter will be referred to as a group.

### It spans across the entire chart area
The line of a line chart usually runs across the entire chart area so it can take advantage of the space. Although this is not always
true, it is safe to use this as a secondary measure as it is still usually true. If the line spans across the chart, it most likely consists
of many pixels, so only the 3 largest groups are used for future processing to increase efficiency. The widest group is determined by getting
the left-most x value and the right-most x value of an identified group. This is repeated for each group, so the maximum can be found. However, 
this can cause misidentifications. This is because there are also other elemnts that span a great width. Some examples include chart axes or other elements
(as demonstrated in [stocks.png](./images/stocks.png)). As an attempt to make the program more robust, it stores multiple wide groups, instead of just 1. 
The amount of groups it stores varies depending on the widths. The program checks from the widest to most narrow groups, and checks if the decrease is under
2x (meaning the group is above half of the previous group). If it is, it continues, otherwise, it stops. Out of these, the final criteria is used to narrow 
it down to just 1 if it is not already.

### It spans vertical space (goes up and down)
Typically, the line changes in vertical position. Although this is not always true, it is commonly true enough to be used if the other criteria cannot
narrow it down to only 1. The check for this is very similar to the previous check. It finds the bottom-most y value and the top-most y value of each
group to fine the one with the biggest difference. Out of all remaining groups, the tallest one is considered to be the final target group.

## Using the identified visual feature
As per the previously stated objective, the program must determine the change across the graph. To do this, it is necessary to get the heights (y values) of
the start and end. This is done by finding the left-most and right-most pixels in the identified group. In most graphs, there are multiple pixels with at the
same horizontal position. Because of this, the program averages the heights of every pixel with this x value. The difference between the start and end heights
is the change in the graph.

Additionally, the program creates a version of the image that shows the isolated chart, and the identified starting and ending pixels. This uses the ImageDraw
class to efficiently create the image, which is stored in a dictionary.

With all the scores determined, the top 5 are printed to the user.

## Score searching
After the score for every image is calculated, the user is prompted to input a score. The program uses binary search to find the image that has this score.
The user can then choose to see the original image, isolated chart, or to cancel. Upon selecting an image, the program will open it in their default photo
viewer.