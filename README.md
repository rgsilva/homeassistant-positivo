
# Positivo Casa Inteligente

This is a HomeAssistant integration for the Positivo Casa Inteligente smart home devices.

This is designed based on a long process of reverse engineering Positivo's app, including the key extraction. You can find more in [this blog post](https://blog.rgsilva.com/reverse-engineering-positivos-smart-home-app/). **Positivo owns any right to their app and keys, obviously**.

Their network uses the Tuya Cloud as backend, so their devices are actually compatible with other integrations, such as Local Tuya. This, however, is an integration that simulates the standard app use, which allow an easier approach for integration these devices into your current setup, as the alternatives are, sometimes, cumbersome. For example, Local Tuya requires you to extract the local key of each device, which is not always easy. Another approach is to flash these devices with a custom firmware (such as Tasmota), but opening electrical devices like these imposes a risk and could harm both the user and the user's environment. Hence this thing.

The Tuya Cloud have multiple API versions. The one I'm using here is a very bad and old one which uses weak RSA encryption (textbook RSA), and as such I've added a working implementation of it. Originally I was using PyCrypto for this job, but it is unsupported by HA, being replaced by PyCryptodome. The latter, however, won't support textbook RSA, so I had to kind of implement my own. Yeah, yeah, you should never implement your own crypto, but this is textbook RSA so it's not _mine_ :)

**This is provided AS IS. I am not responsible if anything goes wrong and your house gets burned down because you used my code. I am also not responsible if you get banned in the app for using this, although this is very unlikely¹**

¹ during the development I usually do dozens of logins per hour and nothing happend (so far).

# Supported devices

- Outlets
  - 10A: fully working
  - 20A: not implemented (shouldn't be hard, I just don't have one)
- IR controller (yes, really)
  - Basic TV remote control
  - Basic generic light control

Device support increases based on my own demand, but feel free to send PRs for devices you own. If you don't feel like reverse engineering the device (in case it's fully unsupported) and wants to send me one so I can try to do it, let me know.

# Missing features/TODO list

There are always missing things and stuff we can make better. This list is obviously incomplete!

**Device support**

- Detect a device that has gone online or offline in realtime. The obvious solution is some kind of periodic check, but I believe the API has a MQTT endpoint we can subscribe to. I still have to figure out how it works though. Last update: I've extract the authentication keys (by mistake lol), but couldn't figure out how the communication is encrypted. There are too many MQTT-related classes on the project itself.
- Support for lightbulbs.
- Improve how IR is handled.
  - Currently the state is always unavailable. I believe we can improve this by having some kind of internal stat, possibly though an opt-in/out feature.
  - The commands are case-sensitive. This is easy, we can simply make them case insensitive.
  - Turn on and off commands fail. We can map those to the words "on" and "off" and find commands matching those words.

**API**

- The API client must be rewritten in proper Python standard and not this shitty code I made. This includes better handling of the gateway device, which is very important for the smart IRs.
- Sometimes the authentication crashes. The API still works, but the log gets full of errors which I still need to debug.
- Keep the token between HA restarts. This is important to avoid flooding the server with logins on every restart.
- Improve device detection though Tuya official codes. This can easily be found on their own [official implementation](https://github.com/tuya/tuya-home-assistant) of this integration¹ and [their official documentation](https://developer.tuya.com/en/docs/iot/categorykgczpc?id=Kaiuz08zj1l4y). Both, as far as I know, do **not** support Positivo's devices - unless you connect them to Tuya directly, of course.
- Support for the new API version (2.0) which has all requests encrypted. This can be tricky as it requires figuring out how the requests are actually being made. Nothing a crazy weekend on Frida wouldn't solve, I suppose.

# Credits

I'm for sure missing stuff here, but these are the main ones:

- [Local Tuya](https://github.com/rospogrigio/localtuya)
- [TuyAPI](https://github.com/codetheweb/tuyapi)
