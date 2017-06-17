import numpy as np


# This is where you can build a decision tree for determining throttle, brake and steer 
# commands based on the output of the perception_step() function
def decision_step(Rover):

    # Implement conditionals to decide what to do given perception data
    # Here you're all set up with some basic functionality but you'll need to
    # improve on this decision tree to do a good job of navigating autonomously!

    # Example:
    # Check if we have vision data to make decisions with

    # rock detected
    Rover.rock_angles = Rover.rock_angles * 180/np.pi
    if Rover.nav_angles is not None:
        if Rover.mode == 'stuck':
            print('------------------------','Stuck mode', '--------------------------')
            Rover.throttle = 0
            # Release the brake to allow turning
            Rover.brake = 0
            # Turn range is +/- 15 degrees, when stopped the next line will induce 4-wheel turning
            Rover.steer = -15 #if len(Rover.nav_angles) < Rover.go_forward else np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
            Rover.mode = 'stop'
        elif Rover.mode == 'stop':
            print('-------------------------','Stop mode','-----------------------------')
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
                elif len(Rover.nav_angles) >= Rover.go_forward:
                    # Set throttle back to stored value
                    Rover.throttle = Rover.throttle_set
                    # Release the brake
                    Rover.brake = 0
                    # Set steer to mean angle
                    Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
                    Rover.mode = 'forward'
        elif is_stuck(Rover):
            launch_recovery(Rover, 'stuck')
        elif len(Rover.rock_angles) >= 1:
            print('-------------------------', 'Rock Detected','------------------------')
            rock_pix = np.mean(Rover.rock_dists)
            rock_angle_mean = np.mean(Rover.rock_angles)
            Rover.steer = np.clip(rock_angle_mean, -15, 15)
            # brake & align towards rock
            if abs(rock_angle_mean) > 15:
                # still moving - brake hard
                if Rover.vel > 0.2:
                    Rover.brake = Rover.brake_set
                    Rover.throttle = 0
                # not moving
                else:
                    Rover.brake = 0
                    Rover.throttle = 0
                    check_stuck(Rover)
            else:
                Rover.throttle = min(1.0, rock_pix/200)
                if Rover.vel > 1:
                    Rover.brake = Rover.brake_set/2
                else:
                    Rover.brake = 0
                    check_stuck(Rover)
            print('\n'*5)
        elif Rover.mode == 'forward':
            print('--------------------------','Forward Mode','---------------------------')
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
                check_stuck(Rover)
            # If there's a lack of navigable terrain pixels then go to 'stop' mode
            elif len(Rover.nav_angles) < Rover.stop_forward:
               launch_recovery(Rover, 'stop')
    # Just to make the rover do something 
    # even if no modifications have been made to the code
    else:
        Rover.throttle = Rover.throttle_set
        Rover.steer = 0
        Rover.brake = 0
        
    if Rover.near_sample and Rover.vel >= 0.2:
        Rover.brake = 1.0
    # If in a state where want to pickup a rock send pickup command
    if Rover.near_sample and Rover.vel <= 0.2 and not Rover.picking_up:
        Rover.send_pickup = True
    
    return Rover

def launch_recovery(Rover, mode):
    print('launching recovery:', mode)
    Rover.throttle = 0
    Rover.brake = Rover.brake_set
    Rover.steer = 0
    Rover.mode = mode

def check_stuck(Rover):
    if Rover.vel < 0.01:
        Rover.throttle=1.0

def is_stuck(Rover):
    if Rover.vel < 0.01 and Rover.throttle == 1.0:
        return True
