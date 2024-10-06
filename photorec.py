'''
distance = item['facts'].get('Distance', '')
caption = item.get('caption', '')
image_link = item.get('image_url', '')
obj_type = item['facts'].get('Object Description', '')
color_info = item['facts'].get('Color Info', '')
'''

import json
import random
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

CORS(app)  # This will enable CORS for all routes

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('survey.html')  # Input HTML file for user preferences

@app.route('/get_image', methods=['POST','GET'])
def get_image():
    # Get user inputs from the request
    user_inputs = request.json
    # Call the existing photorec function
    selected_image = photorec(user_inputs)  # Modify photorec to accept parameters

    return jsonify(selected_image)

def photorec(user_inputs):
    # Unpack the user inputs
    color_input = {
        "red": user_inputs.get('red', False),
        "orange": user_inputs.get('orange', False),
        "yellow": user_inputs.get('yellow', False),
        "green": user_inputs.get('green', False),
        "blue": user_inputs.get('blue', False),
        "violet": user_inputs.get('violet', False),
    }
    
    # Optional preferences (expand logic if necessary)
    preference1 = user_inputs.get('preference1', None)
    preference2 = user_inputs.get('preference2', None)
    preference3 = user_inputs.get('preference3', None)
    selected_images = user_inputs.get('selectedImages', [])
    user_name = user_inputs.get('userName', 'Guest')  # Get user name
    
    # Load image data from JSON file
    input_file_path = 'ver2_image_data.json'
    with open(input_file_path, 'r') as file:
        data = json.load(file)

    # Function to determine the color category based on RGB value
    def get_color_name(rgb):
        colors = {
            "red": (255, 0, 0),
            "orange": (255, 170, 0), 
            "yellow": (255, 255, 0),
            "green": (0, 255, 0),
            "blue": (0, 0, 255),
            "violet": (127, 0, 255)
        }
        min_distance = float("inf")
        closest_color = None
        for color, value in colors.items():
            distance = sum((i - j) ** 2 for i, j in zip(rgb, value))
            if distance < min_distance:
                min_distance = distance
                closest_color = color
        return closest_color
        
    # Function to count true colors in each image
    def count_true_colors(image_data):
        color_percentages = image_data.get('color_percentages', [])
        
        sum_colors = 0
        cnt = 0
        for color_data in color_percentages:
            color_rgb_str = color_data['colorCode'].strip('()')
            rgb = tuple(map(int, color_rgb_str.split(', ')))
            color_name = get_color_name(rgb)
            cnt += 1
            
            if color_name and color_input.get(color_name, False):
                sum_colors += 1
        
        return sum_colors, cnt

    # Create a separate list to store images with color information
    processed_images = []

    for item in data:
        colors = count_true_colors(item)
        
        processed_images.append({
            'title': item['title'],
            'color_score': colors[0],
            'distance': item['distance'],
            'type': item['type'],
            'link': item['image_link'],
            'color_count': colors[1]
        })
        
    # Sort the images by the color score in descending order
    sorted_images = sorted(processed_images, key=lambda x: x['color_score'], reverse=True)
    
    # Remove images with a color score of 0
    sorted_images = [image for image in sorted_images if image['color_score'] > 0]

    # Optionally filter based on preferences and selected images
    if selected_images:
        sorted_images = [image for image in sorted_images if image['title'] in selected_images]

    # Further filtering based on user preferences can be added here if required

    # Randomly select an image from the filtered list
    if sorted_images:
        return {
            "image": random.choice(sorted_images),
            "userName": user_name
        }
    else:
        return {"error": "No suitable images found."}

if __name__ == '__main__':
    app.run(debug=True)



'''
Input colors, Vastness, Distance, Vibrance

If many colors, get colorful?

If vast -> clusters, fields, stellar formations, 
if not vast -> galaxies, supernovae, nebulae, planets

If distance -> Longer distance
if not distant -> shorter distance

If vibrant -> choose photos with multiple colors
if not vibrant -> choose photos with one or two colors

Look through list of images from json and pick an image that respectively passes through each standard:
    Look through for color
    Look through for vast
    Look through for vibrance
    Look through for distance
''' 
