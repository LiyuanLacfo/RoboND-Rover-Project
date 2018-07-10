import numpy as np
import time


# This is where you can build a decision tree for determining throttle, brake and steer 
# commands based on the output of the perception_step() function
EPSILON = 0.000000000001
def decision_step(Rover):

    # Implement conditionals to decide what to do given perception data
    # Here you're all set up with some basic functionality but you'll need to
    # improve on this decision tree to do a good job of navigating autonomously!

    # Example:
    # Check if we have vision data to make decisions with

    #check if stuck
    print('Prev time ', Rover.prev_pos_time)
    print('Cur time ', time.time())
    if time.time() - Rover.prev_pos_time > 10:
        prev_x, prev_y = Rover.prev_pos
        cur_x, cur_y = Rover.pos
        if abs(prev_x-cur_x)+abs(prev_y-cur_y) < 0.5:
            Rover.mode = 'stuck'
        else:
            Rover.prev_pos_time = time.time()
            Rover.prev_pos = Rover.pos


    #check whether robot is running a cycle
    if(abs(Rover.steer+15) < EPSILON or (Rover.steer-15)<EPSILON) and Rover.mode == 'forward':
        if Rover.cycle_start_time < 0:
            Rover.cycle_start_time = time.time()
        elif time.time() - Rover.cycle_start_time > 10: #if keep turning at the maximum steering angle for more than 10 secs, we are sure it is in cycle mode
            Rover.mode = 'cycle'
            print('Enter cycle mode')
    else:
        Rover.cycle_start_time = -1.0

    if Rover.rock_dists is not None and len(Rover.rock_dists) > 0:
        print('pick up !!!!!!!!')
        Rover.mode = 'pick_up'


    if Rover.nav_angles is not None:

        # Check for Rover.mode status
        if Rover.mode == 'forward':
            # Check the extent of navigable terrain
            if len(Rover.nav_angles) >= Rover.stop_forward:  
                # If mode is forward, navigable terrain looks good 
                # and velocity is below max, then throttle 
                if Rover.vel < Rover.max_vel:
                    # Set throttle value to throttle setting
                    Rover.throttle = Rover.throttle_set
                else: # Else coast
                    Rover.throttle = 0
                Rover.brake = 0
                # Set steering to average angle clipped to the range +/- 15
                Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
            # If there's a lack of navigable terrain pixels then go to 'stop' mode
            elif len(Rover.nav_angles) < Rover.stop_forward:
                    print('here 111')
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
                    Rover.steer = -15 # Could be more clever here about which way to turn
                # If we're stopped but see sufficient navigable terrain in front then go!
                if len(Rover.nav_angles) >= Rover.go_forward:
                    # Set throttle back to stored value
                    Rover.throttle = Rover.throttle_set
                    # Release the brake
                    Rover.brake = 0
                    # Set steer to mean angle
                    Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
                    Rover.mode = 'forward'
        elif Rover.mode == 'cycle':
            Rover.throttle = 0
            Rover.brake = Rover.brake_set
            if Rover.steer < 0:
                Rover.steer = 15
            else:
                Rover.steer = -15
            Rover.mode = 'forward'
            Rover.cycle_start_time = -1
        elif Rover.mode == 'stuck':
            if not Rover.start_rolling_time: Rover.start_rolling_time = time.time()
            if time.time() - Rover.start_rolling_time > 2:
                Rover.mode = 'forward'
                Rover.start_rolling_time = None
                Rover.prev_pos_time = time.time()
            else:
                Rover.throttle = 0
                Rover.brake = 0
                Rover.steer = -15

        elif Rover.mode == 'pick_up' and len(Rover.rock_dists) > 0:
            if max(Rover.rock_dists) < 20:
                Rover.throttle = 0
                Rover.brake = Rover.brake_set
                Rover.steer = 0
            else:
                Rover.throttle = 0 if Rover.vel >= 0.5 else 0.2
                Rover.steer = np.clip(np.mean(Rover.rock_angles * 180/np.pi), -15, 15)
    # Just to make the rover do something 
    # even if no modifications have been made to the code
    else:
        Rover.throttle = Rover.throttle_set
        Rover.steer = 0
        Rover.brake = 0
        
    # If in a state where want to pickup a rock send pickup command
    if Rover.near_sample and Rover.vel == 0 and not Rover.picking_up:
        Rover.send_pickup = True
        if len(Rover.nav_angles) >= Rover.go_forward:
            # Set steer to mean angle
            Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
            Rover.mode = 'forward'
        else:
            Rover.throttle = 0
            # Release the brake to allow turning
            Rover.brake = 0
            # Turn range is +/- 15 degrees, when stopped the next line will induce 4-wheel turning
            Rover.mode = 'stop'
    print('mode: ', Rover.mode)
    return Rover

