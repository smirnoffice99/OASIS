## 한국 특허 전문가 분석: 단일성 위반 거절이유 (특허법 제45조)

### 1. 각 그룹 독립항 전문 나열

*   **청구항 그룹 A (독립항):** 청구항 1
    1.  A method for measuring a position, comprising:
        collecting a plurality of wireless signals;
        calculating a first positioning reference value based on the collected wireless signals; and
        determining a position by fusing the first positioning reference value with inertial sensor data.

*   **청구항 그룹 B (독립항):** 청구항 6
    6.  A terminal device comprising:
        a wireless signal collector configured to collect a plurality of wireless signals;
        a first positioning reference value calculator configured to calculate a first positioning reference value; and
        a position determiner configured to determine a position based on the first positioning reference value.

### 2. 독립항들 간 공통 구성 추출

청구항 1과 청구항 6은 다음과 같은 공통 또는 대응되는 구성요소를 포함합니다.

*   **공통 구성 1:** 복수의 무선 신호를 수집하는 구성 (collecting a plurality of wireless signals / a wireless signal collector configured to collect a plurality of wireless signals)
*   **공통 구성 2:** 제1 측위 기준값을 산출하는 구성 (calculating a first positioning reference value / a first positioning reference value calculator configured to calculate a first positioning reference value)
*   **공통 구성 3:** 상기 제1 측위 기준값을 기반으로 위치를 결정하는 구성 (determining a position based on the first positioning reference value / a position determiner configured to determine a position based on the first positioning reference value)

### 3. 공통 구성과 인용발명(D1) 대비

*   **공통 구성 1 (무선 신호 수집) 및 공통 구성 3 (위치 결정):**
    *   **D1 개시 여부:** D1에 개시되어 있습니다.
    *   **D1 관련 발췌:**
        *   D1 Claim 1: "receiving wireless signals from a plurality of access points"; "outputting a determined location."
        *   D1 Column 3, Lines 15-40: "The location calculation means (positioning module) of the present invention receives RSSI data... The output of the positioning module is a two-dimensional coordinate pair representing the estimated current location..."
        *   D1 Column 6, Lines 5-20: "The mobile terminal embodiment includes a wireless signal receiver module and a microprocessor running the location estimation algorithm."
    *   **차이점:** D1 대비 개선된 차이점은 없습니다.

*   **공통 구성 2 (제1 측위 기준값 산출):**
    *   **D1 개시 여부:** D1에 "location estimation value" 또는 "location reference value" 산출이 개시되어 있습니다.
    *   **D1 관련 발췌:**
        *   D1 Claim 1: "computing a location estimation value from the received signals"
        *   D1 Column 5, Lines 10-30: "The reference value calculation method of the present invention computes a location reference value as follows: first, RSSI values from at least three access points are collected simultaneously. Second, a distance estimate is computed from each RSSI value using a path loss model. Third, a weighted average of the distance estimates is computed..."
    *   **차이점 (잠재적 STF):** D1은 RSSI 값을 이용한 거리 추정치의 가중 평균을 개시하지만, 본 출원의 "제1 측위 기준값"은 명세서 [0002] 및 청구항 3에서 "RSSI, RTT, AoA의 가중 평균"으로 구체화되어 있습니다. D1은 RTT, AoA를 동시에 결합한 다중 신호 지표의 가중 평균을 개시하지 않습니다.

### 4. 공통 구성의 STF 해당 여부 판단

*   **STF 후보:** "RSSI, RTT, AoA를 동시에 결합한 가중 평균으로 산출되는 제1 측위 기준값" (A first positioning reference value calculated as a weighted average combining RSSI, RTT, and AoA simultaneously).
*   **D1 대비 개선점:** D1은 RSSI만을 이용한 거리 추정치의 가중 평균을 개시하며, RTT 및 AoA와 같은 다른 무선 신호 지표를 동시에 결합하는 다중 지표 융합을 개시하지 않습니다. 이는 측위 정확도를 향상시키는 개선된 기술적 특징입니다.
*   **명세서 뒷받침:**
    *   [0002]: "상기 제1 측위 기준값은 RSSI(수신신호강도), RTT(왕복 지연시간), AoA(도달각도) 중 적어도 하나를 포함하는 가중 평균값으로 정의된다." (본 발명의 "제1 측위 기준값"의 핵심적인 정의)
    *   [0005]: "본 발명에 따르면, 종래 기술 대비 실내 측위 오차를 50% 이상 줄일 수 있는 현저한 효과가 있다." (다중 지표 융합을 통한 정확도 향상에 기인함을 시사)
*   **STF 해당 여부:**
    *   청구항 1의 "제1 측위 기준값을 산출하는 단계"는 청구항 3에서 "RSSI, RTT, AoA의 가중 평균"으로 구체화될 수 있으며, 명세서 [0002]에 의해 본 발명의 "제1 측위 기준값"의 본질적인 정의로 볼 수 있습니다.
    *   청구항 6의 "제1 측위 기준값 산출부"는 이러한 개선된 산출 방법을 수행하도록 구성된 장치 구성요소로 해석될 수 있습니다.
    *   따라서, "RSSI, RTT, AoA를 동시에 결합한 가중 평균으로 산출되는 제1 측위 기준값"은 D1 대비 개선된 특별한 기술적 특징(STF)으로 인정될 수 있으며, 청구항 1과 청구항 6은 이 STF를 *대응되는* 기술적 특징으로 공유한다고 주장할 수 있습니다.
*   **결론:** STF에 해당하므로 단일성 주장 가능.

### 5. 단일성 인정 가능성 평가

*   **평가:** 보통
*   **이유:** D1이 RSSI 기반의 가중 평균을 개시하고 있으나, RTT 및 AoA를 동시에 결합한 가중 평균은 개시하지 않으므로, "RSSI, RTT, AoA를 동시에 결합한 가중 평균으로 산출되는 제1 측위 기준값"은 D1 대비 개선된 STF로 인정될 가능성이 있습니다. 청구항 1과 6은 각각 방법 및 장치로서 이 STF를 *대응되는* 형태로 포함하고 있다고 주장할 수 있으나, 독립항 자체에 명시적으로 기재되지 않은 점은 심사관의 추가적인 반박을 야기할 수 있습니다.