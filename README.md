# Cyber-Physical Digital Twin for Real-Time OEE and Thermal Stress Isolation

This project is a portfolio-ready prototype of a cyber-physical digital twin for a high-temperature production line. It combines a 1D transient thermal model, thermal stress accumulation, expansion estimation, and a discrete-event OEE simulator that shows how localized mechanical degradation can shift system bottlenecks.

## Why It Matters

Kiln-fed ceramic, glass, metal, and heat-treatment lines can lose entire shifts when thermal shock damages rollers, bearings, conveyors, or downstream handling equipment. Traditional predictive maintenance may predict a component failure, but it rarely quantifies the factory-wide throughput loss caused by that degradation.

This prototype demonstrates the link between:

- Sensor-style thermal inputs
- Thermal expansion and stress accumulation
- Machine availability degradation
- OEE and bottleneck movement across a production line

## What Is Included

- `src/digital_twin_oee.py` - runnable Python simulation
- `data/sample_plc_stream.csv` - synthetic PLC-style sensor stream
- `requirements.txt` - no external packages required
- `GITHUB_NOTES.md` - how to publish this project to GitHub

## Run

```bash
python src/digital_twin_oee.py
```

The script prints a time-series summary of temperature, stress index, expansion, OEE, and the active bottleneck.

## Engineering Concepts Demonstrated

- Lumped 1D transient thermal modeling
- Thermal expansion calculation
- Stress and damage accumulation
- OEE decomposition: availability, performance, quality
- Discrete-event style bottleneck estimation
- Cyber-physical architecture thinking for PLC-connected production systems

## Future Hardware Extension

In a real deployment, `load_sensor_stream()` would be replaced by a live data adapter for an OMRON PLC, MQTT broker, OPC UA server, or historian database.
