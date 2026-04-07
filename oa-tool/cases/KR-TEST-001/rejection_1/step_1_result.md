## [Step 1: 본원발명 분석]

### 1. 거절 대상 청구항 중 독립항 식별

거절 대상 청구항(1, 3, 5항) 중 다른 청구항을 인용하지 않는 독립항은 다음과 같습니다.

*   **청구항 1**

### 2. 독립항(청구항 1) 구성요소 분해 및 기술적 의미/효과 설명

**청구항 1:** A method for measuring a position, comprising:
   (A) collecting a plurality of wireless signals;
   (B) calculating a first positioning reference value based on the collected wireless signals; and
   (C) determining a position by fusing the first positioning reference value with inertial sensor data.

---

**구성요소 (A): collecting a plurality of wireless signals**

*   **기술적 의미:** 단말 장치가 주변 환경으로부터 복수의 무선 신호(예: Wi-Fi, Bluetooth, cellular signals 등)를 수집하는 단계. 이는 위치 측정을 위한 원시 데이터를 확보하는 과정입니다.
*   **효과:** 종래 GPS 기반 측위의 실내 정확도 저하 문제나 Wi-Fi AP 지문 정보 변화에 취약한 단점(spec [배경기술])을 극복하기 위해 다양한 무선 신호를 활용할 수 있는 기반을 마련합니다. (spec [0001])

**구성요소 (B): calculating a first positioning reference value based on the collected wireless signals**

*   **기술적 의미:** 구성요소 (A)에서 수집된 복수의 무선 신호들을 기반으로, 위치 측정에 활용될 수 있는 제1 측위 기준값(first positioning reference value)을 산출하는 단계. 이 기준값은 명세서 [0002]에 따라 RSSI, RTT, AoA 중 적어도 하나를 포함하는 가중 평균값으로 정의될 수 있습니다.
*   **효과:** 원시 무선 신호 데이터를 직접 사용하는 것이 아니라, 이를 가공하여 측위에 더 적합한 형태의 기준값을 생성함으로써, 신호의 불안정성이나 환경 변화에 따른 오차를 줄이고 측위 정확도를 향상시킬 수 있는 기반을 제공합니다. (spec [0001], [0003])

**구성요소 (C): determining a position by fusing the first positioning reference value with inertial sensor data**

*   **기술적 의미:** 구성요소 (B)에서 산출된 제1 측위 기준값과 관성 센서(inertial sensor) 데이터(예: 가속도계, 자이로스코프 데이터)를 융합(fusing)하여 최종 위치를 결정하는 단계.
*   **효과:** 무선 신호 기반 측위의 단점(예: 신호 음영 지역, 다중 경로 오차)과 관성 센서 기반 측위의 단점(예: 드리프트 오차 누적)을 상호 보완합니다. 이를 통해 실내 환경 등에서 종래 기술 대비 50% 이상 측위 오차를 줄이는 현저한 효과(spec [0005])를 달성하여, 보다 정확하고 안정적인 위치 측정이 가능하게 합니다. (spec [0004])