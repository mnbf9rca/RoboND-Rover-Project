## Project: Search and Sample Return
### Writeup Template: You can use this file as a template for your writeup if you want to submit it as a markdown file, but feel free to use some other method and submit a pdf if you prefer.

---


**The goals / steps of this project are the following:**  

**Training / Calibration**  

* Download the simulator and take data in "Training Mode"
* Test out the functions in the Jupyter Notebook provided
* Add functions to detect obstacles and samples of interest (golden rocks)
* Fill in the `process_image()` function with the appropriate image processing steps (perspective transform, color threshold etc.) to get from raw images to a map.  The `output_image` you create in this step should demonstrate that your mapping pipeline works.
* Use `moviepy` to process the images in your saved dataset with the `process_image()` function.  Include the video you produce as part of your submission.

**Autonomous Navigation / Mapping**

* Fill in the `perception_step()` function within the `perception.py` script with the appropriate image processing functions to create a map and update `Rover()` data (similar to what you did with `process_image()` in the notebook). 
* Fill in the `decision_step()` function within the `decision.py` script with conditional statements that take into consideration the outputs of the `perception_step()` in deciding how to issue throttle, brake and steering commands. 
* Iterate on your perception and decision function until your rover does a reasonable (need to define metric) job of navigating and mapping.  

[//]: # (Image References)

[image1]: ./code/rock_threshed.png


## [Rubric](https://review.udacity.com/#!/rubrics/916/view) Points
### Here I will consider the rubric points individually and describe how I addressed each point in my implementation.  

---
### Writeup / README

#### 1. Provide a Writeup / README that includes all the rubric points and how you addressed each one.  You can submit your writeup as markdown or pdf.  

You're reading it!

### Notebook Analysis
#### 1. Run the functions provided in the notebook on test images (first with the test data provided, next on data you have recorded). Add/modify functions to allow for color selection of obstacles and rock samples.
See the [Jupyter notebook](./code/Rover_Project_Test_Notebook.ipynb) for the full code.

i completed `color_thresh()` as requested. 

`color_thresh()` returns two arrays, the first is teh mask where the threshold is exceeded, the second where it's not and where there is a non-zero pixel value. While testing, i noticed that i had to exclude areas with no value (as i can't realistically confirm whether they do or don't have obstacles). 

![5 images showing processing stages of a rock discovery via warping, and thresholding][image1]

#### 1. Populate the `process_image()` function with the appropriate analysis steps to map pixels identifying navigable terrain, obstacles and rock samples into a worldmap.  Run `process_image()` on your test data using the `moviepy` functions provided to create video output of your result. 
steps were included. Video is here: [Training run video](output/test_mapping.mp4)

### Autonomous Navigation and Mapping

#### 1. Fill in the `perception_step()` (at the bottom of the `perception.py` script) and `decision_step()` (in `decision.py`) functions in the autonomous mapping scripts and an explanation is provided in the writeup of how and why these functions were modified as they were.
`perception.py` was pretty much a cut and paste job from my previous code. I populated `color_thresh()`, and added `perception_step()` to process the image data. I added a condition to the step where Rover.worldmap is updated to include only those points captured in a frame with roll and pitch within a ±0.4 degrees of horizontal to improve fidelity. This included adding `absolute_degrees()` to calculate the absolute number of degress from 0 (as negative are reported as a number 180 < n < 360). I also swapped some of the colour coding as i found it hard to see rocks.

`decision.py` was a bit more challenging. I modified the `decision_step()` to include a check for positional change, as i found that the rover often got stuck. In this case, we rapidly reverse for 1 second and spin in a random direction. This seems to work :)

At first, I found that the rover swung from side to side, so i moderated nav_angle by using a rolling average of the last n (50 seems to work) results. Although this reduced the jerkiness of some movements, it didn't solve another problem i'd observed - the rover tended to go up and down the same paths, or get stuck going around in a circle on an open patch of land. So I now set the angle to 0 (straight) on approx 20% of readings. As I'm using an average, this has the effect of slightly decreasing the magnitude of the turn radius, or the propensity to turn i.e. the rover is more likely to head in a straighter line.

i had to add some properties to the `Rover` class for these changes to work.

#### 2. Launching in autonomous mode your rover can navigate and map autonomously.  Explain your results and how you might improve them in your writeup.  

**Note: running the simulator with different choices of resolution and graphics quality may produce different results, particularly on different machines!  Make a note of your simulator settings (resolution and graphics quality set on launch) and frames per second (FPS output to terminal by `drive_rover.py`) in your writeup when you submit the project so your reviewer can reproduce your results.**

when launching i selected 1024x768 resolution with "fantastic" graphics quality. This gave an FPS typically around 40, although on some runs it was as high as 60.

I made a [video of a training run, which is on youtube](https://youtu.be/_twsFdoUu3c). In this, you can see that the rover does a reasonable job of scanning the environment and locating the rocks - achieving around 60% coverage at over 80% fidelity in around 3 minutes.

I iteratively tested several different parameters
- `max_vel` - reduced slightly to reduce roll and yaw and increase precision
- `stop_forward` - increased slightly to reduce the chance of hitting a wall
- `go_forward` - 500 seemed to be a good number. Too low and it kept stopping, too high and sometimes it couldnt find a clear path.

what could cause it to fail?
- at the moment, the biggest cause is looping i.e. re-covering ground that's already scanned, and not discovering other paths.
- the rover also gets stuck on rocks - being able to identify obstacles independent of the edges of the road would help.
- rough terrain increases pitch and roll and reduces fidelity.
- in one test run, the rover got stuck behind a big rock. Even manually, i couldn't get it out :)

In future, I would consider
- biasing the `nav_angle` away from areas which have already been scanned, or even some sort of planning where it can identify isolated but unscanned areas.
- work out how to collect rocks i.e. set a course for a rock and approach it, stop, and pick.

Thanks!
