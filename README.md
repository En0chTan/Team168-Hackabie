# UMHackathon 2025
Domain 3 (Task 1)
© Team Hackabie

<<<<<<< Updated upstream
<<<<<<< Updated upstream
## Team Members
<ul>
  <li>Enoch Tan Jeng Sen</li>
  <li>Chee Rui</li>
  <li>Tang Wei Xiong</li>
  <li>Foo Yau Yun</li>
</ul>

<br></br>

## Links
<ul>
  <li><a href="">Presentation Video</a></li>
  <li><a href="https://www.canva.com/design/DAGkG5SLV8Q/tyQPBf4vpVJaaoKeYXwIUg/edit?utm_content=DAGkG5SLV8Q&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton">Presentation Slides</a></li>
</ul>

=======
>>>>>>> Stashed changes
Folders
- Main_UI
Contains the AI implemention using Python Flask and Tkinter, In the final product, Python Flask would be probably used/C++ for better performance

- Voice_Recognition
Contains the capturing of user voiceprints and comparing it to new voices, and also an example of how the AI will respond

- Gesture_Mode
Basically this just captures specific amplitudes/shapes and determine whether if its a ough. Future implementations, may include audio capture for custome gesture recognition.

- Extras
Here, you can see the early implementations and breakdown of our program.

If we are available to go into the finals, this will be our final implementation.
(1) Real time audio will be captured and processed into segments.
(2A) The segments starting with "Hey Grab" will trigger recording mode. 
(2B) If 3 or a custom instances of "gestures" is captured, emergency mode will be triggered.
(3) The program will capture the ending of a sentence either through VAD or User Voice Recognition Models.
(4) The complete audio of the sentence will be sent into a server and processed by a Speech-To-Text Model.
(5) The text processed will now be compared with available commands (or translated as needed) and matched with the correct intents.
(6) Now the server can process the correct commands and go to Task 2! 

<<<<<<< Updated upstream
Thank you, if you're interested in how we'll do this, do consider letting us into finals and (maybe give us some datasets/credits for model training purposes (or not!))

<br></br>

## Features Voice Assistant for Drivers

### Voice Shortcut for Common Tasks

- **"Call Passenger"**: Activates phone mode for easy communication.
- **"Send message to [x]"**: Initiates message input, taking the next sentence as the content and prompting for confirmation when to end.
- **"Start navigation"**: Launches Google Maps for seamless route planning.
- **"Hi"**: Triggers a personalized greeting, addressing the user by name.
- **"I cannot find leh"**: The system will respond with the prompt, “Do you want to call the passenger?”
- **"What’s the weather in the next [x] hours?"**: Provides weather details for the specified time and location.

### Next-Passenger Mode

- The system will notify the driver with the voice prompt:  
  **"You have a new ride request from Jalan Ampang. ETA: 6 minutes. Do you want to accept?"**
  
- If the driver responds **"Yes"**, the AI confirms the request with:  
  **“Order confirmed; navigating now.”**

### Situational Awareness

- **Rerouting Function**:  
  If there is heavy traffic, the system will suggest,  
  **"Traffic ahead is slow, consider rerouting."**

- **Weather Awareness**:  
  If weather conditions change, the AI will notify the driver, such as,  
  **“It’s raining, drive cautiously.”**

- **Fatigue Awareness**:  
  The system will track driving time and alert the driver, for example:  
  **“You’ve been driving for 4 hours, take a break?”**

### Gesture Mode

- The driver can use gestures, such as coughing three times, to receive haptic feedback (vibration) instead of audible responses.
  
- For instance, if the driver coughs three times, the system will trigger a double vibration to initiate an emergency action, like calling the police, in situations such as a robbery.

### Voice Recognition

- During account setup, the driver is required to speak specific sentences to create a voice profile. This ensures that only the registered driver can interact with the AI.

- The system stores the driver’s accent in a database to enhance recognition accuracy.

=======
Thank you, if you're interested in how we'll do this, do consider letting us into finals and (maybe give us some datasets/credits for model training purposes (or not!))
>>>>>>> Stashed changes
