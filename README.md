<div id="top"></div>
<h1 align="center">Autonomous Roadside Mechanic</h1>
<br />
<div align="center">
  <a href="https://jacobsschool.ucsd.edu/">
    <img src="media\UCSDLogo_JSOE_BlueGold.png" alt="Logo" width="432" height="108">
  </a>

## 

<h3>Team 7 </h3>
<h3>ECE/MAE 148 Final Project FA25</h3>
<p>
</p>
<img src="media\car.jpg?" width="605" height="501">
</div>

## Table of Contents
  <ol>
    <li><a href="#team-members">Team Members</a></li>
    <li><a href="#overview">Overview</a></li>
    <li><a href="#what-we-promised">What We Promised</a></li>
    <li><a href="#accomplishments">Accomplishments</a></li>
    <li><a href="#demonstration">Demonstration</a></li>
    <li><a href="#challenges">Challenges</a></li>
    <li><a href="#robot-design">Robot Design</a></li>
    <li><a href="#electrical-diagram">Electrical Diagram</a></li>
    <li><a href="#references">References</a></li>
    <li><a href="#Acknowledgments">Acknowledgments</a></li>
  </ol>
  
## Team Members

<ul>
  <li>Shubhan Mital - MS Electrical and Computer Engineering (MLDS)</li>
  <li>Alison Stosser - Mechanical Engineering</li>
  <li>Long-Giang Vu - MS Computer Science and Engineering</li>
  <li>Qiwen Xu - Electrical Computer Engineering</li>
</ul>

## Overview
The goal of the "Autonomous Roadside Mechanic" is to identify and navigate a broken down car on the side of the road via hazard lights. The system uses two cameras, one “bird’s eye” camera mounted above the road which identifies there is a broken down vehicle via a blinking hazard light and one OAK-D camera mounted on the car to detect the car itself on the ground. Using ROS2, the “bird’s eye” camera sends a signal to activate the mechanic while the mechanic receives the signal to start driving on the track to navigate to and park behind the broken down car.

## What We Promised
### Must Have:
* Bird’s eye view camera that detects broken down stationary vehicle via hazard lights, sends signal to activate mechanic
* Receive “release” signal from bird’s eye view camera to start driving forward to search for broken down vehicle
* Detect back of broken down vehicle with OAK-D camera
* Stop behind the broken down car using LiDAR 

### Nice to Have:
* Avoid other cars/obstacles on the track
* Ability to push the broken down car for a distance (simulating moving the car out of harm's way) 
* Change lanes into the emergency lane

## Accomplishments
* We sucessfully integrated a Jetson Nano with ROS2 node and Intel RealSense Camera for "bird's eye view"
  * Detects blinking red lights and send publishes release signal
  * Pi is able to access and recieve the signal that a red blinking light has been detected
* Created accurate Roboflow model for detecting the cars in general, but focusing on the back of cars
  * Model runs on the camera with an approximate 90% accuracy
* We created a ROS2 node on Pi that uses the OAK-D camera running a Roboflow model to calculate the angle from the center of the camera to the center of the broken down vehicle
  * Measure both left and right offset 
* We created a second ROS2 node on Pi to control the robot using LiDAR to calculate the distance between the robot and the broken down car
  * Subscribes to blink detector node on Jetson Nano and camera node on Pi
  * Car starts driving forward when message is received that red blinking light is  detected on “bird’s eye” camera
  * Once the Roboflow model detects the broken down car, angle information from camera node is used to navigate the robot with a PD
  * Car stops when the LiDAR calculates a certain distance from  the broken down car

## Demonstration
<div align="center">
<img src="media/demo.gif" alt="Demo GIF" />
</div>

[Watch Full Demo Video](media/Demo_Video.mp4)

## Challenges
* Field of view for the Intel RealSense Camera was not as wide as necessary for a proper "bird's eye view"
  * The solution was to lower our placement of the camera closer to the blinking hazard light, but given more time we would replace it with a wide angle camera
* The PD control as the robot got closer to the broken down car was not as accurate due to the angle of correction needed being much greater at the shorter distances
  * We solved this by exponentially scaling the error angle between the car and the robot which increased the angle of correction needed when the robot was father away thereby reducing the angle of correction necessary when the robot was closer
* The blink detection algorithm was too sensitive and would trigger on any red light, not just hazard lights on stopped vehicles.
  * To address this, we converted the bird’s eye camera image to HSV color space to isolate red pixels, applied region-of-interest filtering to focus on potential hazard lights, analyzed temporal brightness changes across frames, and confirmed the blink frequency using a fast Fourier transform (FFT). Only when all three conditions were met did the system send the release signal to the mechanic vehicle, significantly reducing false positives while reliably detecting stopped vehicles with blinking hazard lights.
* Our Nice-To-Have goal is to integrate the existing lane detection system (from https://gitlab.com/ucsd_robocar2/ucsd_robocar_lane_detection2_pkg) with the mechanic system to enable lane following. Ideally, lane following is activated when the bird’s-eye camera detects a blinking light and remains active until a car is detected. Although the code integration is complete, we encountered an issue where the camera cannot simultaneously run both the Roboflow detection pipeline and the lane detection pipeline. The most likely cause is that the Roboflow detection node creates its own camera pipeline, while the lane detection node also attempts to subscribe directly to the camera, leading to conflicts between the two nodes.
    * Possible solution: Introduce a dedicated camera node that publishes raw RGB image data. Both the lane detection node and the car detection (Roboflow) node will then subscribe to this shared image topic, allowing them to process the same camera data independently without pipeline conflicts.
 
## Robot Design
<div align="center">
<img src="media\car_cad.png?" width="525" height="791">
</div>

### Hardware Components list
  * Traxxas Chassis with steering servo and sensored brushless DC motor
  * Jetson Nano
  * Inter RealSense D435i
  * Raspberry pi
  * OAK-D camera
  * Lidar LD06
  * 12V Battery
  * DC-DC Converter (12V to 5V)
  * VESC

## Electrical Diagram
<div align="center">
<img src="media\Electrical_Wiring.png?" width="581" height="500">
</div>
 
## References
* [Roboflow Car Detection Model](https://universe.roboflow.com/ece-148/car-object-detection-vw2le-5heye)

## Acknowledgments
Documentation inspired by/directly referenced from Team 5 - Fall 2024

Thank you to Professor Jack Silberman and our incredible TA's Winston and Aryan for an amazing Fall 2025 class!

<div align="center">
<img src="media\team_photo.jpg?" width="582" height="436">
</div>
