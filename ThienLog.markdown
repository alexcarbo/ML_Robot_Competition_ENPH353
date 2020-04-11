# Thien's Log for ENPH 353 Machine Learning and Computer Vision Project Course
This document goes through the work I've done to complete this project. I've formatted it on a day to day basis when I work on the project. Each day may consist of just thoughts, research, goals, and progress updates along the way.

## March 3,2020
---
Looking at YOLO for object detection, thinking about using remote control to collect data to train a plate detection model.
Created a script to take images from Anki and turn them into videos for later analysis

## March 5
---
Planning on using SIFT to detect the "Cars" and cut away that part of the image
Update after working with SIFT, now trying to use HSV colors to detect the block. Finding more success and will need to get the
HSV colors for each block. Afterward I will develop an algorithm to isolate the plates. Requires more thinking

## March 12
---
New license labels might make it easier to detect the location from the images. I will try to get SIFT to detect the 'car' block
since I haven't had success using SIFT to isolate the plates themselves. I want to use SIFT to isolate the cars and then splice the
image to then look for the plates. Currently I have been using HSV to isolate blocks in the images.

### Progress Updates
* I've gotten a bounding box on the 'car' blocks after converting the HSV images to binary and analyzing the amount of pixels in the 
frame vertical and horizontally. This only works if there's one car in the image.

* My next task is to allow for the detection of multiple 'cars'. I'm thinking of imlpementing an algorithm to
detect rises and falls in the binary image.

* Spent some time on the updated course collecting more data. Going to update our PID drive to include recording video.

## March 30
---
Change of plans to work on simulation now instead. Going to first work on manually controlling the simulation robot in Gazebo and have that record video to be analyzed so I
can adapt the previous work into something usable for sim

### Goals for Today:
* Implement video capture from manual driving
* Look at the video and transfer the algorithm from real world onto sim
* Isolate license plates

### Progress Updates

* After working on this for 6 hours I have successfully implemented a video capture script off the simulated robot and saving them to a video folder to develop an algorithm to cut away the license plates.

* Adjusting some hsv values I have managed to get a bounding box around the cars and cut away those images to them be analyzed for the license plates.

* We can now focus on cropping out the license plates to be fed into a neural net for later which I will work on later this week.

* Some issues i'm seeing right now are the time it takes to analyze one frame so I will likely limit the analysis of frames to every 10 or 30 and only once the bounding box around the car is large enough for a clear view of the plates. It would also be ideal to only look at a specific section of the frame lowering the number of pixels I would need to look at.

## April 2
---
Today I plan on speeding up the analysis of images, focussing on the right half of the image, this should also remove issues with seeing two cars in one image as we want to
focus on the larger and clearer image rather than the one farther back.

### Goals and Tasks:
* Determine a good size to crop the image down to before using OpenCV
* Implement vision for all three colours of cars
* Isolate the license plates into their own image to be stored
* Differentiate parking number with plate number
* Begin work on neural network by collecting data from these plates from the robot driving
* Integrate PID with Alex's part of the codebase

### Notes:
* Simulated world coordinates in Gazebo
* Start location with blue cars: x -2.2 y -2.4 z 0.05 R 0.0 P 0.0 Y 1.57
* Corner with green cars: x 2.2 -y 2.4 z 0.05 R 0.0 P 0.0 Y 1.57

### Progress Updates

* Currently cleaning up my analysis code to have better readability and optimizing the speed.

* Updated the filters to detect the blue, green, and yellow cars as well as the black border of the license plates.

* Some issue using bitwise_and for the black filter, for now I'm using the mask for black instead.

* Re-working my detection algorithm to ignore the contribution of the black alphanumerics to get the bounds
on the license plates by setting a high threshold for the sum of values in each row and column of pixels
this also acts to require the image be sufficently large enough before the program crops out the license plate

* Successfully implemented a plate detection algorithm based off a video, it is able to put bounding boxes around the parking and license plates. I used the black mask to count the contribution of black pixels in each
column and row while filtering out the alphanumerics. Thersholding the transition from low to high in the arrays I set the min and max values on x and the y's for the two plates. 

* Taking a break but will continue now try to add this detection algorithm on top of a running instance of Gazebo

* Running the capture_video node in Gazebo while controling the robot with **teleop_twist_keyboard** successfully record video
while under my control.

* Transfered over the script to detect plates into a DetectPlate.py class file along with a constants.py file with constants
used in DetectPlate.py. Running the node in Gazebo shows that it can detect plates while driving. There may be issues with plates
that are skewed from a rectangular image as they currently are.

### Todo for next time
* Integrate the PID from Alex's part and test the plate detection
* Save pictures license plates driving around. Might need to use a perspective transform for skewed plates
* Collect images to train a convolutional neural network

## April 3
---
Today I plan on completing the Todo from last day (April 3) and start work on collecting license plate data by driving around the course manual after reseting the world and its plates. I may want to just hardcode some values for driving to automate this.

### Progress Updates
* I've worked on cropping out the license plates from the detection algorithm and have now also created a pickle file to keep a running tally of the number of plates saved to continually store the collected plates into a file.
* Changed the algorthim to use cornerHarris on the contours of the black outline for the license plates. Using this I've extracted the coordinates of the corners to do a perspective transform. These plates are saved in a plates folder with a pickle file updating the tally of plates. 

## April 10
---
I had some major issues updating the repo. I think I forgot to commit and push my last update on April 3 so I'm missing a few progress updates. The main idea change is that now I've switched over to using contours and finding the coordinates of the corners using the above mentioned way.
After fixing the issues in updating the Gazebo repo, Alex and I are moving to local copies which we should've done at the start and only share the neural network, node, and launch files on the repo for now.

## Goal and Tasks
* Put together the PID and plate detection and see how if behaves
* Start collecting some data for the neural network
* Start working on the neural network

## Progress Updates
* Putting together the pid and plate detection seems to work well. I only made it scan the plates if the contours are a certain size. These files save to a new plate folder well. Some bugs persist with the perspective transform ocassionally.
* Spent some time cleaning up magic numbers and formatting for DetectPlate.py
* Made a plate labeller jupyter script for the plate pictures to be fed into a nerual net. I rename the images from a parking##.jpg to their parking number P##.jpg and license plates from license##.jpg to AB##.jpg.
* Started transfering the CNN from lab 5 over to the competition use case. Adjusted the jupyter script to be a bit cleaner and simpler. Fed it the data collected from the sim world and it has started to recognize some letter. Needs more data which I will do tomorrow.