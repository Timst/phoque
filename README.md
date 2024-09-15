# Phoque

## What is this?
This is a queuing system I came up with to organize my Burning Man's camp's line. You see:
- We make crêpes
- People really like crêpes
- Crêpes take a couple of minutes to cook
- People (who, as I mentioned, really like crêpes) come faster than that

This quickly results in a line (or "queue", if you're European), which in our case could take as long as one hour to get through. I don't know if you've ever waited one hour under 100°F sun while very hungry, but I have, and let me tell you that it is not fun. Hence, this thing.

### What it do? 
This is a comprehensive (read: over-engineered) line management system. Here's the workflow:

- People slam a big red button (I'll go over the hardware later)
- This takes a picture of them on a webcam, and prints in on a receipt along with a number
- Meanwhile, we're crêpin'. When a crêpe is ready, we press a "call" button
- This makes an audio announcement, and increments the current number on a public-facing screen, so that people know where we're at
- On our side, along with the call button, we also see a screen that let us know the state of the line (current number, max number, estimated wait, etc)

And that's pretty much it. Numbers are tracked in a database so you can later make little charts and stuff (little charts and stuff not included; use Grafana or something). There is also a "photobooth" mode that strips out the numbering stuff but adds a viewfinder. That's cool at parties.

Note that you strictly speaking don't need to use a thermal receipt printer: any old printer would do. But thermal printers are fast (the whole thing takes about one second from button press to the receipt being out, and that's mostly throttled by the system), and thermal paper rolls are inexpensive, plus they don't require ink or toner. So that essentially makes this a (very low res) instantaneous photobooth.

Here it is in motion: https://photos.app.goo.gl/PGY3nPgdvAmaGse49

### Why is it called that? 
"Phoque" (pronounced "fok") is French for "sealion". Believe it or not, it is in fact not a pun on "fuck". Instead it's a contraction of "pho" and "queue" (and again yes, that sounds a lot like "fuck you", but no, not on purpose). This is because before the crêpe camp, I originally built this for a different camp that was serving phở. And why "sealion"? That's just a coincidence. Not everything has to be meaningful, you know.

## Hardware
This is meant to run on a Rasperry Pi. I've been using a Pi 4B, this would likely also work on a 5 or on an older Pi.

Besides that, the big items you'll need is a button ([that's the one I use](https://www.amazon.com/gp/product/B00XRC9URW/)), a webcam (anything will do, I use this logitech cam that everybody has), a thermal receipt printer (that's the most specialized and expensive piece of kit; I use this [MUNBYN](https://www.amazon.com/dp/B0779WGYHS) printer), a keyboard, and maybe a couple of screens.

I could go through the rest of the system here, but instead let me give you the link to the "schematics" (more of a guide to putting everything together) that lists everything you need, complete with a diagram and step-by-step instructions: https://docs.google.com/document/d/1qJzJxlinTLHUv-rM7RpuQfxlVQy0EvKh1EnHSkjROCY/edit?usp=sharing

## Setting up
So there's probably some stuff you need to do on your system to make all of this work. You know like uuh, installing some packages, probably some RPI-specific config and stuff. Also I think something related to CUPS quirks for this type of printer? Unfortunately I don't recall most of what I did and didn't take notes. Sorry!!! 

At least I did include a requirements.txt, so you can start by installing the required Python packages by doing `pip install -r requirements.txt`. Then you can run it by doing `python3 phoque.py`, at which point it will almost certainly not work. You probably need to export a display variable or something. 

On top of the various processes to start the camera etc, the system launches a server with two endpoints: localhost:5000/public is the public facing screen that shows the current called number and estimated wait (based on averaging the wait over the last 15 crêpes); localhost:5000/admin is the backoffice screen with more details.

The system also listens for keystrokes, so careful with what you do once it's running. Here are the keys:
- `d` calls the next number. It increments the current number and makes the audio call
- `f` calls the current number again. People never pay attention to anything, so you'll be using this a lot.
- Maintaining `g` for 2s+ switches between different modes. There are four: "open" (standard mode), "last call" (works like the standard mode, but the public screen shows a flashing message that the line is about to close), "finishing" (people can't get new tickets, but you can still call old ones), and "closed" (the whole system is suspended)
- Maintaining `h` for 2s+ resets the count to 0. This is non-destructive: internally this starts a new session, but old numbers are still saved in DB.

Rather than using a regular keyboard, I got one of these [little 4-key minikeyboards](https://www.amazon.com/gp/product/B093WJ38D9/). You can configure them to assign a logical key to each physical key, and then I printed some labels, and voilà.

I also recommend turning this into a systemd service. _In theory_, that way, as soon as you start the Pi, everything should boot up on its own, including the displays. This almost never works, but hey, you know, it could.

## Future plans
This whole code is due for a major overhaul sooner or later, if only because the web code is _ridiculous_. It uses a Flask server to start the two endpoints I mentioned, which are html pages with [htmx](https://htmx.org/) code that calls the same endpoints to refresh themselves. This is how I, a professional full stack dev, decided to solve the "how do I have a client and server in the same app" problem. It works, but it's really dumb and prevents me from adding a few features that would be useful, for example flashing the public screen when a number is called.

Eventually I'll transition this to make a properly separated architecture where a server exposes a REST API that both "display clients" and "button clients" talk to. The primary benefit would be that not everything has to be connected to the one Raspberry Pi and I can, for example, put the button at the entrance of the camp and the admin screen in the back (currently I use a wireless HDMI transmitter to have the public screen separated from the rest of the system, but that only works for this)

Editing the ticket template is a bit of a pain, too. You have to guess at everything (the position of each text block, font size, etc), and it takes a while to get right. I'm not sure how, but if I could somehow add a template editor, that would be swell.

As I mentioned you could use the DB to display some stats and graphs and whatnot. 

At one point I toyed with saving the pictures and then displaying them on the public screen when the number is called, so that people would pay more attention (the #1 problem with this whole thing). Eventually we veto'd the idea out of privacy concerns: this being Burning Man, we had at least one woman flash her breasts at the camera. She might or might not have consented to have them displayed in 4K on a giant screen later, so better not to risk it. It wasn't very hard to implement, and in fact I think the code is still here but commented out. There might be something there, if you can navigate the ethical issues.
