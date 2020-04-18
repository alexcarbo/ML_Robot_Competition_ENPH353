# Alex Carbo ENPH 353 Logbook

## March 5th
  * Getting acquainted with moving the Anki Vector around. Going to implement PID control but the course is a perfect grid, so I think having a "turn_degrees" function to use at the corners may be a good idea.

## March 12th
  * I implemented PID control of the Anki Vector. 
  * It has a base "drive" mode where PID control occurs and keeps the robot on the road. The PID error is calculated based on the x-coordinate of the centre of mass of the black pixels in the lower 100 pixels of the image that are between the white lines. I needed to use an incredibly high cutoff for this as the picture is very bright. 
  * It also has a "turn" mode triggered by the distance sensor. If the Anki is 7.5cm away from the wall it will turn 90 degrees to the right (this is all that we need).
  * I also started a state machine type deal where we track where we are in the specified route we want the anki to follow.
Next step is identifying crosswalk and dealing with it.

## March 30th 
### [Everything has changed.](https://www.youtube.com/watch?v=w1oM3kQpXRo)
  * Change of plans - we will do the competition online.
  * I will now have to repeat what I have done on the Anki Vector in simulation
  * Today I got the base PID working with the publisher/subscriber model of ROS, still very untuned. Need to tune it before moving on and need to figure out what to do about corners.

## April 3rd
  * I have tuned the pid, the car is controlled nice and smoothly now.
  * I figured out how to do corners. It took some trial and error. Originally, I wanted to define "the road" as all the black pixels inside the tape - but this was pretty computationally expensive, so I only do it for the x axis (first_black_pixel, last_black_pixel) for each y in the bottom 120 pixels. 
  * A corner is triggered by a combination of the y coordinate of the centre of mass being very low, and a lot of white pixels being directly in front of the camera. I then use a turn_degrees function to turn the robot a specified number of degrees. Annoyingly it seems like this will be different of different computers, but I will need to test it more to find out.
  * I am now turning my attention to the issue of crosswalk detection, and then pedestrain detection/avoidance.
  * PLAN: make detect red bar, stop, then begin looking for pedestrain determining if it's safe to cross.

## April 10th
  * Since a lot of the files pertainting to the gazebo environment are device specific (the catkin workspace and such) I will upload my navigation node to the repo without pushing anything else.
  * Sent Thien my current PID control - is able to stay on the road and turn at corners, but no state control yet, no crosswalk detection, and no pedestrain avoidance. Hopefully the NN and navigation mesh well.
  * Decided final path for robot to take: Completes one loop around the first set of 3 cars, then crosses the crosswalk to access the rest of the plates, crosses the second crosswalk, and returns up the middle to get the last plate

## April 12th
  * Set aside the whole day for this, trying to get mostly done, will update at end of day!
  * Drew out a state diagram of the circuit, 8 states in total
  * Decided protocol for crossing crosswalk, 4 steps
  1. Detect a certain threshold of red in the image, increment state (start crosswalk state)
  2. If in a state where we need to cross the crosswalk, watch the pedestrain and decide if it is safe to cross
  3. Once we decide its safe begin crossing using the center of mass of black pixels on the screen, stop if pedestrain re enters image (keep checking if safe)
  4. Increment state to finished crosswalk state when you longer see a threshold of red in the image
  * First order of business was masking the bottom of the image for red, then summing the pixels and deciding on a threshold. I modified the image size and red threshold until I was satisfied with the stopping distance - close enough to make it safely across in the time the pedestrain is out of the road. Took me longer than I'd like to admit to figure out masks, as I was passing an HSV image to cv2.imshow, which was messing up the colours, making me think there was a problem converting to HSV, when really imshow just expects BGR...
  * Next, I need to figure out how to determine if it's safe to cross. After experimenting with a few methods I decided on detecting the amount of blue in an 60 pixel high image. That seemed to cut out everything except for the model's pants. I then ran a few tests to see how far to the edge of the image the pedestrain went. Once I had a good idea, I cut the edge of the mask at where the edge of the crosswalk typically was. The function returns True if it is safe to cross (less than a certain threshold of blue) and False otherwise.
  * Finally I needed to actually cross the crosswalk. Turns out I needed to modify a few things. First of all I need to ignore my code that defines the edges of the road, since the white lines of the crosswalk would make it inaccurate. I then needed to increase my binary threshold such that the grey of the crosswalk was mapped to black. After making these changes I could successfully cross the crosswalk.
  * This day was largely a success! I can do all the actions I need quite reliably now, so the next step is to build a state machine such that the robot completes our desired route through the course! That will be a job for another day though it's very late.

## April 14th
  * Time to finish this bad boy, goal is to get course navigation completed and reliable.
  * Going off of the state map I made a while ago, I started encoding the state machine using a property of my navigation class called state.
  * I quickly realized I needed a few more states, crossing a crosswalk involves detecting it, looking for pedestrain, crossing, and then looking for the next turn...
  * The first loop is fairly easy to code, just always turn right (now that I think about it our bot never turns left)
  * Had some issues with state changing too fast in the crosswalk crossing phase, but fixed by giving it a slightly larger FOV
  * Smooth sailing until I got to the end (after crossing the second crosswalk) where we need to turn into the middle with a distinct lack of signs to do so. 
  * Went back and commented my code, cleaned it up and made it look nice while I thought about a solution.
  * I noticed the position at which the robot changed state after leaving the crosswalk was quite consistent, so I thought "hmmm why not just set a timer for when it needs to turn?". So that's what I did, after timing it out properly. It worked better than I expected, and was quite tolerant to changes in the robot's position and velocity leaving the crosswalk, so I decided to keep it.
  * The robot can now succesfully complete the circuit, with quite high reliability!
  * Talked to Thien and his plate detection NN was working quite well so I pushed the finished navigation code to see how it worked with the NN. 
  * Ran the course on Thien's laptop and recorded a perfect run!

## April 17th
  * We have realized that the time limit is SIM TIME not real time, meaning our 4:30 sim time run is actually too slow.
  * I increased the base PID speed, and retuned the PID to work well with this speed
  Changed the timer for the last turn to reflect the new speed
  * Pushed new code and ran the course again on Thien's laptop 
  * Recorded the best run, now comfortably within the time limit!
  * This will be my last log entry, as we are done and moving on to the report. I thoroughly enjoyed this project, though I wish we got to use the Anki Vector robots, I do miss them.
