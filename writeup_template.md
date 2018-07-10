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

[image1]: ./misc/rover_image.jpg
[image2]: ./calibration_images/example_grid1.jpg
[image3]: ./calibration_images/example_rock1.jpg 

## [Rubric](https://review.udacity.com/#!/rubrics/916/view) Points
### Here I will consider the rubric points individually and describe how I addressed each point in my implementation.  

---
### Writeup / README

#### 1. Provide a Writeup / README that includes all the rubric points and how you addressed each one.  You can submit your writeup as markdown or pdf.  

You're reading it!

### Notebook Analysis
#### 1. Run the functions provided in the notebook on test images (first with the test data provided, next on data you have recorded). Add/modify functions to allow for color selection of obstacles and rock samples.
Here is an example of how to include an image in your writeup.

#### 1. Populate the `process_image()` function with the appropriate analysis steps to map pixels identifying navigable terrain, obstacles and rock samples into a worldmap.  Run `process_image()` on your test data using the `moviepy` functions provided to create video output of your result. 
And another! 

![alt text][image2]
### Autonomous Navigation and Mapping

#### 1. Fill in the `perception_step()` (at the bottom of the `perception.py` script) and `decision_step()` (in `decision.py`) functions in the autonomous mapping scripts and an explanation is provided in the writeup of how and why these functions were modified as they were.

First for the `perception_step()` function, it mainly deals with how to process the image and extract information from the image to navigate the rover. Since the view of the world map is of eagle's view, we need to first transform the perspective of the images taken from the camera in front of the rover. 
![image for perspective transform](https://github.com/LiyuanLacfo/RoboND-Rover-Project/blob/master/result_images/example_grid1.jpg)

![image after perspective transform](https://github.com/LiyuanLacfo/RoboND-Rover-Project/blob/master/result_images/perspective_transform.jpg)
Second, since the navigable pixels have high values in all channels, the color threshold method can be used to separate navigable area from obstacle area. After trying some threshold values, `(160, 160, 160)` is selected. 
![image after color threshold](https://github.com/LiyuanLacfo/RoboND-Rover-Project/blob/master/result_images/thresh.jpg)
Third, to mark the rover in the world map, the coordinates of the image need to be adjusted and placed in the coordinates of the world map. As for how to find `rocks`, the rgb color of rock is identified as (147, 127, 21), and the corresponding hsv is (24, 214, 142). By referring to [this](https://docs.opencv.org/3.2.0/df/d9d/tutorial_py_colorspaces.html), the lower bound of hsv value and upper bound of hsv value are set to `(14, 100, 100)` and `(34, 255, 255)`. 

Then for the `decision_step()`. Actually, this function can be used without modification. But after some tests of autonomous mode, the rover sometimes would move in a cycle. Thus a decision to break the cycle is added. While cycling, the steering angle of the rover is always `15` or `-15`. If the steering angle keep those values for more than 10 seconds, the rover enter into `cycle` mode. The rover would first break and steer to another side then go into `forward` mode.  


#### 2. Launching in autonomous mode your rover can navigate and map autonomously.  Explain your results and how you might improve them in your writeup.  

**Note: running the simulator with different choices of resolution and graphics quality may produce different results, particularly on different machines!  Make a note of your simulator settings (resolution and graphics quality set on launch) and frames per second (FPS output to terminal by `drive_rover.py`) in your writeup when you submit the project so your reviewer can reproduce your results.**

Here I'll talk about the approach I took, what techniques I used, what worked and why, where the pipeline might fail and how I might improve it if I were going to pursue this project further. 

The simulator setting is 640*480 with good quality. The fps is 38.
![performance](https://github.com/LiyuanLacfo/RoboND-Rover-Project/blob/master/result_images/performance.jpg)

First, the fidelity decreases a lot while in the shadow area. It seems that the color threshold method to find navigable area does not perform well when there is shadow. 

Second, sometimes the rover would get stuck, some more decisions need to be implemented.




