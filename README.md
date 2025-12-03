# CMPT-310
Can we beat Bloons TD 6 with AI?

# HOW TO RUN:
**model creation**
to create the model, you must navigate to the model directory
then run this command:
python ./train.py data binary_maps model.pth
this will create a trained model

**running the model**
to run the created model, move your model into the model_weights directory
open bloons tower defense 6
play the monkey meadows map
then run this command in the CMPT-310 directory and quickly tab into bloons tower defense 6
python ./play.py
it will take over playing the game (:
to terminate the program, move you mouse to one of the corners of the screen.

**video processing**
to process data, first navigate to the Video_processing directory
then run this command
python ./FullDetection.py test_data.mp4 monkey_meadow.png final_output.txt
you can then move your data into the model/data folder to train a model on.
Note: data is already provided in this folder to run the model.