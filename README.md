# Positivo Casa Inteligente

This is a HomeAssistant integration for the Positivo Casa Inteligente smart home devices.

This is designed based on a long process of reverse engineering Positivo's app, including the key extraction. You can find more in [this blog post](https://blog.rgsilva.com/reverse-engineering-positivos-smart-home-app/). **Positivo owns any right to their app and keys, obviously**.

Their network uses the Tuya Cloud as backend, so their devices are actually compatible with other integrations, such as Local Tuya. This, however, is an integration that simulates the standard app use, which allow an easier approach for integration these devices into your current setup, as the alternatives are, sometimes, cumbersome. For example, Local Tuya requires you to extract the local key of each device, which is not always easy. Another approach is to flash these devices with a custom firmware (such as Tasmota), but opening electrical devices like these imposes a risk and could harm both the user and the user's environment. Hence this thing.

The Tuya Cloud have multiple API versions. The one I'm using here is a very bad and old one which uses weak RSA encryption (textbook RSA), and as such I've added a working implementation of it. Originally I was using PyCrypto for this job, but it is unsupported by HA, being replaced by PyCryptodome. The latter, however, won't support textbook RSA, so I had to kind of implement my own. Yeah, yeah, you should never implement your own crypto, but this is textbook RSA so it's not _mine_ :)

**This is provided AS IS. I am not responsible if anything goes wrong and your house gets burned down because you used my code. I am also not responsible if you get banned in the app for using this, although this is very unlikely¹**

¹ during the development I usually do dozens of logins per hour and nothing happend (so far).

# Supported devices

- Outlet (10A one)
- IR controller (yes, really!)

# Missing features/TODO list

There are always missing things and stuff we can make better. This list is obviously incomplete!

- Detect a device that has gone online or offline in realtime.
- The API client must be rewritten in proper Python standard and not this shitty code I made.
- Support for lightbulbs.
- Support for the new API version (2.0) which has all requests encrypted.

# Credits

I'm for sure missing stuff here, but these are the main ones:

- [Local Tuya](https://github.com/rospogrigio/localtuya)
- [TuyAPI](https://github.com/codetheweb/tuyapi)
