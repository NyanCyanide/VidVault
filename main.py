import cv2
import numpy as np
import sys
import os

image_dimensions = (HEIGHT, WIDTH) = (480, 640)

def textToImage(filepath):
    """Converts text into images."""
    pixel = [0, 0, 0] # (RED, GREEN, BLUE)
    curpixel = [0, 0]
    curpixelindex = 0
    MAX_HEIGHT, MAX_WIDTH = image_dimensions
    image = np.zeros((MAX_HEIGHT, MAX_WIDTH, 3), dtype=np.uint8)
    image_index = 0
    os.mkdir('./temp/')
    temp_path = './temp/' # Store temporary images here in the format of .bmp (bit map)
    with open(filepath, 'r') as f:
        for line in f: # For every line in the file
            for letter in line: # for every character in the file
                encoded_char = letter.encode('utf-8') # Converts the character into bytes
                char_size = len(encoded_char) # Counts the number of bytes required for each character
                for byte in encoded_char: # For every encoded byte in the character
                    image[curpixel[0], curpixel[1]][curpixelindex] = np.array(byte).astype(np.uint8) # update the current pixel th index value
                    curpixelindex += 1 # go to next pixelth index
                    if curpixelindex == 3: # if the pixelth index is 3, then the pixel is full
                        curpixelindex = 0 # So, reset the pixelth index
                        curpixel[1] += 1 # Go to the next pixel
                        if curpixel[1] == MAX_WIDTH: # If the pixel is out of bounds in width
                            curpixel[1] = 0 # Reset the pixel pointer to starting of the row
                            curpixel[0] += 1 # Go to the next row
                            if curpixel[0] == MAX_HEIGHT: # If the pixel is out of bounds in height
                                cv2.imwrite(f"{temp_path}/temp_{image_index}.bmp", image) # Save the image
                                image = np.zeros((MAX_HEIGHT, MAX_WIDTH, 3), dtype=np.uint8) # Flush the image
                                curpixel = [0, 0] # Reset the pixel pointer
                                curpixelindex = 0 # Reset the pixelth index
                                image_index += 1 # Go to the next image
    # Add a bufferbit to the image
    if curpixelindex == 0:
        image[curpixel[0], curpixel[1]] = np.array([255, 255, 255]).astype(np.uint8)
    elif curpixelindex == 1:
        image[curpixel[0], curpixel[1]][1] = np.array(255).astype(np.uint8)
        image[curpixel[0], curpixel[1]][2] = np.array(255).astype(np.uint8)
    elif curpixelindex == 2:
        image[curpixel[0], curpixel[1]][2] = np.array(255).astype(np.uint8)
    
    curpixel[1] += 1
    if curpixel[1] == MAX_WIDTH:
        curpixel[1] = 0
        curpixel[0] += 1
        if curpixel[0] == MAX_HEIGHT:
            cv2.imwrite(f"{temp_path}/temp_{image_index}.bmp", image) # Save the image
            image = np.zeros((MAX_HEIGHT, MAX_WIDTH, 3), dtype=np.uint8) # Flush the image
            curpixel = [0, 0] # Reset the pixel pointer
            curpixelindex = 0
            image_index += 1
            
    filename = filepath.split('/')[-1]
        
    cv2.imwrite(f"{temp_path}/temp_{image_index}.bmp", image) # Save the image
    
def imageToVideo(filepath, fps = 1):
    """Stitches the images to form a video."""
    MAX_HEIGHT, MAX_WIDTH = image_dimensions
    images = os.listdir('./temp/')
    images.sort()
    fourcc = cv2.VideoWriter_fourcc(*'FFV1')
    new = filepath.split('/')[-1]
    new = new.split('.')[0]
    new = new + '.mkv'
    video_writer = cv2.VideoWriter(new, fourcc, fps, (MAX_WIDTH, MAX_HEIGHT))
    for image in images:
        for _ in range(fps):
            video_writer.write(cv2.imread(f"./temp/{image}"))
            
    video_writer.release()
        
    # for image in images:
    #     os.remove(f"./temp/{image}")
        
    # os.rmdir('./temp/')

def videoToImage(filepath, fps = 1):
    """Converts the video into images."""
    vidcap = cv2.VideoCapture(filepath)
    success, image = vidcap.read()
    count = 0
    os.mkdir('./temp/')
    temp_path = './temp/'
    while success:
        cv2.imwrite(f"{temp_path}/temp_{count}.bmp", image)
        success, image = vidcap.read()
        count += 1
    vidcap.release()
    return count

def ImageToText(filepath):
    """Extracts the actual text from the images."""
    images = os.listdir('./temp/')
    images.sort()
    name = filepath.split("/")[-1]
    name = filepath.split(".")[-2]
    name += ".txt"
    count = None
    key = 0
    temparray = []
    with open(f"./{name}", 'a+') as filewriter:
        for image in images:
            currimage = cv2.imread(f"./temp/{image}")
            for row in currimage:
                for pixel in row:
                    for rgb in pixel:
                        # print("yes")
                        # print(rgb)
                        if key == 0:
                            key = 1
                            rgb = int(rgb)
                            temparray.append(rgb)
                            if (rgb >> 7) | 0b0 == 0b0: # if it is one byte
                                count = 0
                            elif rgb & 0b11000000 == 0b11000000: # if it is two bytes
                                count = 1
                            elif rgb & 0b11100000 == 0b11100000: # if it is three bytes
                                count = 2
                            elif rgb & 0b11110000 == 0b11110000: # if it is four bytes (making sure unwanted characters do not come over the point)
                                count = 3
                            else:
                                # print("reached")
                                count = None
                        else:
                            if count == None:
                                break
                            elif count == 0:
                                # print(temparray)
                                bytes_array = bytes(temparray)
                                utfdecoded = bytes_array.decode('utf-8')
                                # print(utfdecoded)
                                filewriter.write(utfdecoded)
                                temparray = []
                                key = 0
                            else:
                                temparray.append(rgb)
                                count -= 1
                    if count == None:
                        break
                if count == None:
                    break
                
    # for image in images:
    #     os.remove(f"./temp/{image}")
        
    # os.rmdir('./temp/')

def encoder(path):
    """Converts text into images, and stitches those images to form a video."""
    textToImage(path)
    imageToVideo(path)
    pass

def decoder(path):
    """Converts the video into images, and extracts the actual text from it."""
    print("""yaya""")
    videoToImage(path)
    ImageToText(path)
    pass

def processArguments(args):
    """Processes the arguments provided by the user."""
    if args[0] == '--encode' or args[0] == '-e':
        tipe = 1 
    elif args[0] == "--decode" or args[0] == '-d':
        tipe = 0
    else:
        tipe = None
    cpath = args[1]
    return (tipe, cpath)

def main():
    app = sys.argv[1:]
    val = processArguments(app)
    if val[0] == 1:
        encoder(val[1])
    else:
        decoder(val[1])

if __name__ == '__main__':
    main()