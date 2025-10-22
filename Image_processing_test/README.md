Here are the compile commands run the first 1 to generate the isolated images, the second one to match templates:

python3 opencv_test.py base_monkey_meadow.png test_input_small.mp4

python3 test_detection.py dart_monkey.png output_video.mp4 final_video.mp4


-----   NOTE   -----
currently the dart_monkey.png has a background hindering the matcher, further testing needed.