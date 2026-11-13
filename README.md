# HUMAN | AIOps & Critical Systems
### 3D Data Center Cold-Aisle Digital Twin & Predictive Thermal Anomaly Engine

**Mimari & Geliştirme:** Hüseyin Üstündağ — Veri Merkezi & Kritik Altyapı Uzmanı | Yapay Zekâ & Otomasyon  
**Konum:** Ankara, Türkiye  
**Canlı 3D NOC Portalı:** [https://huseyinustundag.github.io/human-dc-aiops-engine/](https://huseyinustundag.github.io/human-dc-aiops-engine/)

---

## 🏗️ Sistem Mimarisi
**HUMAN DC-AIOps Engine**, fiziksel veri merkezi altyapısını (Katman-1 kablolama, sıcak/soğuk koridor hava akışı, 42U kabinet termal zarfı) üç boyutlu bir dijital ikiz (3D Digital Twin) arayüzüyle birleştirirken, arka planda **DMTF Redfish API** üzerinden toplanan telemetri verilerini **Isolation Forest** makine öğrenmesi modeliyle analiz eder.

```text
[Server BMC / iDRAC / iLO] ──(DMTF Redfish REST API)──> [Telemetry Collector]
                                                                 │
                                                                 ▼
[3D Cold-Aisle NOC Portal] <──(Root-Cause JSON)── [ML Anomaly Engine (Isolation Forest)]
