# ==============================================================================
# Copyright (c) 2026 Hüseyin Üstündağ | HUMAN — AIOps & Critical Systems
# All Rights Reserved. Unauthorized copying, commercial deployment, or 
# modification of this file, via any medium, is strictly prohibited.
# ==============================================================================

import json
import datetime
import numpy as np
from sklearn.ensemble import IsolationForest
from telemetry_collector import RackTelemetryPayload

class ThermalAnomalyEngine:
    """
    Veri merkezi kabinet telemetri verilerinde çok değişkenli anomali tespiti
    ve Katman-1 / soğutma kök neden analizi yapan AIOps motoru.
    """
    def __init__(self, contamination: float = 0.05):
        self.model = IsolationForest(
            n_estimators=150,
            contamination=contamination,
            random_state=42
        )
        self._train_baseline_model()

    def _train_baseline_model(self):
        rng = np.random.default_rng(42)
        inlet = rng.normal(22.5, 1.5, 500)
        power = rng.normal(550.0, 80.0, 500)
        delta_t = 8.0 + (power / 100.0) * 1.1 + rng.normal(0, 0.6, 500)
        fan_rpm = 35.0 + (power / 100.0) * 4.5 + rng.normal(0, 2.5, 500)

        baseline_matrix = np.column_stack((inlet, delta_t, fan_rpm, power))
        self.model.fit(baseline_matrix)

    def _infer_root_cause(self, payload: RackTelemetryPayload) -> tuple[str, str]:
        if payload.inlet_temp_c > 27.0:
            return (
                "COLD_AISLE_CONTAINMENT_BREACH",
                "Giriş sıcaklığı ASHRAE A1 üst sınırını (27°C) aştı. Soğuk koridor izolasyonunu, blanking panelleri ve CRAC üfleme debisini kontrol edin."
            )
        if payload.delta_t > 16.5 and payload.avg_fan_rpm_pct > 75.0:
            return (
                "REAR_EXHAUST_IMPEDANCE",
                "Giriş sıcaklığı normal ancak egzos Delta-T ve fan devri kritik seviyede. Kabinet arkası Katman-1 kablolama yoğunluğunu ve sıcak hava tahliyesini inceleyin."
            )
        return (
            "THERMAL_EFFICIENCY_DRIFT",
            "Güç tüketimi ve soğutma tepkisi arasında korelasyon sapması tespit edildi. Sensör kalibrasyonu ve hava akışı dengelemesi önerilir."
        )

    def analyze(self, payload: RackTelemetryPayload, dc_zone: str = "ANK-DC01-HALL-B") -> dict:
        features = np.array([[
            payload.inlet_temp_c,
            payload.delta_t,
            payload.avg_fan_rpm_pct,
            payload.power_draw_watts
        ]])

        prediction = self.model.predict(features)[0]
        score = round(float(self.model.decision_function(features)[0]), 4)
        is_anomaly = bool(prediction == -1)

        if is_anomaly:
            root_cause, recommendation = self._infer_root_cause(payload)
        else:
            root_cause = "NOMINAL_OPERATION"
            recommendation = "Termal zarf ve hava akışı ASHRAE A1 standartları dahilinde."

        return {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "datacenter_zone": dc_zone,
            "rack_id": payload.rack_id,
            "metrics": {
                "inlet_temp_c": payload.inlet_temp_c,
                "exhaust_temp_c": payload.exhaust_temp_c,
                "delta_t": payload.delta_t,
                "avg_fan_rpm_pct": payload.avg_fan_rpm_pct,
                "power_draw_watts": payload.power_draw_watts
            },
            "ai_diagnosis": {
                "is_anomaly": is_anomaly,
                "anomaly_score": score,
                "root_cause": root_cause,
                "recommendation": recommendation
            }
        }

if __name__ == "__main__":
    engine = ThermalAnomalyEngine()
    suspect_rack = RackTelemetryPayload(
        rack_id="RACK-B04",
        inlet_temp_c=24.8,
        exhaust_temp_c=43.2,
        avg_fan_rpm_pct=84.0,
        power_draw_watts=620.0
    )
    print(json.dumps(engine.analyze(suspect_rack), indent=2, ensure_ascii=False))
