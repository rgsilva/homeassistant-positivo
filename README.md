# Positivo Casa Inteligente

This is a HomeAssistant integration for the Positivo Casa Inteligente smart home devices.

This is designed based on a long process of reverse engineering Positivo's app, including
the key extraction. You can find more in [this blog post](https://blog.rgsilva.com/reverse-engineering-positivos-smart-home-app/).
Positivo owns any right to their app and keys, obviously. Their network uses the Tuya Cloud as
backend, so their devices are actually compatible with other integrations, such as Local Tuya.
This, however, is an integration that simulates the app usage, which allow an easier approach
for integration these devices into your current setup, as both Local Tuya and firmware-changing
approaches (such as Tasmota) can be considered a bit too difficult for new users.

Finally, the Tuya Cloud uses weak RSA encryption (textbook RSA), and as such I've added a working
implementation of it. Originally I was using PyCrypto for this job, but it is unsupported by HA,
being replaced by PyCryptodome. The latter, however, won't support textbook RSA, so I had to kind
of implement my own (copy/paste).

**This is provided AS IS. I am not responsible if anything goes wrong and your house gets burned
down because you used my code. I am also not responsible if you get banned in the app for using this,
although this is very unlikely.**

# Missing features/TODO list

- Detect a device that has gone online or offline in realtime.
- Support for lightbulbs and IR devices
- The Tuya API clien