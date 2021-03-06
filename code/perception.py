import numpy as np
import cv2

# Identify pixels above the threshold
# Threshold of RGB > 160 does a nice job of identifying ground pixels only
def color_thresh(img, rgb_thresh=(160, 160, 160)):
    # Create an array of zeros same xy size as img, but single channel
    color_select = np.zeros_like(img[:,:,0])
    # Require that each pixel be above all three threshold values in RGB
    # above_thresh will now contain a boolean array with "True"
    # where threshold was met
    above_thresh = (img[:,:,0] > rgb_thresh[0]) \
                & (img[:,:,1] > rgb_thresh[1]) \
                & (img[:,:,2] > rgb_thresh[2])
    # Index the array of zeros with the boolean array and set to 1
    color_select[above_thresh] = 1
    # Return the binary image
    return color_select

# Define a function to convert from image coords to rover coords
def rover_coords(binary_img):
    # Identify nonzero pixels
    ypos, xpos = binary_img.nonzero()
    # Calculate pixel positions with reference to the rover position being at the 
    # center bottom of the image.  
    x_pixel = -(ypos - binary_img.shape[0]).astype(np.float)
    y_pixel = -(xpos - binary_img.shape[1]/2 ).astype(np.float)
    return x_pixel, y_pixel


# Define a function to convert to radial coords in rover space
def to_polar_coords(x_pixel, y_pixel):
    # Convert (x_pixel, y_pixel) to (distance, angle) 
    # in polar coordinates in rover space
    # Calculate distance to each pixel
    dist = np.sqrt(x_pixel**2 + y_pixel**2)
    # Calculate angle away from vertical for each pixel
    angles = np.arctan2(y_pixel, x_pixel)
    return dist, angles

# Define a function to map rover space pixels to world space
def rotate_pix(xpix, ypix, yaw):
    # Convert yaw to radians
    yaw_rad = yaw * np.pi / 180
    xpix_rotated = (xpix * np.cos(yaw_rad)) - (ypix * np.sin(yaw_rad))
                            
    ypix_rotated = (xpix * np.sin(yaw_rad)) + (ypix * np.cos(yaw_rad))
    # Return the result  
    return xpix_rotated, ypix_rotated

def translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale): 
    # Apply a scaling and a translation
    xpix_translated = (xpix_rot / scale) + xpos
    ypix_translated = (ypix_rot / scale) + ypos
    # Return the result  
    return xpix_translated, ypix_translated


# Define a function to apply rotation and translation (and clipping)
# Once you define the two functions above this function should work
def pix_to_world(xpix, ypix, xpos, ypos, yaw, world_size, scale):
    # Apply rotation
    xpix_rot, ypix_rot = rotate_pix(xpix, ypix, yaw)
    # Apply translation
    xpix_tran, ypix_tran = translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale)
    # Perform rotation, translation and clipping all at once
    x_pix_world = np.clip(np.int_(xpix_tran), 0, world_size - 1)
    y_pix_world = np.clip(np.int_(ypix_tran), 0, world_size - 1)
    # Return the result
    return x_pix_world, y_pix_world

# Define a function to perform a perspective transform
def perspect_transform(img, src, dst):
           
    M = cv2.getPerspectiveTransform(src, dst)
    mask_org = np.ones_like(img[:, :, 0]) if len(img.shape) > 2 else np.ones_like(img)
    warped = cv2.warpPerspective(img, M, (img.shape[1], img.shape[0]))# keep same size as input image
    mask = cv2.warpPerspective(mask_org, M, (img.shape[1], img.shape[0]))
    return warped, mask

#function to find rock, where rock is 255
def find_rock(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    lower, upper = np.array([19, 190, 100]), np.array([30, 255, 255])
    mask = cv2.inRange(hsv, lower, upper)
    return mask


# Apply the above functions in succession and update the Rover state accordingly
def perception_step(Rover):
    # Perform perception steps to update Rover()
    # TODO: 
    # NOTE: camera image is coming to you in Rover.img
    # 1) Define source and destination points for perspective transform
    # 2) Apply perspective transform
    # 3) Apply color threshold to identify navigable terrain/obstacles/rock samples
    # 4) Update Rover.vision_image (this will be displayed on left side of screen)
        # Example: Rover.vision_image[:,:,0] = obstacle color-thresholded binary image
        #          Rover.vision_image[:,:,1] = rock_sample color-thresholded binary image
        #          Rover.vision_image[:,:,2] = navigable terrain color-thresholded binary image

    # 5) Convert map image pixel values to rover-centric coords
    # 6) Convert rover-centric pixel values to world coordinates
    # 7) Update Rover worldmap (to be displayed on right side of screen)
        # Example: Rover.worldmap[obstacle_y_world, obstacle_x_world, 0] += 1
        #          Rover.worldmap[rock_y_world, rock_x_world, 1] += 1
        #          Rover.worldmap[navigable_y_world, navigable_x_world, 2] += 1

    # 8) Convert rover-centric pixel positions to polar coordinates
    # Update Rover pixel distances and angles
        # Rover.nav_dists = rover_centric_pixel_distances
        # Rover.nav_angles = rover_centric_angles

    # The destination box will be 2*dst_size on each side

    dst_size = 5 
    scale = dst_size*2
    bottom_offset = 6
    img = Rover.img
    #the source and destination points for perspective transform
    source = np.float32([[14, 140], [301 ,140],[200, 96], [118, 96]])
    destination = np.float32([[img.shape[1]/2 - dst_size, img.shape[0] - bottom_offset],
                  [img.shape[1]/2 + dst_size, img.shape[0] - bottom_offset],
                  [img.shape[1]/2 + dst_size, img.shape[0] - 2*dst_size - bottom_offset], 
                  [img.shape[1]/2 - dst_size, img.shape[0] - 2*dst_size - bottom_offset],
                  ])
    warped, mask = perspect_transform(img, source, destination)
    #tell where I am
    cur_loc = np.zeros_like(mask)
    cur_loc[img.shape[0]-1][img.shape[1]//2] = 1
    navigable = color_thresh(warped)*mask
    obstacle = (1-navigable)*mask
    #update Rover.vision_image
    Rover.vision_image[:, :, 0] = navigable*255
    Rover.vision_image[:, :, 1] = obstacle*255
    #update worldmap
    x_pix_cur_loc, y_pix_cur_loc = rover_coords(cur_loc)
    x_pix_nav, y_pix_nav = rover_coords(navigable)
    x_pix_obstacle, y_pix_obstacle = rover_coords(obstacle)
    scale = 2*dst_size
    x_pix_world_nav, y_pix_world_nav = pix_to_world(x_pix_nav, y_pix_nav, Rover.pos[0], 
                                                    Rover.pos[1], Rover.yaw, 200, scale)
    
    x_pix_world_obstacle, y_pix_world_obstacle = pix_to_world(x_pix_obstacle, y_pix_obstacle, Rover.pos[0], 
                                                    Rover.pos[1], Rover.yaw, 200, scale)
    x_pix_world_cur_loc, y_pix_world_cur_loc = pix_to_world(x_pix_cur_loc, y_pix_cur_loc, Rover.pos[0],
                                                    Rover.pos[1], Rover.yaw, 200, scale)

    #update world map only when rover in normal view
    if (Rover.pitch < 0.5 or Rover.pitch > 359.5) and (Rover.roll < 0.5 or Rover.roll > 359.5):
        Rover.worldmap[y_pix_world_obstacle, x_pix_world_obstacle, 0] += 1
        Rover.worldmap[y_pix_world_nav, x_pix_world_nav, 2] += 10
    # Rover.worldmap[y_pix_world_cur_loc, x_pix_world_cur_loc, :] = 255
    #find rock
    rock_mask = find_rock(img)
    
    if np.any(rock_mask):
        warped_rock, _ = perspect_transform(rock_mask, source, destination)
        x_pix_rock, y_pix_rock = rover_coords(warped_rock)
        Rover.rock_dists, Rover.rock_angles = to_polar_coords(x_pix_rock, y_pix_rock)
        x_pix_world_rock, y_pix_world_rock = pix_to_world(x_pix_rock, y_pix_rock, Rover.pos[0], 
                                                    Rover.pos[1], Rover.yaw, 200, scale)
        if (Rover.pitch < 0.5 or Rover.pitch > 359.5) and (Rover.roll < 0.5 or Rover.roll > 359.5):
            Rover.worldmap[y_pix_world_rock, x_pix_world_rock, :] = 255
        Rover.vision_image[:, :, 2] = rock_mask #update Rover.vision_image
    else:
        Rover.vision_image[:, :, 2] = 0

    #update distance and angle
    dists, angles = to_polar_coords(x_pix_nav, y_pix_nav)
    Rover.nav_angles = angles
    Rover.nav_dists = dists
    return Rover