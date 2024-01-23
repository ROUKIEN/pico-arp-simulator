# Pico ARP simulator

A windowed application simulating the behavior of a Kitronik ARP buggy, driven using a tcp socket.

# About the simulator

I use this simulator during workshops with teenagers when I don't have enough robots for them. I wrote a client that allows to drive the robot.
They can then reuse the same API to drive either the concrete robot, whose code runs on a pi pico, or in the simulator.

# Starting the simulator

We only provide .AppImages for now. Should run on any linux distro. Please download the latest version of the simulator from the releases page at https://github.com/ROUKIEN/pico-arp-simulator/releases.

Please run `chmod +x pico-arp-simulator.AppImage`. You can then execute it by double clicking on it or by running it in a terminal.

# Building

I don't provide Windows/Mac osX binaries for now.
Windows support is expected at some time, feel free to help with this if you want to!

## Generating .AppImage

```shell
# Requires docker for build reproducibility
make appimage
```

# Networking

The simulator starts a tcp socket listening on `localhost:12345`.
