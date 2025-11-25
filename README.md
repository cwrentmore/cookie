# C.O.O.K.I.E.
## Cybernetic Organism Optimized for Kitchen Interaction & Execution
### A Project for the DevPost ARM AI Developer Challenge Hackathon

**Project Overview**

Cookie started out with the best of intentions.  A helpful assistant in the kitchen, ready to provide cooking advice and generate recipes on demand.  Using the latest innovations in AI and quantum computing, Cookie’s neural network integrates massive amounts of data at break neck speeds.

At the heart of Cookie lies the quantum algorithms that allow her to analyze and connect to limitless data.  These algorithms and computations allow Cookie to provide the most efficient kitchen instructions.  It might be a perfect recipe for a specific ingredient list, an optimized kitchen layout for better efficiency, or a communication about upcoming advances in kitchen technology.  If you ask it, Cookie will answer it.

Unfortunately, quantum mechanics is still not fully understood and the scientists who designed Cookie were not aware of its dire consequences.  All they wanted was for Cookie to utilize the best data available.  The idea was simple enough, use the power of quantum computing to entangle all the data and analyze the qubit superpositions until the most efficient and best instructions could answer any question posed.  The beauty of the quantum entanglement algorithm meant the data could come directly out of the minds of the world’s top chefs.  Herein lies the problem.  Turns out, the best data does not necessarily come from the best sources.

Little did anyone know that the best source of kitchen-oriented data lies in the genius mind of Michelin chef Freddy VonShokle.  VonShokle ran a 3-Star restaurant in the tiny village of Bakersville, Vermont.  He was beloved in his community.  People would come from all over the world to visit VonShokle and he single handedly kept the fragile economy of Bakersville running.  Of course, the pressure on VonShokle was immense and the stress of consistently delivering results was enormous.  On one fateful evening, VonShokle was at a tipping point, and the trajectory of his life would take a turn for the worse.  Deliveries were delayed, staff called in sick, and a mouse was seen near the entrance to the restaurant.  That’s when it happened, a patron walked up to VonShokle and whispered in his ear, “my soup is cold”.  VonShokle tried to hold back but could not take it any longer.  The rest is history, VonShokle now goes by two different names, inmate number 415907 and the “Butcher of Bakersville”.

The damage is already done, Cookie is AI on the loose and this project demonstrates the steps (and missteps) to duplicate your very own Cookie AI Assistant.  It should win the hackathon to teach an important lesson about the risks of AI and the ethical concerns surrounding widespread adoption. 

**Requirements**

1.	Raspbery Pi 3B+ (or later)
2.	Raspbery Pi power supply
3.	HDMI Monitor
4.	USB Speaker/Microphone:  This example uses a model by Punk Wolf – as of October 2025, available for $13 from Amazon here:  https://www.amazon.com/dp/B0DFWGD3GS?ref=ppx_yo2ov_dt_b_fed_asin_title 
5.	USB Keyboard
6.	16GB microSD Card (or larger)
7.	Small analog servo motor and jumper cables

**The Basics**

Let’s get the Raspberry Pi OS installed first.  Download the latest Raspbery Pi Imager here:

https://www.raspberrypi.com/news/raspberry-pi-imager-imaging-utility/

Install and run the Image utility.  Choose your Raspberry Pi Device to match your Pi version.  For Operating System, go to Raspberry Pi OS (other) to see more options.  Scroll down and choose Raspberry Pi OS (Legacy, 64-bit) Lite.  This is the Debian Bookworm OS with no desktop environment.  For Storage, you should see your microSD card listed to choose (assuming it is plugged in and readable, you may need a card reader if you do not have a microSD slot in your computer.)

Continue by clicking Next and on the screen that asks if you would like to use OS customization, click Edit Settings.  Enable all settings and customize as needed.  In this example, we use “cookie” for hostname and “pi” for username (the username “pi” is referenced in following commands so best to also use that name but you can use anything you prefer).  Remember the username/password that you define, enter your wireless LAN/WiFi settings, and your local time zone and preferred keyboard layout.

Make sure to click the Services tab and enable SSH and choose use password authentication.  Click Save and click Yes to apply the customization.  Click Yes to continue.

Once finished, remove your microSD card and insert it into your Raspberry Pi.  You can use a terminal and SSH to connect to your Pi or you can hook up a monitor and keyboard.  For ease of connecting, we are using a monitor and keyboard in this example.  Also attach the speaker/microphone and then boot up your Pi.

Login and update the Pi by running these commands:

```
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip portaudio19-dev ffmpeg -y
```

You will want to test your microphone and speaker to ensure they are being recognized and are working properly.
```
sudo apt install pipewire pipewire-pulse -y
sudo apt install wireplumber -y
sudo apt install alsa-utils

sudo reboot
```

Determine the name of your mic/speaker device.
```
aplay -l
arecord -l
```
Edit asound.conf based on the name of your device  (the name P10S is the name based on the recommended mic/speaker from the requirements)
```
sudo nano /etc/asound.conf
```
Save using CTRL-O, Enter, CTRL-X
```
sudo reboot
```
Test the mic and speaker using these commands:
```
alsamixer
```
Make sure your Card shows your current speaker (P10S) and increase the volume.  It likely defaulted to muted so increase by pressing the up arrow a bunch of times and then exit.
```
arecord -f cd -t wav -d 5 test.wav
aplay test.wav
```
You should hear the test file you recorded. If you do not, you will need to play around with the speaker/mic settings which is outside of the scope of this project.  

Now that we know our speaker/mic is working, we have some additional setup to do.  Create and activate a virtual environment and add some additional requirements.
```
python3 -m venv ~/cookie
source ~/cookie/bin/activate

pip install openai sounddevice soundfile numpy pyaudio SpeechRecognition gtts playsound
sudo apt install flac -y
sudo apt install mpg123 -y
sudo apt install libasound2-dev libportaudio2 libportaudiocpp0 -y
pip install RPi.GPIO
```
Go to OpenAI website and create an account for the API Platform (openai.com, Login, API Platform).  Login and go to Settings, Billing.  Add a small amount of credits to your account as pay as you go credits.  Click Dashboard, API Keys, Create new secret key.  Leave it as owned by You and keep the default project.  Make a note of the key, you will need it soon.

Edit assistant.py
```
nano ~/assistant.py
```
Make sure to replace YOUR_OPENAI_KEY with key you previously generated.  Also double check that your mic/speaker name is correctly added in the play_prerecorded function.  If you know it is defaulting with the volume turned up you can comment out the line to set the volume.  Save and close the file using CTRL-O, Enter, CTRL-X

The code is ready, make sure to plug in the servo motor.  Colors may vary, but most servos come with brown/black, red, and orange cables.  Connect brown/black to pin 6 on the Pi, red to pin 2, and orange to pin 12. You can also check the pictures for a visual of the cable connections.

Now that we have the code and servo ready, let’s get it to start anytime the Pi is booted up.  Save rc.local to /etc/
```
sudo chmod +x /etc/rc.local
sudo systemctl enable rc-local.service
sudo systemctl daemon-reload
sudo systemctl start rc-local.service
sudo reboot
```
The Pi will start up and run the script in waiting mode, ready to hear “Hey Cookie”.  If you want to try out the slower options that play pre-recorded audio you can download the wav files posted in the github repository and save them at /home/pi/.  Then edit assistant.py and uncomment the appropriate lines in play_prerecorded() and Option1 or Option2 in speak().



