# RAT Controlling Command
## Get Sensor Data from All Boards
### Print Fromatted
```rust
rat-control -g/--get
```
### Print JSON
```rust
rat-control -g/--get --json
```

# RB (Readout Board) Controlling Command
## Get Sensor Data
### Print Fromatted
```rust
rat-control -b/--board rb -g/--get
```
### Print JSON
```rust
rat-control -b/--board rb -g/--get --json
```

# LTB (Local Trigger Board) Controlling Command
## Get Sensor Data
### Print Fromatted
```rust
rat-control -b/--board ltb -g/--get
```
### Print JSON
```rust
rat-control -b/--board ltb -g/--get --json
```
## Set Default Threshold Voltages (0: 40.0mV, 1: 32.0mV, 2: 375.0mV)
```rust
rat-control -b/--board ltb --default
```
## Reset Threshold Voltage (0.0mV) for All 3 Thresholds
```rust
rat-control -b/--board ltb --reset
```
## Set Threshold Voltage
### Set Threshold Voltage for Given Channel
```rust
rat-control -b/--board ltb -s/--set -c/--channel <Channel> -v/--voltage <Voltage>
```
### Set Threshold Voltages for All 3 Thresholds Simultaneously
```rust
rat-control -b/--board ltb -s/--set -v/--voltage <CH0Vol, CH1Vol, CH2Vol>
```
### Set Same Threshold Voltage for All 3 Thresholds Simultaneously
```rust
rat-control -b/--board ltb -s/--set -v/--voltage <Voltage>
```

# PB (Power Board) Controlling Command
## Get Sensor Data
### Print Fromatted
```rust
rat-control -b/--board pb -g/--get
```
### Print JSON
```rust
rat-control -b/--board pb -g/--get --json
```

# PA (Preamp Board) Controlling Command
## Get Sensor Data
### Print Fromatted
```rust
rat-control -b/--board pa -g/--get
```
### Print JSON
```rust
rat-control -b/--board pa -g/--get --json
```
## Set Default Voltage (58.0V) for All 16 Preamp Boards
```rust
rat-control -b/--board pa --default
```
## Reset Voltage (0.0V) for All 16 Preamp Boards
```rust
rat-control -b/--board pa --reset
```
## Set SiPM Bias Voltage
### Set Same Voltage for All 16 Preamp Boards
```rust
rat-control -b/--board pa -s/--set -v/--voltage <Voltage>
```
### Set Different Voltages for Each Preamp Boards
```rust
rat-control -b/--board pa -s/--set -v/--voltage <PA1Vol,PA2Vol,PA3Vol,PA4Vol,PA5Vol,PA6Vol,PA7Vol,PA8Vol,PA9Vol,PA10Vol,PA11Vol,PA12Vol,PA13Vol,PA14Vol,PA15Vol,PA16Vol>
```