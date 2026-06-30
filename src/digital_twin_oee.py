from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "sample_plc_stream.csv"


@dataclass
class SensorFrame:
    minute: int
    kiln_exit_c: float
    ambient_c: float
    line_speed_m_min: float
    roller_load_n: float
    defect_rate: float


@dataclass
class TwinState:
    surface_c: float
    core_c: float
    stress_index: float
    expansion_mm: float
    oee: float
    bottleneck: str


def load_sensor_stream(path: Path = DATA_PATH) -> list[SensorFrame]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = csv.DictReader(handle)
        return [
            SensorFrame(
                minute=int(row["minute"]),
                kiln_exit_c=float(row["kiln_exit_c"]),
                ambient_c=float(row["ambient_c"]),
                line_speed_m_min=float(row["line_speed_m_min"]),
                roller_load_n=float(row["roller_load_n"]),
                defect_rate=float(row["defect_rate"]),
            )
            for row in rows
        ]


def update_thermal_network(previous: TwinState, frame: SensorFrame, dt_min: float = 5.0) -> tuple[float, float]:
    surface_tau = 8.0
    core_tau = 22.0
    surface_c = previous.surface_c + (frame.kiln_exit_c - previous.surface_c) * dt_min / surface_tau
    core_c = previous.core_c + (surface_c - previous.core_c) * dt_min / core_tau
    return surface_c, core_c


def estimate_stress(surface_c: float, core_c: float, load_n: float) -> float:
    thermal_gradient = abs(surface_c - core_c)
    load_factor = max(0.0, (load_n - 3800.0) / 2200.0)
    return min(1.0, 0.0018 * thermal_gradient + 0.42 * load_factor)


def estimate_expansion(core_c: float, ambient_c: float, length_mm: float = 1200.0) -> float:
    steel_alpha = 12e-6
    return steel_alpha * length_mm * (core_c - ambient_c)


def simulate_oee(frame: SensorFrame, stress_index: float) -> tuple[float, str]:
    availability = max(0.50, 0.98 - 0.34 * stress_index)
    performance = min(1.0, frame.line_speed_m_min / 18.5)
    quality = max(0.80, 1.0 - frame.defect_rate - 0.07 * stress_index)
    oee = availability * performance * quality

    station_capacity = {
        "kiln exit rollers": 100.0 * availability,
        "cooling conveyor": 94.0 - 15.0 * stress_index,
        "vision inspection": 90.0 * quality,
        "packaging cell": 88.0 * performance,
    }
    bottleneck = min(station_capacity, key=station_capacity.get)
    return oee, bottleneck


def run_twin() -> list[TwinState]:
    stream = load_sensor_stream()
    state = TwinState(
        surface_c=stream[0].ambient_c,
        core_c=stream[0].ambient_c,
        stress_index=0.0,
        expansion_mm=0.0,
        oee=0.0,
        bottleneck="startup",
    )
    history: list[TwinState] = []

    for frame in stream:
        surface_c, core_c = update_thermal_network(state, frame)
        stress_index = estimate_stress(surface_c, core_c, frame.roller_load_n)
        expansion_mm = estimate_expansion(core_c, frame.ambient_c)
        oee, bottleneck = simulate_oee(frame, stress_index)
        state = TwinState(surface_c, core_c, stress_index, expansion_mm, oee, bottleneck)
        history.append(state)

        print(
            f"t={frame.minute:02d} min | surface={surface_c:7.1f} C | "
            f"core={core_c:7.1f} C | stress={stress_index:0.3f} | "
            f"expansion={expansion_mm:5.2f} mm | OEE={oee:0.3f} | bottleneck={bottleneck}"
        )

    return history


if __name__ == "__main__":
    run_twin()
