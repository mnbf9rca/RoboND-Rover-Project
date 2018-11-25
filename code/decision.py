import random
import time
import numbers

import numpy as np
from collections import deque


def append_angle(Rover, new_angle):
    '''append the latest angle to the list, and drop the oldest from the list to max length'''
    Rover.last_nav_angles.append(new_angle)
    while len(Rover.last_nav_angles) > Rover.use_last_n_angles_for_steering:
        Rover.last_nav_angles.popleft()
    return Rover.last_nav_angles

# This is where you can build a decision tree for determining throttle, brake and steer
# commands based on the output of the perception_step() function


def decision_step(Rover):

    # Implement conditionals to decide what to do given perception data
    # Here you're all set up with some basic functionality but you'll need to
    # improve on this decision tree to do a good job of navigating autonomously!

    # Example:
    # Check if we have vision data to make decisions with
    if Rover.nav_angles is not None:
        # Check for Rover.mode status
        stuck_precision = 10

        if Rover.mode == 'unstick':

            turn_direction = 1
            if time.time() - Rover.time_last_checked_pos > 1:
                # we;ve been at this for at least 1 seconds (or just started)
                # check if we're still stuck

                x, y = Rover.pos
                # round
                x = int(x * stuck_precision)
                y = int(y * stuck_precision)
                if Rover.last_pos != (x, y):
                    # we seem to have moved
                    # try going forward again
                    Rover.mode = 'forward'
                else:
                    # randomise the turn direction every stuck_timeout seconds
                    turn_direction = [-1, 1][random.randrange(2)]
                    Rover.steer = turn_direction * 15
                Rover.time_last_checked_pos = time.time()
                Rover.last_pos = (x, y)
            # stuck - try turning
            Rover.brake = 0
            Rover.throttle = -10  # try backing up hard

        if Rover.mode == 'forward':
            # calculate go_froward_distance (for use later in if case)
            if Rover.rock_in_sight:
                if Rover.near_sample:
                    # if we're close enough to pick up - just stop
                    current_max_vel = 0
                else:
                    # otherwise, slow down as we get closer. Limit speed to Rover.max_vel.
                    current_max_vel = min(0.01 * np.mean(Rover.rock_dists), Rover.max_vel)
                # set stop_forward_distance to rock_stop_forward
                stop_forward_distance = Rover.rock_stop_forward
            else:
                # no rock near here, just go at max vel
                current_max_vel = Rover.max_vel
                # use regular stop_forward when no rock present
                stop_forward_distance = Rover.stop_forward
            # check pos every 3 seconds
            # if it's identical, and velocity is low, assume we're stuck
            if time.time() - Rover.time_last_checked_pos > Rover.stuck_timeout:
                x, y = Rover.pos
                # round
                x = int(x * stuck_precision)
                y = int(y * stuck_precision)
                if Rover.vel < current_max_vel:
                    if Rover.last_pos == (x, y):
                        # stuck!
                        # Set mode to "unstick" and hit the brakes!
                        Rover.throttle = 0
                        # Set brake to stored brake value
                        Rover.brake = Rover.brake_set
                        Rover.steer = 0
                        Rover.mode = 'unstick'

                Rover.time_last_checked_pos = time.time()
                Rover.last_pos = (x, y)
            # Check the extent of navigable terrain
            elif len(Rover.nav_angles) >= stop_forward_distance:
                # If mode is forward, navigable terrain looks good
                # and velocity is below max, then throttle, else brake
                if Rover.vel > current_max_vel:
                    # remove throttle and apply brake - but gently
                    Rover.throttle = 0
                    Rover.brake = Rover.brake_set * 0.1
                elif Rover.vel < current_max_vel:
                    # Set throttle value to throttle setting
                    Rover.throttle = Rover.throttle_set
                    Rover.brake = 0
                else:  # Else coast
                    Rover.throttle = 0
                    Rover.brake = 0
                
                # Set steering to average angle clipped to the range +/- 15
                # use an historic weighted average to try and steer more to one side than teh other (avoid circles)
                # check if there's a rock nearby. If so, aim for it.

                if Rover.rock_in_sight:
                    steer_degrees = np.mean(Rover.rock_angles * 180/np.pi)
                else:
                    # append absolute mean nav_angle - this way we smooth out angles
                    last_angles = np.mean(append_angle(Rover, np.mean(Rover.nav_angles * 180/np.pi)))
                    angle_compensation = last_angles * 0.1
                    steer_degrees = np.mean((Rover.nav_angles * 180/np.pi) + angle_compensation)

                Rover.steer = np.clip(steer_degrees, -15, 15)

            # If there's a lack of navigable terrain pixels then go to 'stop' mode

            elif len(Rover.nav_angles) < stop_forward_distance:
                # Set mode to "stop" and hit the brakes!
                Rover.throttle = 0
                # Set brake to stored brake value
                Rover.brake = Rover.brake_set
                Rover.steer = 0
                Rover.mode = 'stop'

        # If we're already in "stop" mode then make different decisions
        elif Rover.mode == 'stop':
            # If we're in stop mode but still moving keep braking
            if Rover.vel > 0.2:
                Rover.throttle = 0
                Rover.brake = Rover.brake_set
                Rover.steer = 0
            # If we're not moving (vel < 0.2) then do something else
            elif Rover.vel <= 0.2:
                # Now we're stopped and we have vision data to see if there's a path forward
                if len(Rover.nav_angles) < Rover.go_forward:
                    Rover.throttle = 0
                    # Release the brake to allow turning
                    Rover.brake = 0
                    # Turn range is +/- 15 degrees, when stopped the next line will induce 4-wheel turning
                    Rover.steer = -15  # Could be more clever here about which way to turn
                # If we're stopped but see sufficient navigable terrain in front then go!
                if len(Rover.nav_angles) >= Rover.go_forward:
                    # Set throttle back to stored value
                    Rover.throttle = Rover.throttle_set
                    # Release the brake
                    Rover.brake = 0
                    # Set steer to mean angle
                    Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
                    Rover.mode = 'forward'
    # Just to make the rover do something
    # even if no modifications have been made to the code
    else:
        Rover.throttle = Rover.throttle_set
        Rover.steer = 0
        Rover.brake = 0

    # If in a state where want to pickup a rock send pickup command
    if Rover.near_sample and Rover.vel == 0 and not Rover.picking_up:
        Rover.send_pickup = True

    return Rover
