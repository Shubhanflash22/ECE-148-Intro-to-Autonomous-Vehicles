<div id="top"></div>
<h1 align="center">Autonomous Roadside Mechanic</h1>
<br />
<div align="center">
  <a href="https://jacobsschool.ucsd.edu/">
    <img src="media\UCSDLogo_JSOE_BlueGold.png" alt="Logo" width="432" height="108">
  </a>

## 

<h3>Team 7 </h3>
<h3>ECE 148 Final Project FA25</h3>
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
<img src="media\Demo_Video.mp4?" width="851" height="386">
</div>

## Challenges
* tbd 
 
## Robot Design
<div align="center">
<img src="media\car-cad.png?" width="851" height="386">
</div>

## Electrical Diagram
<div align="center">
<img src="media\Electrical_wiring.png?" width="581" height="365">
</div>
 
## References
* [Roboflow Car Detection Model](https://universe.roboflow.com/ece-148/car-object-detection-vw2le-5heye)
